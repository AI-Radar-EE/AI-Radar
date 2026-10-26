import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

URL = "https://news.ycombinator.com/rss"

KEYWORDS = [
    "ai", "artificial intelligence", "llm", "gpt",
    "gemini", "claude", "grok", "agent",
    "machine learning", "openai", "anthropic",
    "automation", "robot"
]

print("=== AI RADAR | UUDISTE RAPORT ===")
print("Kuupäev:", datetime.now(timezone.utc).strftime("%d.%m.%Y"))
print()

request = urllib.request.Request(
    URL,
    headers={"User-Agent": "AI-Radar/1.0"}
)

with urllib.request.urlopen(request, timeout=20) as response:
    data = response.read()

root = ET.fromstring(data)
news = root.findall("./channel/item")

ai_news = []

for entry in news:
    title = entry.findtext("title", "")
    link = entry.findtext("link", "")

    words = title.lower().split()
    if any(keyword in words or keyword in title.lower()
           for keyword in KEYWORDS):
        ai_news.append((title, link))

print("Leitud AI-teemalisi uudiseid:", len(ai_news))
print()

if not ai_news:
    print("Praegu AI-teemalisi uudiseid ei leitud.")
else:
    print("=== TÄNASED AI AVASTUSED ===")

    for number, (title, link) in enumerate(ai_news[:5], 1):
        print()
        print(f"{number}. {title}")
        print(f"Allikas: {link}")

print()
print("=== RAPORT VALMIS ===")
