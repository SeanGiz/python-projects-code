"""Password toolkit: generate passwords and passphrases, rate strength."""
import argparse
import math
import secrets
import string

SYMBOLS = "!@#$%^&*-_=+?"
WORDS = (
    "apple river candle orbit mango tiger velvet cloud piano rocket "
    "maple ocean pixel lemon falcon garden marble comet harbor quartz "
    "willow ember canyon violet anchor meadow nectar summit lantern breeze "
    "cobalt saffron glacier thunder koala walnut cactus nebula island prism"
).split()


def generate_password(length=16, digits=True, symbols=True):
    """Return a random password containing at least one of each chosen kind."""
    pools = [string.ascii_lowercase, string.ascii_uppercase]
    if digits:
        pools.append(string.digits)
    if symbols:
        pools.append(SYMBOLS)
    if length < len(pools):
        raise ValueError(f"length must be at least {len(pools)}")
    alphabet = "".join(pools)
    # One guaranteed character from each pool, the rest from everything.
    chars = [secrets.choice(pool) for pool in pools]
    chars += [secrets.choice(alphabet) for _ in range(length - len(pools))]
    # Shuffle so the guaranteed characters aren't always at the start.
    for i in range(len(chars) - 1, 0, -1):
        j = secrets.randbelow(i + 1)
        chars[i], chars[j] = chars[j], chars[i]
    return "".join(chars)


def generate_passphrase(words=4, separator="-", wordlist=WORDS):
    """Return a passphrase of random words, e.g. 'maple-rocket-ember-prism'."""
    return separator.join(secrets.choice(wordlist) for _ in range(words))


def entropy_bits(password):
    """Estimate entropy from the character classes used and the length."""
    pool = 0
    if any(c.islower() for c in password):
        pool += 26
    if any(c.isupper() for c in password):
        pool += 26
    if any(c.isdigit() for c in password):
        pool += 10
    if any(not c.isalnum() for c in password):
        pool += len(SYMBOLS)
    return len(password) * math.log2(pool) if pool else 0.0


def rate(password):
    """Return (label, bits, list of tips) for a password."""
    bits = round(entropy_bits(password))
    tips = []
    if len(password) < 12:
        tips.append("use at least 12 characters")
    if password.lower() in {"password", "123456", "qwerty", "letmein"}:
        tips.append("this is one of the most common passwords")
        bits = 0
    if len(set(password)) <= len(password) // 2:
        tips.append("avoid repeating characters")
    if bits < 40:
        label = "weak"
    elif bits < 70:
        label = "fair"
    elif bits < 100:
        label = "strong"
    else:
        label = "excellent"
    return label, bits, tips


def build_parser():
    p = argparse.ArgumentParser(prog="passwords",
                                description="Generate and check passwords.")
    sub = p.add_subparsers(dest="command", required=True)

    gen = sub.add_parser("gen", help="generate passwords")
    gen.add_argument("-n", "--count", type=int, default=1)
    gen.add_argument("-l", "--length", type=int, default=16)
    gen.add_argument("--no-digits", action="store_true")
    gen.add_argument("--no-symbols", action="store_true")

    phrase = sub.add_parser("phrase", help="generate a passphrase")
    phrase.add_argument("-w", "--words", type=int, default=4)

    check = sub.add_parser("check", help="rate a password's strength")
    check.add_argument("password")
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    if args.command == "gen":
        for _ in range(args.count):
            print(generate_password(args.length, not args.no_digits,
                                    not args.no_symbols))
    elif args.command == "phrase":
        print(generate_passphrase(args.words))
    else:
        label, bits, tips = rate(args.password)
        print(f"Strength: {label} (about {bits} bits)")
        for tip in tips:
            print(f"  - {tip}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
