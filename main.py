import asyncio
import requests
from datetime import datetime, UTC
from telegram import Bot
from flask import Flask
import os

app = Flask(__name__)

TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
CHAT_ID = int(os.environ['CHAT_ID'])


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


async def send_games():
    bot = Bot(token=TELEGRAM_TOKEN)
    games = get_free_epic_games()
    message = "\n".join(
        games) if games else "Brak darmowych gier w tym momencie 🎮"
    await bot.send_message(chat_id=CHAT_ID, text=message)


@app.route("/")
def home():
    return "Bot działa!"


@app.route("/run")
def run_bot():
    asyncio.run(send_games())
    return "Wiadomość wysłana ✅"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
