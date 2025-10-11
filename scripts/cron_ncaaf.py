import os
import requests
import pandas as pd
from datetime import datetime
from scripts.api_manager import ApiManager

# Load API keys from env
API_KEYS = [
    os.getenv("ODDS_1"),
    os.getenv("ODDS_2"),
    os.getenv("ODDS_3"),
    os.getenv("ODDS_4"),
    os.getenv("ODDS_5"),
]

api_manager = ApiManager(API_KEYS)
API_KEY = api_manager.get_next_key()

def get_sports(SPORT="americanfootball_ncaaf"):
    url = f"https://api.the-odds-api.com/v4/sports/{SPORT}/odds?oddsFormat=american&apiKey={API_KEY}&regions=us&markets=h2h,spreads,totals"
    response = requests.get(url)
    data = response.json()

    now = datetime.now()
    formatted = now.strftime("%Y%m%d%H%M%S") + f"{now.microsecond:06d}"

    rows = []
    for game in data:
        for bookmaker in game.get("bookmakers", []):
            for market in bookmaker.get("markets", []):
                for outcome in market.get("outcomes", []):
                    rows.append({
                        "sport": game.get("sport_title"),
                        "game_time": game.get("commence_time"),
                        "home_team": game.get("home_team"),
                        "away_team": game.get("away_team"),
                        "bookmaker": bookmaker.get("title"),
                        "market": market.get("key"),
                        "team": outcome.get("name"),
                        "price": outcome.get("price"),
                        "point": outcome.get("point"),
                        "query_time": formatted
                    })

    df = pd.DataFrame(rows)
    os.makedirs(f"data/{SPORT}", exist_ok=True)
    df.to_csv(f"data/{SPORT}/{formatted}.csv", index=False)

if __name__ == "__main__":
    get_sports()
