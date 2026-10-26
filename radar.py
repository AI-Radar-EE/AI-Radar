import os
import json
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

# AI RADAR SEADED

RSS_URL = "https://news.ycombinator.com/rss"

GEMINI_MODEL = "gemini-2.5-flash"

KEYWORDS = [
    "ai", "artificial intelligence", "llm",
    "gpt", "gemini", "claude", "grok",
    "agent", "machine learning", "openai",
    "anthropic", "automation", "robot"
]


def get_ai_news():
    print("Kogun värskeid AI-uudiseid...")

    request = urllib.request.Request(
        RSS_URL,
        headers={"User-Agent": "AI-Radar/1.0"}
    )

    with urllib.request.urlopen(request, timeout=20) as response:
        data = response.read()

    root = ET.fromstring(data)
    entries = root.findall("./channel/item")

    results = []

    for entry in entries:
        title = entry.findtext("title", "")
        link = entry.findtext("link", "")

        title_lower = title.lower()

        if any(keyword in title_lower for keyword in KEYWORDS):
            results.append({
                "title": title,
                "link": link
            })

    return results[:5]


def analyze_with_gemini(news):
    api_key = os.environ.get("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY puudub GitHubi keskkonnast."
        )

    news_text = "\n".join(
        f"{i}. {item['title']}\nAllikas: {item['link']}"
        for i, item in enumerate(news, 1)
    )

    prompt = f"""
Sa oled AI Radar, professionaalne AI-tehnoloogia
ja ärivõimaluste analüütik.

Analüüsi järgmisi AI-uudiste pealkirju.

UUDISED:
{news_text}

Koosta EESTI KEELES raport.

Raporti struktuur:

1. TÄHTSAMAD AI-UUDISED
Selgita lühidalt iga uudise võimalikku tähendust.

2. OLULISEMAD TRENDID
Milliseid AI arengusuundi need uudised näitavad?

3. ÄRIVÕIMALUSED
Paku 3 praktilist ideed, kuidas AI abil
raha teenida või kasulik teenus luua.

4. AI RADARI SOOVITUS
Millist ideed tasuks esimesena katsetada?
Selgita, miks.

5. JÄRGMISED SAMMUD
Anna 3 konkreetset tegevust.

OLULINE:
Sul on ainult uudiste pealkirjad ja lingid.
Ära väida, et oled artiklite sisu läbi lugenud.
Erista kinnitatud faktid ja oletused.
Vasta selgelt, konkreetselt ja eesti keeles.
"""

    url = (
        "https://generativelanguage.googleapis.com/"
        f"v1beta/models/{GEMINI_MODEL}:generateContent"
    )

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.4
        }
    }

    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": api_key
        },
        method="POST"
    )

    with urllib.request.urlopen(request, timeout=60) as response:
        result = json.loads(response.read().decode("utf-8"))

    candidates = result.get("candidates", [])

    if not candidates:
        raise RuntimeError(
            "Gemini ei tagastanud analüüsi."
        )

    parts = candidates[0].get("content", {}).get("parts", [])

    analysis = "\n".join(
        part.get("text", "")
        for part in parts
        if "text" in part
    )

    if not analysis.strip():
        raise RuntimeError(
            "Gemini vastus oli tühi."
        )

    return analysis


def main():
    print("=" * 45)
    print("AI RADAR | AUTOMAATNE AI ANALÜÜS")
    print(
        "Kuupäev:",
        datetime.now(timezone.utc).strftime("%d.%m.%Y")
    )
    print("=" * 45)

    news = get_ai_news()

    print(f"\nLeitud AI-uudiseid: {len(news)}")

    if not news:
        print("Sobivaid AI-uudiseid ei leitud.")
        return

    print("\nSaadan uudised Geminile analüüsimiseks...")

    analysis = analyze_with_gemini(news)

    print("\n" + "=" * 45)
    print("AI RADARI RAPORT")
    print("=" * 45)

    print(analysis)

    print("\n" + "=" * 45)
    print("RAPORT VALMIS")
    print("=" * 45)


if __name__ == "__main__":
    main()
