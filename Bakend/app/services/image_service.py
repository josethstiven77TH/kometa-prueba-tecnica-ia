import requests
import urllib.parse
from app.utils.retry import con_reintentos


@con_reintentos(intentos=3, espera_inicial=4.0)
def generar_imagen(prompt_ingles: str, ruta_salida: str) -> str:
    """
    Genera una imagen a partir de un prompt en inglés usando Pollinations.ai
    (servicio gratuito, no requiere API key) y la guarda en disco.

    Retorna la ruta del archivo guardado.
    """
    prompt_codificado = urllib.parse.quote(prompt_ingles)
    url = f"https://image.pollinations.ai/prompt/{prompt_codificado}?width=1024&height=768&nologo=true"

    response = requests.get(url, timeout=60)
    response.raise_for_status()

    with open(ruta_salida, "wb") as f:
        f.write(response.content)

    return ruta_salida