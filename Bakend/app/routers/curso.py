import os
import shutil
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.ai_service import generar_estructura_curso, generar_contenido_modulo
from app.services.image_service import generar_imagen
from app.services.audio_service import generar_podcast
from app.services.pdf_service import generar_pdf
from app.services.moodle_service import crear_categoria, crear_curso, crear_seccion, crear_recurso
from app.state import guardar_curso, obtener_curso_actual

router = APIRouter(prefix="/api/curso", tags=["curso"])

CARPETA_TEMPORAL = "archivos_generados"


class InstruccionRequest(BaseModel):
    instruccion: str


class PublicarRequest(BaseModel):
    curso: dict  # la estructura completa (posiblemente editada por el usuario)


@router.post("/generar")
def generar(request: InstruccionRequest):
    """
    Recibe una instrucción en lenguaje natural, genera la estructura del curso
    y el contenido de texto de cada módulo. Esto es lo que se muestra en el
    preview, ANTES de publicar nada en Moodle.
    """
    try:
        estructura = generar_estructura_curso(request.instruccion)

        modulos_con_contenido = []
        for modulo in estructura["modulos"]:
            contenido = generar_contenido_modulo(
                titulo_curso=estructura["nombre_curso"],
                titulo_modulo=modulo["titulo"],
                descripcion_modulo=modulo["descripcion"],
            )
            modulos_con_contenido.append({
                "titulo": modulo["titulo"],
                "descripcion": modulo["descripcion"],
                "contenido_texto": contenido["contenido_texto"],
                "guion_podcast": contenido["guion_podcast"],
                "prompt_imagen": contenido["prompt_imagen"],
            })

        resultado = {
            "nombre_curso": estructura["nombre_curso"],
            "descripcion_corta": estructura["descripcion_corta"],
            "modulos": modulos_con_contenido,
        }

        guardar_curso(resultado)

        return resultado

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando el curso: {str(e)}")


@router.post("/publicar")
def publicar(request: PublicarRequest):
    """
    Recibe la estructura del curso (posiblemente editada por el usuario en el
    preview) y la publica de verdad en Moodle: genera imagen/audio/PDF por
    módulo, crea el curso, sus secciones, y sube los recursos.
    """
    curso = request.curso
    carpeta_curso = os.path.join(CARPETA_TEMPORAL, "curso_actual")
    os.makedirs(carpeta_curso, exist_ok=True)

    try:
        id_categoria = crear_categoria("Cursos generados por IA")
        id_curso = crear_curso(
            nombre_curso=curso["nombre_curso"],
            descripcion_corta=curso["descripcion_corta"],
            id_categoria=id_categoria,
        )

        for idx, modulo in enumerate(curso["modulos"], start=1):
            crear_seccion(
                id_curso=id_curso,
                numero_seccion=idx,
                nombre=modulo["titulo"],
                resumen=modulo["descripcion"],
            )

            ruta_pdf = os.path.join(carpeta_curso, f"modulo_{idx}.pdf")
            generar_pdf(modulo["titulo"], modulo["contenido_texto"], ruta_pdf)
            crear_recurso(
                id_curso=id_curso, numero_seccion=idx,
                nombre=f"{modulo['titulo']} (PDF)",
                ruta_archivo=ruta_pdf,
                descripcion="Material del módulo en PDF",
            )

            ruta_imagen = os.path.join(carpeta_curso, f"modulo_{idx}.png")
            generar_imagen(modulo["prompt_imagen"], ruta_imagen)
            crear_recurso(
                id_curso=id_curso, numero_seccion=idx,
                nombre=f"{modulo['titulo']} (Imagen)",
                ruta_archivo=ruta_imagen,
                descripcion="Imagen ilustrativa del módulo",
            )

            ruta_audio = os.path.join(carpeta_curso, f"modulo_{idx}.mp3")
            generar_podcast(modulo["guion_podcast"], ruta_audio)
            crear_recurso(
                id_curso=id_curso, numero_seccion=idx,
                nombre=f"{modulo['titulo']} (Podcast)",
                ruta_archivo=ruta_audio,
                descripcion="Podcast del módulo",
            )

        guardar_curso(curso, id_curso_moodle=id_curso)

        return {
            "mensaje": "Curso publicado correctamente",
            "id_curso": id_curso,
            "url_curso": f"http://localhost:8080/course/view.php?id={id_curso}",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error publicando el curso: {str(e)}")

    finally:
        if os.path.exists(carpeta_curso):
            shutil.rmtree(carpeta_curso)