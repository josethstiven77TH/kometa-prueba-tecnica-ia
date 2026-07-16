"""
Utilidad simple de reintentos con backoff exponencial, sin dependencias externas.
Se usa para llamadas a APIs externas (Gemini, Moodle) que pueden fallar
temporalmente por límites de cuota, timeouts o problemas de red.
"""
import time
import functools


def con_reintentos(intentos: int = 3, espera_inicial: float = 2.0, factor: float = 2.0):
    """
    Decorador que reintenta una función si lanza una excepción,
    esperando cada vez más tiempo entre intentos (backoff exponencial).
    """
    def decorador(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            espera = espera_inicial
            ultimo_error = None

            for intento in range(1, intentos + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    ultimo_error = e
                    if intento < intentos:
                        print(f"Intento {intento}/{intentos} falló para {func.__name__}: {e}. "
                              f"Reintentando en {espera:.0f}s...")
                        time.sleep(espera)
                        espera *= factor
                    else:
                        print(f"Falló definitivamente {func.__name__} tras {intentos} intentos.")

            raise ultimo_error

        return wrapper
    return decorador