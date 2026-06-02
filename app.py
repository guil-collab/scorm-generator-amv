import os, json, re
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import anthropic

app = Flask(__name__, static_folder="static", static_url_path="")
CORS(app)

# ── Content DB ────────────────────────────────────────────────
CONTENT_PATH = os.path.join(os.path.dirname(__file__), "content", "index.json")
with open(CONTENT_PATH, encoding="utf-8") as f:
    CONTENT_DB = json.load(f)

UNITS_BY_ID = {u["id"]: u for u in CONTENT_DB["units"]}

# ── Anthropic client ──────────────────────────────────────────
def get_client():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable not set")
    return anthropic.Anthropic(api_key=api_key)

# ── Routes ────────────────────────────────────────────────────
@app.route("/")
def index():
    return send_from_directory("static", "index.html")

@app.route("/api/health")
def health():
    has_key = bool(os.environ.get("ANTHROPIC_API_KEY"))
    return jsonify({"status": "ok", "api_key_set": has_key})

@app.route("/api/units")
def get_units():
    units = []
    for u in CONTENT_DB["units"]:
        units.append({
            "id":       u["id"],
            "title":    u["title"],
            "short":    u["short"],
            "color":    u["color"],
            "topics":   u["topics"],
            "hashtags": u.get("hashtags", []),
        })
    return jsonify(units)

@app.route("/api/generate", methods=["POST"])
def generate():
    data = request.get_json()
    unit_ids         = data.get("units", [])
    num_questions    = int(data.get("num_questions", 10))
    difficulty       = data.get("difficulty", "Intermedio")
    language         = data.get("language", "Castellano")
    context          = data.get("context", "").strip()
    selected_tags    = data.get("selected_tags", [])   # hashtags chosen by teacher

    if not unit_ids:
        return jsonify({"error": "Selecciona al menos una unidad"}), 400

    # Build context from selected units
    content_blocks = []
    unit_titles = []
    for uid in unit_ids:
        u = UNITS_BY_ID.get(uid)
        if not u:
            continue
        unit_titles.append(u["title"])
        block = f"=== {u['title']} ===\n"
        if u.get("theory"):
            block += f"TEORÍA:\n{u['theory'][:3000]}\n\n"
        if u.get("exams"):
            block += f"PREGUNTAS DE EXÁMENES ANTERIORES (usa como referencia de estilo y nivel):\n{u['exams'][:2000]}\n\n"
        if u.get("practices"):
            block += f"PRÁCTICAS RELACIONADAS: {u['practices']}\n"
        content_blocks.append(block)

    content_text = "\n\n".join(content_blocks)
    lang_instruction = "en castellano (español)" if language == "Castellano" else "en galego (gallés)"

    difficulty_map = {
        "Básico":     "preguntas sencillas de recordatorio y reconocimiento, conceptos básicos",
        "Intermedio": "preguntas de comprensión y aplicación, mezcla de conceptos",
        "Avanzado":   "preguntas de análisis, evaluación y casos prácticos, nivel de examen final"
    }
    diff_desc = difficulty_map.get(difficulty, difficulty_map["Intermedio"])

    # Build hashtag focus block
    if selected_tags:
        tags_str = ", ".join(f"#{t}" for t in selected_tags)
        tags_block = f"\nCONCEPTOS ESPECÍFICOS A EVALUAR (el profesor ha seleccionado estos hashtags — centra las preguntas PRINCIPALMENTE en estos conceptos):\n{tags_str}\n"
    else:
        tags_block = ""

    extra = f"\nINSTRUCCIONES ADICIONALES DEL PROFESOR:\n{context}" if context else ""

    prompt = f"""Eres un experto en creación de tests educativos para la asignatura "Animación Musical en Vivo" (Ciclo Medio de Vídeo DJ, FP).

CONTENIDO DE REFERENCIA:
{content_text}
{tags_block}
{extra}

INSTRUCCIONES:
- Genera exactamente {num_questions} preguntas de opción múltiple {lang_instruction}
- Nivel de dificultad: {difficulty} — {diff_desc}
{"- IMPORTANTE: enfoca las preguntas en los conceptos con hashtag indicados arriba" if selected_tags else ""}
- Cada pregunta debe tener exactamente 4 opciones (a, b, c, d)
- Solo una opción es correcta
- Incluye una explicación breve (1-2 frases) de por qué la respuesta es correcta
- Las preguntas deben basarse en el contenido real del curso
- Evita preguntas ambiguas o con trampa innecesaria

RESPONDE ÚNICAMENTE con un JSON válido en este formato exacto (sin markdown, sin texto adicional):
{{
  "title": "Título descriptivo del test",
  "units": "{', '.join(unit_titles)}",
  "difficulty": "{difficulty}",
  "language": "{language}",
  "questions": [
    {{
      "id": 1,
      "text": "Texto de la pregunta",
      "options": ["Opción A", "Opción B", "Opción C", "Opción D"],
      "correct": 0,
      "explanation": "Explicación de la respuesta correcta"
    }}
  ]
}}

El campo "correct" es el índice (0-3) de la opción correcta."""

    try:
        client = get_client()
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}]
        )
        raw = message.content[0].text.strip()
        # Strip markdown code fences if present
        raw = re.sub(r'^```(?:json)?\s*', '', raw)
        raw = re.sub(r'\s*```$', '', raw)
        result = json.loads(raw)
        return jsonify(result)
    except json.JSONDecodeError as e:
        return jsonify({"error": f"Error al parsear respuesta de IA: {str(e)}", "raw": raw[:500]}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/refine", methods=["POST"])
def refine():
    data = request.get_json()
    questions    = data.get("questions", [])
    instruction  = data.get("instruction", "").strip()
    language     = data.get("language", "Castellano")
    title        = data.get("title", "Test AMV")
    difficulty   = data.get("difficulty", "Intermedio")
    units        = data.get("units", "")

    if not instruction:
        return jsonify({"error": "Escribe una instrucción de modificación"}), 400

    lang_instruction = "en castellano (español)" if language == "Castellano" else "en galego"

    prompt = f"""Eres un experto en tests educativos. Tienes este test de la asignatura "Animación Musical en Vivo":

{json.dumps({"title": title, "questions": questions}, ensure_ascii=False, indent=2)}

INSTRUCCIÓN DE MODIFICACIÓN DEL PROFESOR:
{instruction}

Aplica la instrucción al test. Puedes: cambiar preguntas, añadir preguntas, eliminar preguntas, cambiar dificultad, reformular, añadir contexto, cambiar idioma, etc.
El resultado debe estar {lang_instruction}.

RESPONDE ÚNICAMENTE con el JSON completo del test modificado (sin markdown, sin texto adicional):
{{
  "title": "...",
  "units": "{units}",
  "difficulty": "{difficulty}",
  "language": "{language}",
  "questions": [...]
}}"""

    try:
        client = get_client()
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}]
        )
        raw = message.content[0].text.strip()
        raw = re.sub(r'^```(?:json)?\s*', '', raw)
        raw = re.sub(r'\s*```$', '', raw)
        result = json.loads(raw)
        return jsonify(result)
    except json.JSONDecodeError as e:
        return jsonify({"error": f"Error al parsear respuesta: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
