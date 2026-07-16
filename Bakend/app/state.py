"""
Almacenamiento simple en memoria del último curso generado/publicado.
No se requiere base de datos ni autenticación (según el alcance del reto:
un curso a la vez, sin usuarios).
"""

estado_curso_actual = {
    "datos": None,
    "id_curso_moodle": None,
}


def guardar_curso(datos: dict, id_curso_moodle: int = None):
    estado_curso_actual["datos"] = datos
    if id_curso_moodle is not None:
        estado_curso_actual["id_curso_moodle"] = id_curso_moodle


def obtener_curso_actual() -> dict:
    return estado_curso_actual