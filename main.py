import requests
import os
from dotenv import load_dotenv

# Wczytanie zmiennych z .env
load_dotenv()

FIREFLY_URL = os.getenv("FIREFLY_URL")
TOKEN = os.getenv("FIREFLY_TOKEN")
DESCRIPTION_FILTER = "BLIK - płatność w internecie"

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.api+json"
}

def get_blik_transactions():
    url = f"{FIREFLY_URL}/api/v1/transactions"
    params = {
        "limit": 10000,
        "type": "withdrawal",
        "description": DESCRIPTION_FILTER,
    }

    transactions = []
    page = 1

    while True:
        params["page"] = page
        response = requests.get(url, headers=HEADERS, params=params)
        response.raise_for_status()
        data = response.json()

        for t in data["data"]:
            for sub in t["attributes"]["transactions"]:
                category_data = sub.get("relationships", {}).get("category", {}).get("data")
                if category_data is None and DESCRIPTION_FILTER in sub["description"]:
                    transactions.append(t)

        if not data["links"].get("next"):
            break
        page += 1

    return transactions

if __name__ == "__main__":
    results = get_blik_transactions()
    print(len(results))
