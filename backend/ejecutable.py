"""Punto de entrada de la distribucion como ejecutable.

Levanta el servicio y abre el navegador. Existe para que quien solo quiera usar el
sistema no tenga que instalar Python, Node ni un servidor de base de datos: el interprete,
las dependencias, el corpus y la interfaz ya compilada viajan dentro del propio archivo, y
la persistencia se resuelve con SQLite en un archivo junto al ejecutable.

Lo unico que sigue haciendo falta aparte es Ollama con el modelo generador, porque son
3,4 GB de pesos y un servicio del sistema: empaquetarlo aqui dentro no seria razonable.

El proyecto entregado no usa esta via. Su modo por defecto es PostgreSQL con la interfaz
servida por su propio proceso de desarrollo, que es lo que la guia de instalacion describe.
"""

import socket
import sys
import threading
import time
import webbrowser

import httpx
import uvicorn

PUERTO = 8000


def puerto_libre(puerto: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", puerto)) != 0


def elegir_puerto() -> int:
    for puerto in range(PUERTO, PUERTO + 20):
        if puerto_libre(puerto):
            return puerto
    return PUERTO


def comprobar_ollama(url: str) -> str | None:
    """Devuelve el aviso que corresponda, o None si el generador esta disponible."""
    try:
        respuesta = httpx.get(f"{url}/api/tags", timeout=4.0)
        respuesta.raise_for_status()
    except httpx.HTTPError:
        return (
            "AVISO: no se encuentra Ollama en " + url + ".\n"
            "  El sistema arrancara igual, pero no podra redactar respuestas.\n"
            "  Instalalo con:  winget install Ollama.Ollama\n"
            "  y descarga el modelo con:  ollama pull qwen3.5:4b"
        )
    modelos = [m.get("name", "") for m in respuesta.json().get("models", [])]
    if not any(m.startswith("qwen3.5:4b") for m in modelos):
        return (
            "AVISO: Ollama esta activo pero falta el modelo generador.\n"
            "  Descargalo con:  ollama pull qwen3.5:4b"
        )
    return None


def abrir_navegador(puerto: int) -> None:
    for _ in range(60):
        if not puerto_libre(puerto):
            webbrowser.open(f"http://127.0.0.1:{puerto}")
            return
        time.sleep(0.5)


def main() -> int:
    from infrastructure.config import configuracion

    puerto = elegir_puerto()

    print("=" * 62)
    print("  Asistente de consulta del quechua wanka")
    print("=" * 62)
    aviso = comprobar_ollama(configuracion.ollama_url)
    if aviso:
        print(aviso)
        print("-" * 62)
    print(f"  Abriendo http://127.0.0.1:{puerto}")
    print("  El modelo tarda cerca de un minuto en quedar listo.")
    print("  Para cerrar, cierra esta ventana.")
    print("=" * 62)

    threading.Thread(target=abrir_navegador, args=(puerto,), daemon=True).start()

    from main import app

    uvicorn.run(app, host="127.0.0.1", port=puerto, log_level="warning")
    return 0


if __name__ == "__main__":
    sys.exit(main())
