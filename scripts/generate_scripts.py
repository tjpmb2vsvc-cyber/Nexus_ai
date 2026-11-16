
import json
import re
from pathlib import Path
from datetime import datetime, timezone

INPUT = Path("discoveries.json")
OUTPUT = Path("generated_scripts.json")

def clean(text):
    return re.sub(r"\s+", " ", text or "").strip()

def make_script(story):
    title = clean(story.get("title", "Unknown mystery"))
    summary = clean(story.get("summary", ""))
    url = story.get("url", "")
    topic = title.rstrip(" .!?")

    es = {
        "language": "es",
        "title": f"El misterio de {topic}",
        "hook": f"¿Sabías que existe una historia fascinante sobre {topic}?",
        "narration": (
            f"Hoy descubrimos {topic}. "
            f"Esto es lo que cuenta la fuente original: {summary}. "
            "Pero antes de sacar conclusiones, "
            "hay que investigar las pruebas. "
            "¿Qué explicación te parece más interesante?"
        ),
        "duration_target_seconds": 45,
        "description": f"Descubre esta historia: {topic}.",
        "hashtags": ["#Curiosidades", "#Misterios", "#Historia"],
        "sources": [url]
    }

    en = {
        "language": "en",
        "title": f"The mystery of {topic}",
        "hook": f"Have you heard this fascinating story about {topic}?",
        "narration": (
            f"Today we explore {topic}. "
            f"Here is what the original source says: {summary}. "
            "Before reaching any conclusion, "
            "we need to examine the evidence. "
            "What explanation do you find most interesting?"
        ),
        "duration_target_seconds": 45,
        "description": f"Discover this story: {topic}.",
        "hashtags": ["#Curiosities", "#Mysteries", "#History"],
        "sources": [url]
    }

    return {
        "id": re.sub(r"[^a-z0-9]+", "-", topic.lower()).strip("-")[:60],
        "status": "draft",
        "approved": False,
        "es": es,
        "en": en,
        "fact_check_required": True,
        "visuals": "Use original or licensed footage",
        "music": "Use original or licensed music"
    }

def main():
    if not INPUT.exists():
        raise SystemExit("ERROR: discoveries.json not found")

    data = json.loads(INPUT.read_text(encoding="utf-8"))
    stories = data.get("items", [])

    drafts = []

    for story in stories:
        if story.get("url", "").startswith("https://"):
            drafts.append(make_script(story))

    result = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_drafts": len(drafts),
        "notice": "Drafts only. Verify facts and translations before publication.",
        "items": drafts
    }

    OUTPUT.write_text(
        json.dumps(result, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    print("NEXUS AI script generation completed.")
    print("Drafts generated:", len(drafts))

if __name__ == "__main__":
    main()
