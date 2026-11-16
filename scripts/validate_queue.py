
import json
import sys
from pathlib import Path

def main():
    file = Path("content/queue.json")

    if not file.exists():
        print("ERROR: No existe la cola de contenidos")
        sys.exit(1)

    try:
        data = json.loads(file.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        print("ERROR: El archivo JSON no es válido")
        sys.exit(1)

    items = data.get("items", [])

    if not isinstance(items, list):
        print("ERROR: La lista de contenidos no es válida")
        sys.exit(1)

    for item in items:
        for language in ["es", "en"]:
            content = item.get(language, {})

            if not content.get("title"):
                print("ERROR: Falta un título")
                sys.exit(1)

            if not content.get("script"):
                print("ERROR: Falta un guion")
                sys.exit(1)

            if not content.get("sources"):
                print("ERROR: Faltan fuentes")
                sys.exit(1)

    print("NEXUS AI: Validación completada")
    print(f"Historias revisadas: {len(items)}")

if __name__ == "__main__":
    main()
