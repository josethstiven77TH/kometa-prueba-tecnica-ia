import requests
from app.config import MOODLE_URL, MOODLE_TOKEN
from app.utils.retry import con_reintentos

ENDPOINT = f"{MOODLE_URL}/webservice/rest/server.php"


@con_reintentos(intentos=3, espera_inicial=3.0)
def _llamar_moodle(wsfunction: str, params: dict) -> dict:
    """
    Función auxiliar interna: hace la llamada real a la API REST de Moodle.
    """
    payload = {
        "wstoken": MOODLE_TOKEN,
        "wsfunction": wsfunction,
        "moodlewsrestformat": "json",
        **params,
    }
    response = requests.post(ENDPOINT, data=payload, timeout=30)
    response.raise_for_status()
    data = response.json()

    if isinstance(data, dict) and "exception" in data:
        raise Exception(f"Error de Moodle ({wsfunction}): {data.get('message')}")

    return data


def crear_categoria(nombre: str) -> int:
    """
    Crea una categoría de curso en Moodle. Retorna el id de la categoría creada.
    """
    params = {
        "categories[0][name]": nombre,
        "categories[0][parent]": 0,
    }
    resultado = _llamar_moodle("core_course_create_categories", params)
    return resultado[0]["id"]


def crear_curso(nombre_curso: str, descripcion_corta: str, id_categoria: int) -> int:
    """
    Crea un curso en Moodle. Retorna el id del curso creado.
    """
    import time
    shortname = f"{nombre_curso[:40]}-{int(time.time())}"

    params = {
        "courses[0][fullname]": nombre_curso,
        "courses[0][shortname]": shortname,
        "courses[0][categoryid]": id_categoria,
        "courses[0][summary]": descripcion_corta,
        "courses[0][format]": "topics",
        "courses[0][numsections]": 0,
    }
    resultado = _llamar_moodle("core_course_create_courses", params)
    return resultado[0]["id"]


def obtener_info_sitio() -> dict:
    """
    Llama a core_webservice_get_site_info, útil para probar la conexión.
    """
    return _llamar_moodle("core_webservice_get_site_info", {})


def crear_seccion(id_curso: int, numero_seccion: int, nombre: str, resumen: str = "") -> int:
    """
    Crea o actualiza una sección del curso con nombre y resumen.
    Usa la función custom del plugin local_kometaws.
    """
    params = {
        "courseid": id_curso,
        "sectionnum": numero_seccion,
        "name": nombre,
        "summary": resumen,
    }
    resultado = _llamar_moodle("local_kometaws_create_section", params)
    return resultado["sectionid"]


@con_reintentos(intentos=3, espera_inicial=3.0)
def subir_archivo_borrador(ruta_archivo: str) -> int:
    """
    Sube un archivo al área de "borradores" (draft area) del usuario.
    Retorna el itemid del borrador, necesario para luego crear el recurso.
    """
    import os

    with open(ruta_archivo, "rb") as f:
        files = {"file_1": (os.path.basename(ruta_archivo), f)}
        data = {
            "token": MOODLE_TOKEN,
            "moodlewsrestformat": "json",
        }
        upload_url = f"{MOODLE_URL}/webservice/upload.php"
        response = requests.post(upload_url, data=data, files=files, timeout=60)

    response.raise_for_status()
    resultado = response.json()

    if isinstance(resultado, dict) and "error" in resultado:
        raise Exception(f"Error subiendo archivo: {resultado.get('error')}")

    return resultado[0]["itemid"]


def crear_recurso(id_curso: int, numero_seccion: int, nombre: str, ruta_archivo: str, descripcion: str = "") -> int:
    """
    Sube un archivo y lo crea como recurso dentro de una sección del curso.
    Usa la función custom del plugin local_kometaws.
    """
    draft_itemid = subir_archivo_borrador(ruta_archivo)

    params = {
        "courseid": id_curso,
        "sectionnum": numero_seccion,
        "name": nombre,
        "intro": descripcion,
        "draftitemid": draft_itemid,
    }
    resultado = _llamar_moodle("local_kometaws_create_resource", params)
    return resultado["cmid"]