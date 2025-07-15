import os
import requests
from bs4 import BeautifulSoup
from telegram import Bot
from dotenv import load_dotenv
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import asyncio

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

# ✅ Google Sheets Setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('creds.json', scope)
client = gspread.authorize(creds)
sheet = client.open("Internship Tracker").sheet1

# ✅ Keywords
KEYWORDS = [
    "python", "django", "flask", "machine learning", "data science", "artificial intelligence",
    "ai", "deep learning", "nlp", "remote", "work from home", "mern", "react",
    "node", "web development", "full stack", "javascript", "typescript", "flutter",
    "android", "mobile app", "internship"
]

# ✅ Telegram
async def send_notification(message):
    bot = Bot(token=TELEGRAM_TOKEN)
    await bot.send_message(chat_id=CHAT_ID, text=message, parse_mode='HTML')

# ✅ Google Sheet
def log_to_sheet(title, company, link):
    today = datetime.now().strftime("%Y-%m-%d")
    sheet.append_row([title, company, link, today])

# ✅ Scraper
def scrape_unstop():
    url = "https://unstop.com/internships/search?search=python&entity_type=internship&locations=Hyderabad"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    internships = []

    for card in soup.find_all("div", class_="event-card", limit=5):
        title_tag = card.find("h2")
        link_tag = card.find("a", class_="card-title-link")
        company_tag = card.find("div", class_="organization-name")

        if title_tag and link_tag and company_tag:
            title = title_tag.text.strip()
            link = "https://unstop.com" + link_tag["href"]
            company = company_tag.text.strip()

            # ✅ Keyword Filtering
            title_lower = title.lower()
            if any(keyword in title_lower for keyword in KEYWORDS):
                internships.append((title, company, link))

    return internships

# ✅ Main Bot Logic
async def main():
    jobs = scrape_unstop()
    if jobs:
        for title, company, link in jobs:
            msg = f"<b>{title}</b>\nCompany: {company}\n<a href='{link}'>Apply Here</a>"
            await send_notification(msg)
            log_to_sheet(title, company, link)
    else:
        await send_notification("❗ No new internships found today.")

if __name__ == "__main__":
    asyncio.run(main())
