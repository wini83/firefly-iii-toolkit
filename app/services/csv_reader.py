import csv
from datetime import date, datetime

from app.services.tx_processor import SimplifiedRecord


def parse_pl_date(s: str) -> date:
    """
    Parsuje datę w formacie 'DD-MM-YYYY' (np. '09-11-2025') i zwraca datetime.date.
    Rzuca ValueError przy złym formacie.
    """
    s = s.strip()
    return datetime.strptime(s, "%d-%m-%Y").date()


def parse_amount(s: str) -> float:
    """
    Parsuje kwotę w formacie polskim, zamieniając przecinki na kropki i usuwając spacje.
    Zwraca wartość typu float.
    Rzuca ValueError przy złym formacie.
    """
    s = s.strip().replace(" ", "").replace(",", ".")
    return float(s)


class BankCSVReader:
    """Czytnik danych z pliku CSV banku"""

    def __init__(self, filename):
        self.filename = filename

    def parse(self):
        """Czyta dane z CSV i zwraca listę słowników"""
        records = []
        with open(self.filename, newline="", encoding="utf-8") as csvfile:
            next(csvfile)
            reader = csv.DictReader(csvfile, delimiter=";")
            for row in reader:
                records.append(
                    SimplifiedRecord(
                        date=parse_pl_date(row["Data transakcji"]),
                        amount=parse_amount(
                            row["Kwota w walucie rachunku"].replace(",", ".").replace(" ", "")
                        ),
                        operation_amount=parse_amount(
                            row["Kwota operacji"].replace(",", ".").replace(" ", "")
                        ),
                        sender=row["Nazwa nadawcy"],
                        recipient=row["Nazwa odbiorcy"],
                        details=row["Szczegóły transakcji"],
                        operation_currency=row["Waluta operacji"],
                        account_currency=row["Waluta rachunku"],
                        sender_account=row["Numer rachunku nadawcy"],
                        recipient_account=row["Numer rachunku odbiorcy"],
                    )
                )
        return records
