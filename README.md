# Kometa — Prueba Técnica: Desarrollador IA

Aplicación fullstack que administra cursos en Moodle usando un agente de IA para generar y publicar contenido (texto, PDF, imágenes y podcast) a partir de una instrucción en lenguaje natural.

**Flujo:** el usuario escribe una instrucción → la IA genera la estructura y el contenido del curso → se muestra una vista previa editable → al confirmar, se genera el material (PDF, imagen, audio) y se publica de verdad en Moodle → un chat permite hacer preguntas sobre el curso ya creado.

---

## 🧱 Stack utilizado

- **Backend:** Python + FastAPI
- **Frontend:** Jinja2 (templates) + JavaScript vanilla (sin framework, sin build step)
- **IA (texto):** Google Gemini (`gemini-flash-latest`) — nivel gratuito
- **IA (imágenes):** Pollinations.ai — gratuito, sin API key
- **Audio (podcast):** gTTS (Google Text-to-Speech) — gratuito
- **PDF:** reportlab
- **Moodle:** 5.0.1, corriendo en Docker (`bitnamilegacy/moodle`), vía API REST + un **plugin propio** (ver más abajo)

> Nota sobre el stack de IA: el reto sugería OpenAI. Se optó por un stack 100% gratuito (Gemini + Pollinations + gTTS) para no depender de una tarjeta de crédito, sin sacrificar ninguno de los 4 tipos de contenido pedidos.

---

## ⚙️ Requisitos previos

- Docker Desktop
- Python 3.12 (⚠️ no usar 3.14 al momento de escribir esto: varias librerías, como `pydantic-core`, todavía no publican builds precompilados para esa versión y falla la instalación)
- Una API key gratuita de Google AI Studio ([aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey))

---

## 🚀 Cómo levantar Moodle local

```bash
docker compose up -d
```

Esto levanta dos contenedores: `moodle-db` (MariaDB 11.4) y `moodle-app` (Moodle 5.0.1). La primera vez tarda varios minutos en completar la instalación interna de Moodle — puedes seguir el progreso con:

```bash
docker compose logs -f moodle
```

Cuando termine, entra a **http://localhost:8080** con usuario `admin` / contraseña `Admin123!` (definidos en `docker-compose.yml`).

### Habilitar Web Services / API REST y generar el token

1. **Site administration → Advanced features** → activar "Enable web services"
2. **Site administration → Server → Web Services → Manage protocols** → habilitar "REST protocol"
3. **Site administration → users → Permissions → Define roles** → creas tu rol llamado **"webserviceuser"** en shot name y en custom full name **"Web service user"** y activas el **"system"** en el apartado de **"Context types where this role may be assigned"**
4. **Site administration → Server → Web services → External services** → crear un servicio (ej. "Kometa API"), habilitarlo, luego le das en show less y marcar **"Can upload files"** y **"Can upload files"**
5. Dentro del servicio → **Functions** → agregar:
   - `core_course_create_categories`
   - `core_course_create_courses`
   - `core_course_get_categories`
   - `core_course_get_courses`
   - `core_files_upload`
   - `core_webservice_get_site_info`
   - `local_kometaws_create_section` (del plugin propio, ver abajo)
   - `local_kometaws_create_resource` (del plugin propio, ver abajo)
6. **Site administration → Server → Web services → Manage tokens** → crear un token para el usuario admin y ese servicio que es KOmeta API
7. **Site administration → users → Permissions → Assign system roles** → asignas el usuario admin el rol de **"Web service user"**

### Instalar el plugin personalizado `local_kometaws`

La API estándar de Moodle **no expone una función para agregar recursos (archivos) dentro de las secciones de un curso** — solo permite crear el curso en sí. Para resolver esto de forma correcta (en vez de un workaround frágil), se construyó un pequeño plugin de Moodle que expone dos funciones nuevas al servicio web:

- `local_kometaws_create_section`: crea/actualiza una sección del curso (nombre + resumen)
- `local_kometaws_create_resource`: sube un archivo (ya cargado a un área de borrador) y lo publica como recurso dentro de una sección

El código del plugin está en `moodle-plugin/kometaws/`. Para instalarlo:

```bash
docker cp moodle-plugin/kometaws moodle-app:/bitnami/moodle/local/kometaws
docker exec -u root moodle-app chown -R daemon:daemon /bitnami/moodle/local/kometaws
docker restart moodle-app
```

Luego ve a `http://localhost:8080/admin/index.php` para que Moodle detecte e instale el plugin nuevo, y agrega sus dos funciones al servicio "Kometa API" (paso 4 de arriba).

---

## 🔑 Configuración del backend

Dentro de `Bakend/`, copia `.env.example` a `.env` y completa:

```
MOODLE_URL=http://localhost:8080
MOODLE_TOKEN=tu_token_de_moodle
GEMINI_API_KEY=tu_api_key_de_gemini
```

---

## ▶️ Cómo correr la aplicación

```bash
cd Bakend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Abre **http://localhost:8000**.

---

## 🧩 Decisiones técnicas

- **Stack de IA 100% gratuito** (Gemini, Pollinations, gTTS) en vez de OpenAI, para evitar depender de una tarjeta de crédito, manteniendo los 4 tipos de contenido pedidos (texto, PDF, imagen, podcast).
- **Plugin personalizado de Moodle** para resolver la limitación real de la API estándar respecto a la creación de recursos dentro de secciones. Se evaluaron alternativas (plugins comunitarios existentes, o "simplificar" usando solo etiquetas de texto con links) y se optó por construir el plugin propio por ser la solución más correcta y controlable, aunque tomó más tiempo.
- **El preview genera el contenido de texto real** (no solo la estructura) antes de publicar, para que el usuario pueda revisar/editar el contenido real, no solo títulos. Los archivos binarios (imagen, PDF, audio) se generan recién al confirmar, para no gastar generación de IA en contenido que el usuario podría descartar.
- **Estado en memoria** (sin base de datos) para el curso actual, ya que el alcance del reto es "un curso a la vez, sin autenticación".
- **Frontend con Jinja2 + JS vanilla** (sin React/Vue) para priorizar velocidad de desarrollo dado el plazo de 4 días, ya que el reto no exige un framework específico.
- El chat de dudas usa como contexto el **contenido de texto real generado** para cada módulo (no una respuesta genérica), concatenado y enviado como contexto a Gemini junto con la pregunta.

## ✅ Funcionalidades implementadas

- [x] Generación de estructura del curso con IA
- [x] Vista previa antes de publicar (editable)
- [x] Generación de texto por módulo
- [x] Generación de PDF
- [x] Generación de imagen
- [x] Generación de podcast (guion + audio)
- [x] Publicación real en Moodle (curso, secciones, recursos)
- [x] Chat de dudas sobre el curso

## ✨ Extras implementados

- [x] Edición de contenido (texto de módulos) antes de confirmar la publicación

## ❌ Qué no alcancé a hacer

- Video interactivo con puntos de interacción (extra opcional)
- Manejo de reintentos automáticos ante fallos de la API de IA o de Moodle (actualmente, si un módulo falla a mitad de la publicación, hay que reintentar el proceso completo)
- Validación exhaustiva de errores de red intermitentes

## 🎥 Videos

- Video 1 — Decisiones técnicas: _(link)_
- Video 2 — Demo de uso: _(link)_
