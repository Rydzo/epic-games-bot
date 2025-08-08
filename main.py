import os
import requests
from datetime import datetime, UTC
from telegram import Bot
from dotenv import load_dotenv

# Wczytaj dane z .env
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID"))

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
                slug = game.get('productSlug')
                if not slug:
                    mappings = game.get('catalogNs', {}).get('mappings')
                    if mappings and len(mappings) > 0:
                        slug = mappings[0].get('pageSlug')

                if slug:
                    link = f"https://store.epicgames.com/pl/p/{slug}"
                    free_games.append(f"🎮 {title} - {link}")
                else:
                    free_games.append(f"🎮 {title} - (brak linku)")

    return free_games

def send_games():
    bot = Bot(token=TELEGRAM_TOKEN)
    games = get_free_epic_games()
    message = "\n".join(games) if games else "Brak darmowych gier w tym momencie 🎮"

    max_length = 4096
    for i in range(0, len(message), max_length):
        bot.send_message(chat_id=CHAT_ID, text=message[i:i + max_length])

if __name__ == "__main__":
    send_games()
