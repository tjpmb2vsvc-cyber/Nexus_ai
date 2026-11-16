
import json
import re
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

FEEDS = [
    ("NASA", "https://www.nasa.gov/feed/"),
    ("Smithsonian", "https://www.smithsonianmag.com/rss/latest_articles/")
]

KEYWORDS = {
    "mystery": 4,
    "mysterious": 4,
    "unexplained": 5,
    "ancient": 3,
    "discovery": 3,
    "hidden": 2,
    "ocean": 2,
    "space": 2,
    "archaeology": 4,
    "unknown": 3,
    "rare": 2,
    "lost": 2,
    "evidence": 2
}

def clean(text):
    text = re.sub(r"<[^>]+>", " ", text or "")
    return re.sub(r"\s+", " ", text).strip()

def parse_feed(xml, source):
    root = ET.fromstring(xml)
    results = []

    for item in root.iter():
        tag = item.tag.split("}")[-1].lower()

        if tag not in ("item", "entry"):
            continue

        title = ""
        summary = ""
        link = ""

        for child in item:
            name = child.tag.split("}")[-1].lower()

            if name == "title":
                title = child.text or ""

            elif name in ("description", "summary"):
                summary = child.text or ""

            elif name == "link":
                link = child.attrib.get("href", "")
                if not link:
                    link = child.text or ""

        if title and link.startswith("https://"):
            results.append({
                "title": clean(title),
                "summary": clean(summary)[:1000],
                "url": link,
                "source": source
            })

    return results

def main():
    stories = []

    for source, url in FEEDS:
        try:
            request = urllib.request.Request(
                url,
                headers={"User-Agent": "NEXUS-AI/0.2"}
            )

            with urllib.request.urlopen(request, timeout=15) as response:
                xml = response.read(2000000).decode("utf-8", "replace")

            stories.extend(parse_feed(xml, source))
            print("Fuente consultada:", source)

        except Exception as error:
            print("Fuente no disponible:", source, error)

    unique = {}

    for story in stories:
        text = (story["title"] + " " + story["summary"]).lower()

        story["score"] = sum(
            points for word, points in KEYWORDS.items()
            if word in text
        )

        unique[story["url"]] = story

    ranked = sorted(
        unique.values(),
        key=lambda x: x["score"],
        reverse=True
    )[:20]

    result = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "notice": "Research leads. Verify facts before publication.",
        "items": ranked
    }

    Path("discoveries.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    print("NEXUS AI research completed.")
    print("Stories discovered:", len(ranked))

    if "GITHUB_STEP_SUMMARY" in __import__("os").environ:
        with open(
            __import__("os").environ["GITHUB_STEP_SUMMARY"],
            "a",
            encoding="utf-8"
        ) as report:
            report.write("# NEXUS AI Research Radar\n\n")

            for story in ranked[:10]:
                report.write(
                    f"- [{story['title']}]({story['url']}) "
                    f"— Score: {story['score']}\n"
                )

if __name__ == "__main__":
    main()
