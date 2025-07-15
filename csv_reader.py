import csv

class BankCSVReader:
    """Czytnik danych z pliku CSV banku"""

    def __init__(self, filename):
        self.filename = filename

    def read(self):
        """Czyta dane z CSV i zwraca listę słowników"""
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