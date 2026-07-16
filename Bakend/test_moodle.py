"""
Script de prueba: crea una categoría y un curso REAL en tu Moodle local,
usando la API REST, para confirmar que la integración funciona.

Ejecutar con: python test_moodle.py
"""
from app.services.moodle_service import crear_categoria, crear_curso, obtener_info_sitio

if __name__ == "__main__":
    print("1️ Probando conexión con Moodle...")
    info = obtener_info_sitio()
    print(f"Conectado a: {info['sitename']}\n")

    print("2️ Creando categoría de prueba...")
    id_categoria = crear_categoria("Cursos generados por IA")
    print(f" Categoría creada con id: {id_categoria}\n")

    print("3️ Creando curso de prueba...")
    id_curso = crear_curso(
        nombre_curso="Excel Intermedio: Prueba de integración",
        descripcion_corta="Curso de prueba generado automáticamente para validar la API",
        id_categoria=id_categoria,
    )
    print(f"Curso creado con id: {id_curso}\n")

    print("🎉 ¡Listo! Ve a tu Moodle (http://localhost:8080) y busca el curso.")