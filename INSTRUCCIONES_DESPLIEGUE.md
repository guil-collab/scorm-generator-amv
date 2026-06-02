# SCORM Generator — AMV
## Generador de tests SCORM con IA para Animación Musical en Vivo

---

## 🚀 Despliegue en Railway (recomendado, GRATIS)

Railway permite tener la app online en menos de 10 minutos.

### Paso 1 — Crear cuenta en GitHub (si no tienes)
→ https://github.com/signup

### Paso 2 — Subir el proyecto a GitHub

1. Abre **GitHub Desktop** o la web de GitHub
2. Crea un repositorio nuevo (privado recomendado): `scorm-generator-amv`
3. Sube toda la carpeta `scorm-generator/` al repositorio

O desde terminal:
```bash
cd "ruta/a/scorm-generator"
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/TU_USUARIO/scorm-generator-amv.git
git push -u origin main
```

### Paso 3 — Desplegar en Railway

1. Ve a → https://railway.app
2. Haz login con tu cuenta de GitHub
3. Pulsa **"New Project"** → **"Deploy from GitHub repo"**
4. Selecciona `scorm-generator-amv`
5. Railway detecta automáticamente que es Python/Flask

### Paso 4 — Añadir tu API Key de Anthropic

En Railway, en tu proyecto:
1. Ve a la pestaña **Variables**
2. Añade:
   - Nombre: `ANTHROPIC_API_KEY`
   - Valor: tu API key (empieza por `sk-ant-...`)
3. Guarda → Railway redespliega automáticamente

### Paso 5 — Acceder a tu app

Railway te da una URL pública del tipo:
`https://scorm-generator-amv-production.up.railway.app`

¡Esa es tu app! Guárdala en marcadores.

---

## 💻 Ejecución local (en tu Mac)

Si prefieres usarla solo en tu ordenador:

```bash
# 1. Instalar dependencias (solo la primera vez)
cd "ruta/a/scorm-generator"
pip3 install -r requirements.txt

# 2. Configurar API key
export ANTHROPIC_API_KEY=sk-ant-tuclaveaqui

# 3. Arrancar
python3 app.py
```

Luego abre el navegador en: **http://localhost:5000**

---

## 📁 Estructura del proyecto

```
scorm-generator/
├── app.py                    ← Backend Flask (API + servidor)
├── requirements.txt          ← Dependencias Python
├── Procfile                  ← Comando de arranque para Railway
├── railway.json              ← Config de Railway
├── .env.example              ← Plantilla de variables de entorno
├── content/
│   └── index.json            ← Base de datos de apuntes y exámenes
└── static/
    └── index.html            ← Frontend completo (SPA)
```

---

## 🔄 Actualizar el contenido (apuntes nuevos)

Si añades nuevos apuntes o exámenes, hay que regenerar `content/index.json`.
Avisa y se puede automatizar para que lo haga con un script.

---

## 🎛️ Cómo usar la app

1. **Selecciona las unidades** del panel izquierdo (UD1–UD5)
2. **Configura**: número de preguntas, dificultad, idioma
3. **Describe la sesión** en el cuadro de texto (opcional pero recomendado)
4. Pulsa **✨ Generar test SCORM**
5. **Previsualiza** el test generado
6. Si quieres cambios, escribe en el chat de refinamiento
7. Pulsa **⬇️ Descargar SCORM (.zip)** y sube el ZIP al aula virtual

---

## 💰 Coste estimado

- **Railway**: gratis hasta 500 horas/mes (más que suficiente)
- **Anthropic API**: ~0,003€ por test generado (10 preguntas ≈ 0,003€)
  - 100 tests al mes ≈ 0,30€
