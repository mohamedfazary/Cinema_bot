import os
import json
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup

URL = "https://cfc.scenecinemas.com/home"
TOKEN = os.environ["TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]
FILE = "seen.json"

# إضافة User-Agent لكي لا يتم حظر الطلب من قبل الموقع
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
response = requests.get(URL, timeout=20, headers=headers)
html = response.text
soup = BeautifulSoup(html, "html.parser")

movies = {}
for a in soup.select('a[href*="/movie-details"]'):
    name = a.get("title") or a.get("text")
    if name:
        name = name.strip()
        href = a.get("href")
        full_url = urljoin(URL, href) if href else URL
        movies[name] = full_url

# تحميل الأفلام التي تم الإشعار بها مسبقاً
seen = {}
if os.path.exists(FILE):
    try:
        with open(FILE, "r", encoding="utf-8") as f:
            seen = json.load(f)
    except Exception:
        seen = {}

# البحث عن الأفلام الجديدة غير الموجودة في الملف
new_movies = {name: link for name, link in movies.items() if name not in seen}

if new_movies:
    for name, link in new_movies.items():
        message = f"🎬 فيلم جديد في سينما كايرو فيستيفال سيتي:\n\n{name}\n{link}"
        telegram_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {
            "chat_id": CHAT_ID,
            "text": message
        }
        requests.post(telegram_url, json=payload)

    # تحديث الملف بالأفلام الجديدة حتى لا يتم تكرار الإشعار
    seen.update(new_movies)
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(seen, f, ensure_ascii=False, indent=4)
