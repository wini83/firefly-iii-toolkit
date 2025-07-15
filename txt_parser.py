from datetime import datetime, timedelta
from tabulate import tabulate


def _parse_date(raw):
    raw = raw.lower()
    if raw == 'dziś':
        return datetime.today().strftime('%d-%m-%Y')
    if raw == 'wczoraj':
        return (datetime.today() - timedelta(days=1)).strftime('%d-%m-%Y')
    try:
        parsed = datetime.strptime(raw, '%d.%m.%y')
        return parsed.strftime('%d-%m-%Y')
    except ValueError as exc:
        raise ValueError(f"Nieprawidłowy format daty: {raw}") from exc

def print_txt_data(data):
    """Pomocnicza funkcja do wyświetlania danych z tekstu"""
    if not data:
        print("📭 Brak danych do wyświetlenia.")
        return

    headers = ["Data", "Opis", "Odbiorca", "Kwota (PLN)"]
    rows = [[d["date"], d.get("description", ""), d["recipient"], f"{d['amount']:.2f}"] for d in data]
    print(tabulate(rows, headers=headers, tablefmt="grid"))

class TxtParser:
    """Parser tekstów skopiowanych z systemu bankowego"""

    def __init__(self, filename):
        self.filename = filename

    def parse(self):
        with open(self.filename, encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip()]

        if len(lines) % 5 != 0:
            raise ValueError("Nieprawidłowa liczba linii — dane powinny być w blokach po 5")

        records = []

        for i in range(0, len(lines), 5):
            date_str = _parse_date(lines[i])
            description = lines[i + 1]
            recipient = lines[i + 2]
            amount_str = (
                lines[i + 3].replace('PLN', '').replace(',', '.').replace(' ', '').strip()
            )
            amount = float(amount_str)

            records.append({
                "date": date_str,
                "amount": amount,
                "details": description,
                "recipient": recipient
            })

        return records

