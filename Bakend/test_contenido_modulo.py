"""
Script de prueba: genera el contenido completo de UN módulo
(texto, imagen, audio, PDF) para verificar que todo funciona
antes de conectar con Moodle.

Ejecutar con: python test_contenido_modulo.py
"""
import os
from app.services.ai_service import generar_contenido_modulo
from app.services.image_service import generar_imagen
from app.services.audio_service import generar_podcast
from app.services.pdf_service import generar_pdf

os.makedirs("output_prueba", exist_ok=True)

if __name__ == "__main__":
    print("1️  Generando contenido de texto con Gemini...")
    contenido = generar_contenido_modulo(
        titulo_curso="Excel Intermedio",
        titulo_modulo="Módulo 1: Funciones Lógicas y de Búsqueda Avanzada",
        descripcion_modulo="Dominio de BUSCARV, BUSCARX, SI, Y, O",
    )
    print("Texto generado:")
    print(contenido["contenido_texto"][:200], "...\n")

    print("2️ Generando imagen...")
    ruta_imagen = generar_imagen(
        contenido["prompt_imagen"],
        "output_prueba/imagen_modulo1.png"
    )
    print(f"Imagen guardada en: {ruta_imagen}\n")

    print("3️ Generando audio (podcast)...")
    ruta_audio = generar_podcast(
        contenido["guion_podcast"],
        "output_prueba/audio_modulo1.mp3"
    )
    print(f"Audio guardado en: {ruta_audio}\n")

    print("4️ Generando PDF...")
    ruta_pdf = generar_pdf(
        "Módulo 1: Funciones Lógicas y de Búsqueda Avanzada",
        contenido["contenido_texto"],
        "output_prueba/modulo1.pdf"
    )
    print(f"PDF guardado en: {ruta_pdf}\n")

    print("🎉 ¡Todo el contenido del módulo se generó correctamente!")