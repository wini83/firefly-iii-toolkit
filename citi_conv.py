import csv
import re

month_map = {
    "sty": "01", "lut": "02", "mar": "03", "kwi": "04",
    "maj": "05", "cze": "06", "lip": "07", "sie": "08",
    "wrz": "09", "paź": "10", "paz": "10", "lis": "11", "gru": "12"
}

def convert_date(polish_date):
    parts = polish_date.lower().split()
    if len(parts) != 3:
        return polish_date
    day, month_str, year = parts
    month = month_map.get(month_str[:3])
    if not month:
        return polish_date
    return f"{year}-{month}-{int(day):02d}"

def parse_txt_to_firefly_csv(input_file, output_file, skip_positive=True):
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]

    transactions = []
    i = 0

    date_pattern = re.compile(r"\d{1,2} \w+ \d{4}")
    foreign_currency_pattern = re.compile(r"-?\d+,\d{2}[A-Z]{3}")

    while i < len(lines):
        line = lines[i]
        if date_pattern.fullmatch(line.lower()):
            try:
                raw_date = line
                date = convert_date(raw_date)

                description = lines[i + 1]
                pln_line = lines[i + 3]
                amount = float(pln_line.replace("PLN", "").replace(",", ".").replace(" ", ""))

                if skip_positive and amount >= 0:
                    i += 4
                    continue

                currency = "PLN"
                foreign_currency = ""
                foreign_amount = ""

                if i + 4 < len(lines) and foreign_currency_pattern.fullmatch(lines[i + 4].replace(" ", "")):
                    fc_line = lines[i + 4].replace(" ", "").replace(",", ".")
                    foreign_amount = re.findall(r"\d+\.\d{2}", fc_line)[0]
                    foreign_currency = re.findall(r"[A-Z]{3}", fc_line)[-1]
                    i += 5
                else:
                    i += 4

                transactions.append([
                    date,
                    description,
                    amount,
                    currency,
                    foreign_currency,
                    foreign_amount,
                    description  # opposing_account_name
                ])
            except (IndexError, ValueError) as e:
                print(f"Skipped malformed transaction at line {i}: {e}")
                i += 1
        else:
            i += 1

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow([
            "date",
            "description",
            "amount",
            "currency",
            "foreign_currency",
            "foreign_amount",
            "opposing_account_name"
        ])
        writer.writerows(transactions)

    print(f"Saved {len(transactions)} transactions to {output_file} (skip_positive={skip_positive})")


parse_txt_to_firefly_csv("statement.txt", "firefly_import.csv")

# parse_txt_to_firefly_csv("bank_output.txt", "firefly_import.csv", skip_positive=False)