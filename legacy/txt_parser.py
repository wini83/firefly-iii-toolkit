from datetime import date, datetime, timedelta

from tabulate import tabulate

from app.services.tx_processor import SimplifiedRecord


def _parse_date(raw: str) -> date:
    raw = raw.strip().lower()

    if raw == "dziś":
        return date.today()
    elif raw == "wczoraj":
        return date.today() - timedelta(days=1)

    try:
        # Format typu 17.07.25
        parsed = datetime.strptime(raw, "%d.%m.%y")
        return parsed.date()
    except ValueError:
        pass

    try:
        # ISO 8601, np. 2025-07-16T09:23:47.86Z
        if raw.endswith("z"):
            raw = raw[:-1]
        parsed = datetime.fromisoformat(raw)
        return parsed.date()
    except ValueError as exc:
        raise ValueError(f"Nieprawidłowy format daty: {raw}") from exc


def print_txt_data(data):
    """Pomocnicza funkcja do wyświetlania danych z tekstu"""
    if not data:
        print("📭 Brak danych do wyświetlenia.")
        return

    headers = ["Data", "Opis", "Odbiorca", "Kwota (PLN)"]
    rows = [
        [d["date"], d.get("description", ""), d["recipient"], f"{d['amount']:.2f}"]
        for d in data
    ]
    print(tabulate(rows, headers=headers, tablefmt="grid"))


class TxtParser:
    """Parser tekstów skopiowanych z systemu bankowego"""

    def __init__(self, filename):
        self.filename = filename

    def parse(self):
        with open(self.filename, encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]

        if len(lines) % 5 != 0:
            raise ValueError(
                "Nieprawidłowa liczba linii — dane powinny być w blokach po 5"
            )

        records = []

        for i in range(0, len(lines), 5):
            book_date = _parse_date(lines[i])
            description = lines[i + 1]
            recipient = lines[i + 2]
            amount_str = (
                lines[i + 3]
                .replace("PLN", "")
                .replace(",", ".")
                .replace(" ", "")
                .strip()
            )
            amount = float(amount_str)

            records.append(
                SimplifiedRecord(
                    date=book_date,
                    amount=amount,
                    details=description,
                    recipient=recipient,
                )
            )

        return records
