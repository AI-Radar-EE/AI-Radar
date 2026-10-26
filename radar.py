import os
import json
import re
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

# ==========================================
# AI RADAR - GEMINI VERSIOON
# ==========================================

RSS_URL = "https://news.ycombinator.com/rss"

API_BASE = "https://generativelanguage.googleapis.com/v1beta"

KEYWORDS = [
    "ai",
    "artificial intelligence",
    "llm",
    "gpt",
    "gemini",
    "claude",
    "grok",
    "agent",
    "machine learning",
    "openai",
    "anthropic",
    "automation",
    "robot"
]


# ==========================================
# API PARINGUD
# ==========================================

def api_request(url, api_key, payload=None):

    headers = {
        "x-goog-api-key": api_key,
        "Content-Type": "application/json"
    }

    data = None
    method = "GET"

    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        method = "POST"

    request = urllib.request.Request(
        url,
        data=data,
        headers=headers,
        method=method
    )

    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            return json.loads(response.read().decode("utf-8"))

    except urllib.error.HTTPError as error:

        details = error.read().decode("utf-8")

        print()
        print("GEMINI API VIGA")
        print("HTTP staatus:", error.code)
        print("Selgitus:", details[:1500])

        raise RuntimeError(
            f"Gemini API paring ebaonnestus: HTTP {error.code}"
        ) from error


# ==========================================
# GEMINI MUDELI VALIMINE
# ==========================================

def find_gemini_model(api_key):

    print("Kontrollin saadaolevaid Gemini mudeleid...")

    models = []
    page_token = None

    while True:

        url = API_BASE + "/models?pageSize=100"

        if page_token:
            from urllib.parse import quote
            url += "&pageToken=" + quote(page_token)

        result = api_request(url, api_key)

        models.extend(result.get("models", []))

        page_token = result.get("nextPageToken")

        if not page_token:
            break

    available = []

    for model in models:

        methods = model.get("supportedGenerationMethods", [])

        if "generateContent" not in methods:
            continue

        name = model.get("name", "")

        if "gemini" not in name.lower():
            continue

        available.append(name)

    if not available:
        raise RuntimeError(
            "Selle API-votmega ei leitud sobivaid Gemini mudeleid."
        )

    print("Leitud sobivaid mudeleid:", len(available))

    # Eelistame kiireid ja soodsaid Flash-mudeleid.
    # Mudeli olemasolu ei taga tasuta kvooti.

    def model_priority(name):

        lower = name.lower()

        if "flash-lite" in lower:
            priority = 0
        elif "flash" in lower:
            priority = 1
        else:
            priority = 2

        if "preview" in lower:
            priority += 1

        return (priority, name)

    available.sort(key=model_priority)

    print("Saadaolevad mudelid:", ", ".join(available))

    return available


# ==========================================
# AI UUDISTE KOGUMINE
# ==========================================

def get_ai_news():

    print()
    print("Kogun varskeid AI-uudiseid...")

    request = urllib.request.Request(
        RSS_URL,
        headers={"User-Agent": "AI-Radar/1.0"}
    )

    with urllib.request.urlopen(request, timeout=30) as response:
        data = response.read()

    root = ET.fromstring(data)

    entries = root.findall("./channel/item")

    results = []

    for entry in entries:

        title = entry.findtext("title", "")
        link = entry.findtext("link", "")

        title_lower = title.lower()

        matched = False

        for keyword in KEYWORDS:

            pattern = r"(?<!\w)" + re.escape(keyword) + r"(?!\w)"

            if re.search(pattern, title_lower):
                matched = True
                break

        if matched:

            results.append({
                "title": title,
                "link": link
            })

    return results[:5]


# ==========================================
# GEMINI ANALUUS
# ==========================================

def analyze_with_gemini(news, api_key, model):

    news_text = "\n".join(
        f"{i}. {item['title']}\nAllikas: {item['link']}"
        for i, item in enumerate(news, 1)
    )

    prompt = f"""
Sa oled AI Radar, AI-tehnoloogia ja
arivoimaluste professionaalne analuutik.

Analüüsi jargmisi AI-uudiseid.

UUDISED:

{news_text}

Koosta raport EESTI KEELES.

RAPORTI STRUKTUUR:

1. TAHTSAMAD AI-UUDISED

Selgita iga uudise voimalikku tahendust.

2. OLULISEMAD AI-TRENDID

Milliseid arengusuundi uudised naitavad?

3. ARIVOIMALUSED

Paku kolm praktilist ideed,
kuidas AI abil raha teenida.

4. PARIM IDEE

Vali koige perspektiivikam idee.

Selgita:
- Miks see on hea?
- Kellele seda muua?
- Kuidas alustada?
- Kas seda saab odavalt testida?

5. JARGMISED SAMMUD

Anna kolm konkreetset tegevust.

OLULINE:

Sul on ainult uudiste pealkirjad ja lingid.
Ara vaida, et oled artiklid labi lugenud.
Ara esita oletusi kinnitatud faktidena.

Vasta selges eesti keeles.
"""

    url = f"{API_BASE}/{model}:generateContent"

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.4,
            "maxOutputTokens": 2048
        }
    }

    print()
    print("Saadan uudised Geminile analuusimiseks...")

    result = api_request(url, api_key, payload)

    candidates = result.get("candidates", [])

    if not candidates:
        raise RuntimeError(
            "Gemini ei tagastanud vastust."
        )

    parts = candidates[0].get(
        "content", {}
    ).get("parts", [])

    analysis = "\n".join(
        part.get("text", "")
        for part in parts
        if "text" in part
    )

    if not analysis.strip():
        raise RuntimeError(
            "Gemini vastus oli tuhi."
        )

    return analysis


# ==========================================
# RAPORTI SALVESTAMINE
# ==========================================

def save_report(analysis, news, model):

    date = datetime.now(
        timezone.utc
    ).strftime("%d.%m.%Y")

    lines = [
        "# AI RADAR",
        "",
        f"Kuupaev: {date}",
        f"AI mudel: {model}",
        "",
        analysis,
        "",
        "## Uudiste allikad",
        ""
    ]

    for item in news:
        lines.append(
            f"- {item['title']}: {item['link']}"
        )

    with open(
        "AI_RADAR_REPORT.md",
        "w",
        encoding="utf-8"
    ) as file:

        file.write("\n".join(lines))

    print()
    print("Raport salvestatud: AI_RADAR_REPORT.md")


# ==========================================
# PROGRAMMI KAIVITAMINE
# ==========================================

def main():

    print("=" * 50)
    print("AI RADAR | AUTOMAATNE AI ANALUUS")
    print("=" * 50)

    print(
        "Kuupaev:",
        datetime.now(timezone.utc).strftime("%d.%m.%Y")
    )

    api_key = os.environ.get("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY puudub GitHub Secrets seadistusest."
        )

    news = get_ai_news()

    print("Leitud AI-uudiseid:", len(news))

    if not news:
        print("AI-uudiseid ei leitud.")
        return

    models = find_gemini_model(api_key)

    analysis = None
    model = None
    for candidate in models:
        try:
            print("Proovin mudelit:", candidate)
            analysis = analyze_with_gemini(news, api_key, candidate)
            model = candidate
            break
        except RuntimeError as error:
            if "HTTP 404" not in str(error):
                raise
            print("Mudel ei ole paringuks saadaval, proovin jargmist.")

    if analysis is None:
        raise RuntimeError("Ukski loetletud Gemini mudel ei vastanud. Kontrolli API vea selgitust.")

    print()
    print("=" * 50)
    print("AI RADARI RAPORT")
    print("=" * 50)

    print(analysis)

    save_report(
        analysis,
        news,
        model
    )

    print()
    print("=" * 50)
    print("AI RADAR VALMIS")
    print("=" * 50)


if __name__ == "__main__":
    main()
