from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.ai_service import responder_chat_curso
from app.state import obtener_curso_actual

router = APIRouter(prefix="/api/chat", tags=["chat"])


class PreguntaRequest(BaseModel):
    pregunta: str


def _construir_contexto_texto(curso: dict) -> str:
    partes = [f"Curso: {curso['nombre_curso']}", f"Descripción: {curso['descripcion_corta']}", ""]
    for modulo in curso["modulos"]:
        partes.append(f"--- {modulo['titulo']} ---")
        partes.append(modulo["contenido_texto"])
        partes.append("")
    return "\n".join(partes)


@router.post("")
def preguntar(request: PreguntaRequest):
    estado = obtener_curso_actual()
    curso = estado.get("datos")

    if not curso:
        raise HTTPException(
            status_code=400,
            detail="Todavía no hay ningún curso generado. Primero genera y publica un curso.",
        )

    contexto = _construir_contexto_texto(curso)
    respuesta = responder_chat_curso(request.pregunta, contexto)

    return {"respuesta": respuesta}