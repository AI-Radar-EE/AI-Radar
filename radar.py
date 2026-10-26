import urllib.request
import xml.etree.ElementTree as ET

url = "https://news.ycombinator.com/rss"

print("AI Radar käivitus!")
print("Otsin Hacker Newsi uudiseid...\n")

with urllib.request.urlopen(url, timeout=20) as response:
    data = response.read()

root = ET.fromstring(data)

for entry in root.findall("./channel/item")[:10]:
    title = entry.findtext("title", "Pealkiri puudub")
    link = entry.findtext("link", "")

    print(title)
    print(link)
    print("---")
