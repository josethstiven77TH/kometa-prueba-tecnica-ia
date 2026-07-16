from gtts import gTTS


def generar_podcast(guion: str, ruta_salida: str) -> str:
    """
    Convierte un guion de texto a audio (mp3) usando Google Text-to-Speech,
    y lo guarda en disco.

    Retorna la ruta del archivo guardado.
    """
    tts = gTTS(text=guion, lang="es", slow=False)
    tts.save(ruta_salida)
    return ruta_salida