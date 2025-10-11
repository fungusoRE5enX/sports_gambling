import os
import requests
import pandas as pd
from datetime import datetime

API_KEY = "0c005ad36e5d207690781e447f51740a"
API_KEYS = {
    "ODDS_1": API_KEY,
}

def get_menu():
    url = f"https://api.the-odds-api.com/v4/sports/?apiKey={API_KEY}"
    response = requests.get(url)
    if response.status_code != 200:
        print("Error:", response.status_code, response.text)
        return
    data = response.json()
    df = pd.DataFrame(data)
    print(df.head(20))

    os.makedirs("data", exist_ok=True)
    df.to_csv("data/sports_list.csv", index=False)

def get_sports(SPORT="americanfootball_ncaaf", REGION="us", MARKETS="h2h,spreads,totals"):
    url = f"https://api.the-odds-api.com/v4/sports/{SPORT}/odds?oddsFormat=american&apiKey={API_KEY}&regions={REGION}&markets={MARKETS}&oddsFormat=american"

    now = datetime.now()
    formatted = now.strftime("%Y%m%d%H%M%S") + f"{now.microsecond:06d}"

    response = requests.get(url)
    data = response.json()

    rows = []
    for game in data:
        for bookmaker in game.get("bookmakers", []):
            for market in bookmaker.get("markets", []):
                for outcome in market.get("outcomes", []):
                    rows.append({
                        "sport": game.get("sport_title"),
                        "sport_key": game.get("sport_key"),
                        "game_id": game.get("id"),
                        "game_time": game.get("commence_time"),
                        "home_team": game.get("home_team"),
                        "away_team": game.get("away_team"),
                        "bookmaker_key": bookmaker.get("key"),
                        "bookmaker_title": bookmaker.get("title"),
                        "bookmaker_last_update": bookmaker.get("last_update"),
                        "market": market.get("key"),
                        "market_last_update": market.get("last_update"),
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
    # add