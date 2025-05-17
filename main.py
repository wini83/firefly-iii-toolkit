from datetime import datetime

import requests
import os
import csv
from dotenv import load_dotenv

load_dotenv()

FIREFLY_URL = os.getenv("FIREFLY_URL")
TOKEN = os.getenv("FIREFLY_TOKEN")

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.api+json",
    "Content-Type": "application/vnd.api+json"
}

DESCRIPTION_FILTER = "BLIK - płatność w internecie"

def get_blik_transactions():
    url = f"{FIREFLY_URL}/api/v1/transactions"
    params = {
        "limit": 1000,
        "type": "withdrawal",
    }

    transactions = []
    page = 1

    while True:
        params["page"] = page
        response = requests.get(url, headers=HEADERS, params=params)
        response.raise_for_status()
        data = response.json()

        for t in data["data"]:
            subtransactions = t["attributes"]["transactions"]

            if len(subtransactions) != 1:
                print(f"⚠️ Pomijam dzieloną transakcję ID {t['id']} (liczba części: {len(subtransactions)})")
                continue

            sub = subtransactions[0]
            category_data = sub.get("relationships", {}).get("category", {}).get("data")

            if (
                    category_data is None and
                    DESCRIPTION_FILTER.lower() == sub["description"].lower()
            ):
                transactions.append({
                    "id": t["id"],
                    "description": sub["description"],
                    "amount": sub["amount"],
                    "date": sub["date"]
                })

        if not data["links"].get("next"):
            break
        page += 1

    return transactions

def read_bank_csv(filename):
    records = []
    with open(filename, newline='', encoding='utf-8') as csvfile:
        next(csvfile)
        reader = csv.DictReader(csvfile, delimiter=';')
        for row in reader:
            records.append({
                "date": row["Data transakcji"],
                "amount": row["Kwota operacji"].replace(',', '.').replace(' ', ''),
                "sender": row["Nazwa nadawcy"],
                "recipient": row["Nazwa odbiorcy"],
                "details":row["Szczegóły transakcji"]
            })
    return records

def update_transaction_description(transaction_id, new_description):
    url = f"{FIREFLY_URL}/api/v1/transactions/{transaction_id}"

    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        print(f"❌ Nie udało się pobrać transakcji {transaction_id}")
        return

    payload = {
        "apply_rules": True,
        "fire_webhooks": True,
        "transactions": [
            {"description": new_description}
        ]
    }

    put_response = requests.put(url, headers=HEADERS, json=payload)
    if put_response.status_code == 200:
        print(f"✅ Zaktualizowano opis transakcji {transaction_id}")
    else:
        print(f"❌ Błąd aktualizacji {transaction_id}: {put_response.status_code} - {put_response.text}")

if __name__ == "__main__":
    print("📥 Wczytywanie transakcji z Firefly...")
    firefly_transactions = get_blik_transactions()
    print("📥 Wczytywanie transakcji z CSV...")
    bank_data = read_bank_csv("alior.csv")

for tx in firefly_transactions:
    firefly_date = datetime.fromisoformat(tx["date"]).date()
    firefly_amount = float(tx["amount"])

    print(f"\n📌 Firefly: ID {tx['id']} | {firefly_date} | {firefly_amount} PLN | {tx['description']}")
    print("   🔍 Możliwe dopasowania z CSV:")

    matches = []
    for record in bank_data:
        csv_date = datetime.strptime(record["date"], "%d-%m-%Y").date()
        csv_amount = float(record["amount"])

        if csv_date == firefly_date and abs(csv_amount) == abs(firefly_amount):
            matches.append(record)
            print(f"   ➕ {record['date']} | {record['amount']} PLN | {record['sender']} → {record['recipient']}")

    if not matches:
        print("   ⚠️ Brak dopasowań.")
        continue

    for i, record in enumerate(matches, start=1):
        print(f"\n   💬 Dopasowanie #{i}")
        print(f"      📅 Data: {record['date']}")
        print(f"      💰 Kwota: {record['amount']} PLN")
        print(f"      👤 Nadawca: {record['sender']}")
        print(f"      🏷️ Odbiorca: {record['recipient']}")
        print(f"      📝 Szczegóły: {record['details']}")
        print(f"          Nowy opis: {tx['description']};{record['recipient']}")
        choice = input("      ❓ Czy chcesz zaktualizować opis w Firefly na podstawie tego wpisu? (t/n): ").strip().lower()
        if choice == 't':
            new_description = f"{tx['description']};{record['recipient']}"
            update_transaction_description(tx["id"], new_description)
            break  # po aktualizacji nie sprawdzaj więcej dopasowań
        else:
            print("      ⏩ Pominięto.")
