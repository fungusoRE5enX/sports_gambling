import os
import json
import requests
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

# --- Load local .env if present ---
load_dotenv()

# --- API Key Manager ---
class ApiManager:
    STATE_FILE = ".api_state.json"

    def __init__(self, keys):
        if not keys:
            raise ValueError("No API keys provided to ApiManager!")
        self.keys = keys
        # Load last index or start at 0
        if os.path.exists(self.STATE_FILE):
            with open(self.STATE_FILE, "r") as f:
                state = json.load(f)
                self.index = state.get("index", 0)
        else:
            self.index = 0

    def get_next_key(self):
        key = self.keys[self.index % len(self.keys)]
        self.index = (self.index + 1) % len(self.keys)
        # save state
        with open(self.STATE_FILE, "w") as f:
            json.dump({"index": self.index}, f)
        return key

# --- Get API keys from environment variables ---
API_KEYS = []
for i in range(1, 6):  # Assuming 5 keys: ODDS_1 to ODDS_5
    key = os.getenv(f"ODDS_{i}")
    if key:
        API_KEYS.append(key)

if not API_KEYS:
    raise ValueError("No API keys set in environment variables!")

api_manager = ApiManager(API_KEYS)

# --- Project Root & Data Directory ---
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_ROOT = os.path.join(PROJECT_ROOT, "data")

# --- Functions ---
def get_sports(SPORT="americanfootball_ncaaf", REGION="us", MARKETS="h2h,spreads,totals"):
    API_KEY = api_manager.get_next_key()
    url = f"https://api.the-odds-api.com/v4/sports/{SPORT}/odds"
    params = {
        "apiKey": API_KEY,
        "regions": REGION,
        "markets": MARKETS,
        "oddsFormat": "american"
    }

    response = requests.get(url, params=params)
    
    try:
        data = response.json()
    except json.JSONDecodeError:
        print("Error decoding JSON:", response.text)
        return

    if not isinstance(data, list):
        print("Unexpected API response:", data)
        return

    now = datetime.now()
    formatted = now.strftime("%Y%m%d%H%M%S") + f"{now.microsecond:06d}"

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

    # Save to correct folder
    SPORT_DIR = os.path.join(DATA_ROOT, SPORT)
    os.makedirs(SPORT_DIR, exist_ok=True)
    filepath = os.path.join(SPORT_DIR, f"{formatted}.csv")
    df.to_csv(filepath, index=False)
    print(f"Saved {len(df)} rows to {filepath}")


# --- Main ---
if __name__ == "__main__":
    get_sports()
