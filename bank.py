"""Bank system: accounts, transfers, interest, statements, and persistence."""
import json
from dataclasses import dataclass, field, asdict
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

CENT = Decimal("0.01")


class BankError(Exception):
    """Base class for all banking errors."""


class InsufficientFunds(BankError):
    pass


class AccountNotFound(BankError):
    pass


def money(value):
    """Convert to a Decimal rounded to cents. Rejects non-positive amounts."""
    amount = Decimal(str(value)).quantize(CENT, rounding=ROUND_HALF_UP)
    if amount <= 0:
        raise BankError(f"amount must be positive, got {amount}")
    return amount


@dataclass
class Transaction:
    day: str
    kind: str
    amount: str          # stored as text to keep exact decimals in JSON
    balance: str
    note: str = ""


@dataclass
class Account:
    number: str
    owner: str
    balance: Decimal = Decimal("0.00")
    history: list[Transaction] = field(default_factory=list)

    def _record(self, kind, amount, note, day):
        self.history.append(Transaction(day.isoformat(), kind, str(amount),
                                        str(self.balance), note))

    def deposit(self, amount, note="", day=None):
        amount = money(amount)
        self.balance += amount
        self._record("deposit", amount, note, day or date.today())
        return self.balance

    def withdraw(self, amount, note="", day=None):
        amount = money(amount)
        if amount > self.balance:
            raise InsufficientFunds(
                f"{self.number}: balance {self.balance}, requested {amount}")
        self.balance -= amount
        self._record("withdraw", -amount, note, day or date.today())
        return self.balance


@dataclass
class SavingsAccount(Account):
    rate: Decimal = Decimal("0.03")         # yearly interest rate

    def add_monthly_interest(self, day=None):
        interest = (self.balance * self.rate / 12).quantize(
            CENT, rounding=ROUND_HALF_UP)
        if interest > 0:
            self.deposit(interest, "interest", day)
        return interest


class Bank:
    def __init__(self):
        self.accounts = {}
        self._next = 1001

    def open(self, owner, kind="checking", **options):
        number = f"AC{self._next}"
        self._next += 1
        cls = SavingsAccount if kind == "savings" else Account
        self.accounts[number] = cls(number, owner, **options)
        return self.accounts[number]

    def get(self, number):
        try:
            return self.accounts[number]
        except KeyError:
            raise AccountNotFound(number) from None

    def transfer(self, source, target, amount, day=None):
        src, dst = self.get(source), self.get(target)
        src.withdraw(amount, f"to {target}", day)   # fails before deposit
        dst.deposit(amount, f"from {source}", day)

    def total_deposits(self):
        return sum((a.balance for a in self.accounts.values()), Decimal("0"))

    def save(self, path):
        data = {"next": self._next, "accounts": []}
        for acc in self.accounts.values():
            record = asdict(acc)
            record["type"] = type(acc).__name__
            data["accounts"].append(record)
        Path(path).write_text(json.dumps(data, indent=2, default=str))

    @classmethod
    def load(cls, path):
        data = json.loads(Path(path).read_text())
        bank = cls()
        bank._next = data["next"]
        for rec in data["accounts"]:
            kind = rec.pop("type")
            rec["balance"] = Decimal(rec["balance"])
            rec["history"] = [Transaction(**t) for t in rec["history"]]
            if kind == "SavingsAccount":
                rec["rate"] = Decimal(rec["rate"])
                acc = SavingsAccount(**rec)
            else:
                acc = Account(**rec)
            bank.accounts[acc.number] = acc
        return bank


def statement(account):
    lines = [f"Statement for {account.number} ({account.owner})"]
    lines.append(f"{'Date':<11}{'Type':<9}{'Amount':>10}{'Balance':>11}  Note")
    for t in account.history:
        lines.append(f"{t.day:<11}{t.kind:<9}{t.amount:>10}{t.balance:>11}"
                     f"  {t.note}")
    return "\n".join(lines)
