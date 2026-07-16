"""
Script de prueba: agrega una sección y un recurso (el PDF que generamos antes)
al curso de prueba que ya existe en Moodle (id 2).

Ejecutar con: python test_moodle_recursos.py
"""
from app.services.moodle_service import crear_seccion, crear_recurso

ID_CURSO_PRUEBA = 2  # el que creamos con test_moodle.py

if __name__ == "__main__":
    print("1️ Creando sección 1...")
    id_seccion = crear_seccion(
        id_curso=ID_CURSO_PRUEBA,
        numero_seccion=1,
        nombre="Módulo 1: Funciones Lógicas y de Búsqueda Avanzada",
        resumen="Dominio de BUSCARV, BUSCARX, SI, Y, O",
    )
    print(f"Sección creada/actualizada, id: {id_seccion}\n")

    print("2️ Subiendo el PDF como recurso...")
    id_recurso = crear_recurso(
        id_curso=ID_CURSO_PRUEBA,
        numero_seccion=1,
        nombre="Material del Módulo 1 (PDF)",
        ruta_archivo="output_prueba/modulo1.pdf",
        descripcion="Contenido en PDF del módulo 1",
    )
    print(f"Recurso creado, cmid: {id_recurso}\n")

    print("🎉 ¡Listo! Ve al curso en Moodle y revisa la sección 1.")