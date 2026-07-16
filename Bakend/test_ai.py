"""
Script de prueba rápida: verifica que la conexión con Gemini funciona
antes de seguir construyendo el resto de la app.
 
Ejecutar con: python test_ai.py
"""
from app.services.ai_service import generar_estructura_curso
 
if __name__ == "__main__":
    resultado = generar_estructura_curso("crea un curso de Excel intermedio con 4 modulos")
    print("\n✅ Resultado generado por Gemini:\n")
    print(resultado)