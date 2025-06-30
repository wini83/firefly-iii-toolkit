import os
import csv
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
import logging
from tabulate import tabulate

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("blik_sync.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

load_dotenv()

FIREFLY_URL = os.getenv("FIREFLY_URL")
TOKEN = os.getenv("FIREFLY_TOKEN")
DESCRIPTION_FILTER = "BLIK - płatność w internecie"

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.api+json",
    "Content-Type": "application/vnd.api+json"
}

class FireflyClient:
    def __init__(self, base_url, headers):
        self.base_url = base_url
        self.headers = headers

    def fetch_transactions(self, tx_type="withdrawal", limit=1000):
        logger.info(f"Pobieranie transakcji typu '{tx_type}' z Firefly...")
        url = f"{self.base_url}/api/v1/transactions"
        params = {"limit": limit, "type": tx_type}
        page = 1
        transactions = []

        while True:
            params["page"] = page
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()

            for t in data["data"]:
                transactions.append(t)

            if not data["links"].get("next"):
                break
            page += 1

        return transactions

    def filter_single_part(self, transactions):
        filtered = []
        for t in transactions:
            subtransactions = t["attributes"]["transactions"]
            if len(subtransactions) == 1:
                filtered.append(t)
            else:
                logger.warning(f"Pomijam dzieloną transakcję ID {t['id']}")
        return filtered

    def filter_without_category(self, transactions):
        filtered = []
        for t in transactions:
            sub = t["attributes"]["transactions"][0]
            category_data = sub.get("relationships", {}).get("category", {}).get("data")
            if category_data is None:
                filtered.append(t)
        return filtered

    def filter_by_description(self, transactions, description_filter, exact_match=True):
        filtered = []
        for t in transactions:
            desc = t["attributes"]["transactions"][0]["description"]
            if exact_match and desc.lower() == description_filter.lower():
                filtered.append(t)
            elif not exact_match and description_filter.lower() in desc.lower():
                filtered.append(t)
        return filtered

    def simplify_transactions(self, transactions):
        simplified = []
        for t in transactions:
            sub = t["attributes"]["transactions"][0]
            simplified.append({
                "id": t["id"],
                "description": sub["description"],
                "amount": sub["amount"],
                "date": sub["date"]
            })
        return simplified

    def update_transaction_description(self, transaction_id, new_description):
        url = f"{self.base_url}/api/v1/transactions/{transaction_id}"
        response = requests.get(url, headers=self.headers)
        if response.status_code != 200:
            logger.error(f"Nie udało się pobrać transakcji {transaction_id}")
            return

        payload = {
            "apply_rules": True,
            "fire_webhooks": True,
            "transactions": [
                {"description": new_description}
            ]
        }

        put_response = requests.put(url, headers=self.headers, json=payload)
        if put_response.status_code == 200:
            logger.info(f"Zaktualizowano opis transakcji {transaction_id}")
        else:
            logger.error(f"Błąd aktualizacji {transaction_id}: {put_response.status_code} - {put_response.text}")

class BankCSVReader:
    def __init__(self, filename):
        self.filename = filename

    def read(self):
        records = []
        with open(self.filename, newline='', encoding='utf-8') as csvfile:
            next(csvfile)
            reader = csv.DictReader(csvfile, delimiter=';')
            for row in reader:
                records.append({
                    "date": row["Data transakcji"],
                    "amount": row["Kwota operacji"].replace(',', '.').replace(' ', ''),
                    "sender": row["Nazwa nadawcy"],
                    "recipient": row["Nazwa odbiorcy"],
                    "details": row["Szczegóły transakcji"]
                })
        return records

class TransactionMatcher:
    @staticmethod
    def match(tx, records):
        firefly_date = datetime.fromisoformat(tx["date"]).date()
        firefly_amount = float(tx["amount"])

        matches = []
        for record in records:
            csv_date = datetime.strptime(record["date"], "%d-%m-%Y").date()
            csv_amount = float(record["amount"])
            if csv_date == firefly_date and abs(csv_amount) == abs(firefly_amount):
                matches.append(record)
        return matches

class TransactionProcessor:
    def __init__(self, firefly_client, bank_records):
        self.firefly_client = firefly_client
        self.bank_records = bank_records

    def process(self, filter_text: str, exact_match: bool = True):
        raw = self.firefly_client.fetch_transactions()
        single = self.firefly_client.filter_single_part(raw)
        uncategorized = self.firefly_client.filter_without_category(single)
        filtered = self.firefly_client.filter_by_description(uncategorized, filter_text, exact_match)
        firefly_transactions = self.firefly_client.simplify_transactions(filtered)

        for tx in firefly_transactions:
            print(f"\n📌 Firefly: ID {tx['id']} | {tx['date']} | {tx['amount']} PLN | {tx['description']}")
            print("   🔍 Możliwe dopasowania z CSV:")

            matches = TransactionMatcher.match(tx, self.bank_records)

            if not matches:
                print("   ⚠️ Brak dopasowań.")
                continue

            for i, record in enumerate(matches, start=1):
                sender = record.get("sender", "–")
                recipient = record.get("recipient", "–")
                details = record.get("details", "–")
                print(f"\n   💬 Dopasowanie #{i}")
                print(f"      📅 Data: {record['date']}")
                print(f"      💰 Kwota: {record['amount']} PLN")
                print(f"      👤 Nadawca: {sender}")
                print(f"      🏷️ Odbiorca: {recipient}")
                print(f"      📝 Szczegóły: {details}")
                print(f"          Nowy opis: {tx['description']};{recipient}")
                choice = input("      ❓ Czy chcesz zaktualizować opis w Firefly na podstawie tego wpisu? (t/n/q): ").strip().lower()
                if choice == 't':
                    new_description = f"{tx['description']};{recipient}"
                    self.firefly_client.update_transaction_description(tx["id"], new_description)
                    break
                elif choice == 'q':
                    print("🔚 Zakończono przetwarzanie.")
                    return
                else:
                    print("      ⏩ Pominięto.")

class TxtParser:
    def __init__(self, filename):
        self.filename = filename

    def parse(self):
        with open(self.filename, encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip()]

        if len(lines) % 5 != 0:
            raise ValueError("Nieprawidłowa liczba linii — dane powinny być w blokach po 5")

        records = []

        for i in range(0, len(lines), 5):
            date_str = self._parse_date(lines[i])
            description = lines[i + 1]
            recipient = lines[i + 2]
            amount_str = (lines[i + 3]
                          .replace('PLN', '').replace(',', '.').replace(' ', '')
                          .strip())
            amount = float(amount_str)

            records.append({
                "date": date_str,
                "amount": amount,
                "details": description,
                "recipient": recipient
            })

        return records

    def _parse_date(self, raw):
        raw = raw.lower()
        if raw == 'dziś':
            return datetime.today().strftime('%d-%m-%Y')
        elif raw == 'wczoraj':
            return (datetime.today() - timedelta(days=1)).strftime('%d-%m-%Y')
        else:
            try:
                parsed = datetime.strptime(raw, '%d.%m.%y')
                return parsed.strftime('%d-%m-%Y')
            except ValueError:
                raise ValueError(f"Nieprawidłowy format daty: {raw}")

def print_txt_data(data):
    if not data:
        print("📭 Brak danych do wyświetlenia.")
        return

    headers = ["Data", "Opis", "Odbiorca", "Kwota (PLN)"]
    rows = [[d["date"], d.get("description", ""), d["recipient"], f"{d['amount']:.2f}"] for d in data]
    print(tabulate(rows, headers=headers, tablefmt="grid"))

if __name__ == "__main__":
    logger.info("Start programu Firefly Transaction Tool")

    firefly = FireflyClient(FIREFLY_URL, HEADERS)
    txt_data = TxtParser("alior08062025.txt").parse()
    processor = TransactionProcessor(firefly, txt_data)
    processor.process(DESCRIPTION_FILTER, exact_match=True)

    logger.info("Zakończono działanie programu")