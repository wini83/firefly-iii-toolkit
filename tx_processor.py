from dataclasses import dataclass
from typing import List, cast

from fireflyiii_enricher_core.firefly_client import (
    FireflyClient,
    SimplifiedItem,
    SimplifiedTx,
    filter_by_description,
    filter_single_part,
    filter_without_category,
    simplify_transactions,
)
from fireflyiii_enricher_core.matcher import TransactionMatcher


@dataclass
class SimplifiedRecord(SimplifiedItem):
    details: str
    recipient: str
    sender: str = ""


class TransactionProcessor:
    """Logika przetwarzania i aktualizacji transakcji"""

    def __init__(self, firefly_client: FireflyClient, bank_records):
        self.firefly_client = firefly_client
        self.bank_records = bank_records

    def preview(self, filter_text: str, exact_match: bool = True):
        raw = self.firefly_client.fetch_transactions()
        single = filter_single_part(raw)
        uncategorized = filter_without_category(single)
        filtered = filter_by_description(uncategorized, filter_text, exact_match)
        firefly_transactions = simplify_transactions(filtered)

        report = []

        for tx in firefly_transactions:
            matches = TransactionMatcher.match(tx, self.bank_records)
            report.append(
                {
                    "id": tx.id,
                    "date": str(tx.date),
                    "amount": tx.amount,
                    "description": tx.description,
                    "matches": [
                        {
                            "date": str(m.date),
                            "amount": m.amount,
                            "recipient": cast(SimplifiedRecord, m).recipient,
                            "details": cast(SimplifiedRecord, m).details,
                        }
                        for m in matches
                    ],
                }
            )

        return report

    def process(self, filter_text: str, exact_match: bool = True):
        raw = self.firefly_client.fetch_transactions()
        single = filter_single_part(raw)
        uncategorized = filter_without_category(single)
        filtered = filter_by_description(uncategorized, filter_text, exact_match)
        firefly_transactions: List[SimplifiedTx] = simplify_transactions(filtered)

        for tx in firefly_transactions:
            print(
                "\n📌 Firefly: ID %s | %s | %s PLN | %s"
                % (tx.id, tx.date, tx.amount, tx.description)
            )
            print("   🔍 Możliwe dopasowania z CSV:")

            matches = TransactionMatcher.match(tx, self.bank_records)

            if not matches:
                print("   ⚠️ Brak dopasowań.")
                continue

            if "blik_done" in tx.tags:
                print("   Oznaczone tagiem 'blik_done' -omijam ")
                continue
            print(f"   Znaleziono {len(matches)} dopasowań.")
            for i, record_raw in enumerate(matches, start=1):
                record: SimplifiedRecord = cast(SimplifiedRecord, record_raw)
                sender = ""  # record.sender
                recipient = record.recipient
                if record.recipient in tx.description:
                    print("   Odbiorca jest już umieszczony -omijam ")
                    continue
                details = record.details
                print("\n   💬 Dopasowanie #%d" % i)
                print(f"      📅 Data: {record.date}")
                print(f"      💰 Kwota: {record.amount} PLN")
                print(f"      👤 Nadawca: {sender}")
                print(f"      🏷️ Odbiorca (operator_tx): {recipient}")
                print(f"      🏷️ Tagi: {tx.tags}")
                print(f"      📝 Szczegóły: {details}")
                print(f"          Nowy opis: {tx.description};{details}")
                choice = (
                    input(
                        "      ❓ Czy chcesz zaktualizować opis w Firefly na podstawie tego wpisu? (t/n/q): "
                    )
                    .strip()
                    .lower()
                )
                if choice == "t":
                    new_description = f"{tx.description};{recipient}"
                    self.firefly_client.update_transaction_description(
                        int(tx.id), new_description
                    )
                    self.firefly_client.add_tag_to_transaction(int(tx.id), "blik_done")
                    break
                if choice == "q":
                    print("🔚 Zakończono przetwarzanie.")
                    return
                print("      ⏩ Pominięto.")
