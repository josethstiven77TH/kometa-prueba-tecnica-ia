from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch


def generar_pdf(titulo_modulo: str, contenido_texto: str, ruta_salida: str) -> str:
    """
    Genera un PDF simple con el título del módulo y su contenido de texto.

    Retorna la ruta del archivo guardado.
    """
    doc = SimpleDocTemplate(ruta_salida, pagesize=letter)
    estilos = getSampleStyleSheet()

    estilo_titulo = ParagraphStyle(
        "TituloModulo",
        parent=estilos["Heading1"],
        fontSize=18,
        spaceAfter=20,
    )
    estilo_cuerpo = ParagraphStyle(
        "CuerpoModulo",
        parent=estilos["Normal"],
        fontSize=11,
        leading=16,
        spaceAfter=12,
    )

    elementos = [
        Paragraph(titulo_modulo, estilo_titulo),
        Spacer(1, 0.2 * inch),
    ]

    for parrafo in contenido_texto.split("\n\n"):
        parrafo_limpio = parrafo.strip().replace("\n", " ")
        if parrafo_limpio:
            elementos.append(Paragraph(parrafo_limpio, estilo_cuerpo))

    doc.build(elementos)
    return ruta_salida