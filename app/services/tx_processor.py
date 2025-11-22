from dataclasses import dataclass, fields
from typing import List, cast

from fireflyiii_enricher_core.firefly_client import (
    FireflyClient,
    SimplifiedItem,
    SimplifiedTx,
    filter_by_description,
    filter_single_part,
    filter_without_category,
    simplify_transactions,filter_without_tag
)
from fireflyiii_enricher_core.matcher import TransactionMatcher


@dataclass
class SimplifiedRecord(SimplifiedItem):
    details: str
    recipient: str
    operation_amount: float
    sender: str = ""
    operation_currency: str = "PLN"
    account_currency: str = "PLN"
    sender_account: str = ""
    recipient_account: str = ""

    def pretty_print(self):
        return "\n".join(f"{f.name}: {getattr(self, f.name)}" for f in fields(self))


@dataclass
class MatchResult:
    tx: SimplifiedTx
    matches: List[SimplifiedRecord]

def add_line(existing: str | None, new_line: str) -> str:
    if existing:
        return existing + "\n" + new_line
    return new_line

class TransactionProcessor:
    """Logika przetwarzania i aktualizacji transakcji"""

    def __init__(self, firefly_client: FireflyClient):
        self.firefly_client = firefly_client

    def match(
        self,
        bank_records: List[SimplifiedRecord],
        filter_text: str,
        exact_match: bool = True,
        tag: str = "blik_done",
    ):
        min_date = min(r.date for r in bank_records)
        max_date = max(r.date for r in bank_records)
        raw = self.firefly_client.fetch_transactions(
            start_date=min_date, end_date=max_date
        )
        single = filter_single_part(raw)
        uncategorized = filter_without_category(single)
        filtered = filter_by_description(uncategorized, filter_text, exact_match)
        filtered = filter_without_tag(filtered, tag)
        firefly_transactions = simplify_transactions(filtered)

        txs: List[MatchResult] = []

        for tx in firefly_transactions:
            matches = TransactionMatcher.match(
                tx, cast(List[SimplifiedItem], bank_records)
            )
            txs.append(
                MatchResult(tx=tx, matches=cast(List[SimplifiedRecord], matches))
            )
        return txs

    def apply_match(self, tx: SimplifiedTx, record: SimplifiedRecord):
        new_description = f"{tx.description};{record.details}"
        self.firefly_client.update_transaction_description(int(tx.id), new_description)
        notes = add_line(tx.notes, record.pretty_print())
        self.firefly_client.update_transaction_notes(int(tx.id), notes)
        self.firefly_client.add_tag_to_transaction(int(tx.id), "blik_done")
