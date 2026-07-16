import json
import google.generativeai as genai
from app.config import GEMINI_API_KEY
from app.utils.retry import con_reintentos
 
genai.configure(api_key=GEMINI_API_KEY)
 
# Usamos el modelo flash: rápido y con buen nivel gratuito
model = genai.GenerativeModel("gemini-flash-latest")

 
@con_reintentos(intentos=3, espera_inicial=8.0)
def generar_estructura_curso(instruccion: str) -> dict:
    """
    A partir de una instrucción en lenguaje natural, genera la estructura
    del curso: nombre, y lista de módulos con su descripción.
    """
    prompt = f"""
Eres un diseñador instruccional experto. A partir de la siguiente instrucción,
genera la estructura de un curso.
 
Instrucción: "{instruccion}"
 
Responde ÚNICAMENTE con un JSON válido (sin texto adicional, sin markdown,
sin ```), con esta forma exacta:
 
{{
  "nombre_curso": "string",
  "descripcion_corta": "string",
  "modulos": [
    {{
      "titulo": "string",
      "descripcion": "string breve de qué trata este módulo"
    }}
  ]
}}
"""
    response = model.generate_content(prompt)
    texto = response.text.strip()
 
    # Por si el modelo agrega bloques de markdown ```json ... ```
    texto = texto.replace("```json", "").replace("```", "").strip()
 
    return json.loads(texto)
 
 
@con_reintentos(intentos=3, espera_inicial=8.0)
def generar_contenido_modulo(titulo_curso: str, titulo_modulo: str, descripcion_modulo: str) -> dict:
    """
    Genera el contenido de texto explicativo para un módulo específico,
    y también un guion corto para convertir a podcast/audio.
    """
    prompt = f"""
Eres un experto creando contenido educativo. Estás desarrollando el módulo
"{titulo_modulo}" del curso "{titulo_curso}".
 
Descripción del módulo: {descripcion_modulo}
 
Responde ÚNICAMENTE con un JSON válido (sin texto adicional, sin markdown),
con esta forma exacta:
 
{{
  "contenido_texto": "Contenido explicativo completo del módulo, en varios párrafos, en español, listo para publicar (mínimo 200 palabras)",
  "guion_podcast": "Guion corto en tono conversacional, como si un profesor lo explicara en voz alta, para convertir a audio (100-150 palabras)",
  "prompt_imagen": "Descripción corta en inglés para generar una imagen ilustrativa de este módulo (para un generador de imágenes tipo DALL-E)"
}}
"""
    response = model.generate_content(prompt)
    texto = response.text.strip()
    texto = texto.replace("```json", "").replace("```", "").strip()
 
    return json.loads(texto)
 

@con_reintentos(intentos=2, espera_inicial=5.0) 
def responder_chat_curso(pregunta: str, contenido_curso: str) -> str:
    """
    Responde una pregunta del usuario sobre el curso, usando SOLO
    el contenido real generado como contexto.
    """
    prompt = f"""
Eres un asistente que responde preguntas sobre un curso específico.
Usa ÚNICAMENTE la siguiente información del curso para responder.
Si la respuesta no está en el contenido, dilo honestamente.
 
Contenido del curso:
{contenido_curso}
 
Pregunta del usuario: {pregunta}
 
Responde de forma clara y concisa, en español.
"""
    response = model.generate_content(prompt)
    return response.text.strip()