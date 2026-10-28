"""Create a sample bank statement, statement.csv, for the budget analyzer."""
import csv
import random
from datetime import date, timedelta

PAYEES = [
    ("City Supermarket", -82.40), ("Corner Cafe", -6.50),
    ("Metro card top-up", -30.00), ("Pizza Palace", -24.90),
    ("Fresh Market", -45.15), ("Cinema City", -18.00),
    ("Taxi ride", -16.75), ("Streaming service", -12.99),
    ("Bookshop", -21.00), ("Coffee Corner", -4.20),
]


def make_statement(path="statement.csv", months=3, seed=42):
    rng = random.Random(seed)
    rows = []
    start = date(2026, 7, 1)
    for m in range(months):
        first = date(start.year, start.month + m, 1)
        rows.append((first, "Salary ACME Ltd", 3200.00))
        rows.append((first + timedelta(days=1), "Rent payment", -1250.00))
        rows.append((first + timedelta(days=14), "Electric bill",
                     -round(rng.uniform(60, 90), 2)))
        for _ in range(18):
            name, amount = rng.choice(PAYEES)
            day = first + timedelta(days=rng.randrange(28))
            rows.append((day, name, round(amount * rng.uniform(0.8, 1.2), 2)))
    rows.sort()
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["date", "description", "amount"])
        for d, desc, amount in rows:
            writer.writerow([d.isoformat(), desc, f"{amount:.2f}"])
    return len(rows)


if __name__ == "__main__":
    print(make_statement(), "rows written")
