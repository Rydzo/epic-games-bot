import requests
from datetime import datetime, UTC
from telegram import Bot
from flask import Flask
import os

# Flask app
app = Flask(__name__)

# Wczytaj dane z environment variables Render.com
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

# Rzutuj CHAT_ID na int jeśli istnieje
if CHAT_ID:
    CHAT_ID = int(CHAT_ID)
else:
    raise Exception("Brak CHAT_ID w zmiennych środowiskowych!")

if not TELEGRAM_TOKEN:
    raise Exception("Brak TELEGRAM_TOKEN w zmiennych środowiskowych!")


def get_free_epic_games():
    url = "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions?locale=pl&country=PL&allowCountries=PL"
    response = requests.get(url)
    data = response.json()
    games = data['data']['Catalog']['searchStore']['elements']
    free_games = []

    for game in games:
        title = game['title']
        promotions = game.get('promotions')
        if not promotions:
            continue

        promo = promotions.get('promotionalOffers')
        if promo:
            start_date = promo[0]['promotionalOffers'][0]['startDate']
            end_date = promo[0]['promotionalOffers'][0]['endDate']

            start = datetime.fromisoformat(start_date[:-1]).replace(tzinfo=UTC)
            end = datetime.fromisoformat(end_date[:-1]).replace(tzinfo=UTC)
            now = datetime.now(UTC)

            if start <= now <= end:
                link = f"https://store.epicgames.com/pl/p/{game['productSlug']}"
                free_games.append(f"🎮 {title} - {link}")

    return free_games


def send_games():
    bot = Bot(token=TELEGRAM_TOKEN)
    games = get_free_epic_games()
    message = "\n".join(games) if games else "Brak darmowych gier w tym momencie 🎮"
    bot.send_message(chat_id=CHAT_ID, text=message)


@app.route("/")
def home():
    return "✅ Bot działa!"


@app.route("/run")
def run_bot():
    try:
        send_games()
        return "✅ Wiadomość wysłana"
    except Exception as e:
        return f"❌ Błąd: {e}"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
