"""Budget analyzer: summarize a bank-statement CSV and chart the spending."""
import csv
from collections import defaultdict
from datetime import date
from pathlib import Path

import matplotlib
matplotlib.use("Agg")                  # draw to files; no window needed
import matplotlib.pyplot as plt        # noqa: E402

CATEGORY_RULES = {
    "groceries": ["supermarket", "grocer", "market"],
    "dining": ["cafe", "restaurant", "pizza", "coffee"],
    "transport": ["metro", "taxi", "fuel", "train"],
    "housing": ["rent", "electric", "water"],
    "fun": ["cinema", "concert", "games", "streaming"],
}


def categorize(description):
    text = description.lower()
    for category, keywords in CATEGORY_RULES.items():
        if any(k in text for k in keywords):
            return category
    return "other"


def read_transactions(path):
    """Yield dicts with date, description, amount, and category."""
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            amount = float(row["amount"])
            yield {
                "date": date.fromisoformat(row["date"]),
                "description": row["description"],
                "amount": amount,
                "category": "income" if amount > 0
                            else categorize(row["description"]),
            }


def summarize(transactions):
    """Return (income, spending by category, spending by month)."""
    income = 0.0
    by_category = defaultdict(float)
    by_month = defaultdict(float)
    for t in transactions:
        if t["amount"] > 0:
            income += t["amount"]
        else:
            spent = -t["amount"]
            by_category[t["category"]] += spent
            by_month[t["date"].strftime("%Y-%m")] += spent
    return income, dict(by_category), dict(sorted(by_month.items()))


def print_report(income, by_category, by_month):
    spent = sum(by_category.values())
    print(f"{'Income':<12}{income:>10,.2f}")
    print(f"{'Spending':<12}{spent:>10,.2f}")
    print(f"{'Saved':<12}{income - spent:>10,.2f} "
          f"({(income - spent) / income:.0%} of income)\n")
    print("By category:")
    for cat, amount in sorted(by_category.items(), key=lambda kv: -kv[1]):
        bar = "#" * round(amount / spent * 40)
        print(f"  {cat:<10}{amount:>9,.2f}  {bar}")
    print("\nBy month:")
    for month, amount in by_month.items():
        print(f"  {month}  {amount:>9,.2f}")


def save_charts(by_category, by_month, path="budget.png"):
    fig, (left, right) = plt.subplots(1, 2, figsize=(10, 4))
    items = sorted(by_category.items(), key=lambda kv: kv[1])
    left.barh([k for k, _ in items], [v for _, v in items], color="0.35")
    left.set_title("Spending by category")
    left.set_xlabel("Amount")
    right.plot(list(by_month), list(by_month.values()), marker="o",
               color="0.1")
    right.set_title("Spending by month")
    right.set_ylim(bottom=0)
    right.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)
    return Path(path)


def main(path="statement.csv"):
    transactions = list(read_transactions(path))
    income, by_category, by_month = summarize(transactions)
    print(f"{len(transactions)} transactions\n")
    print_report(income, by_category, by_month)
    chart = save_charts(by_category, by_month)
    print(f"\nChart saved to {chart}")


if __name__ == "__main__":
    main()
