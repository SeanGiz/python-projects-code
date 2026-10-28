"""Guess the Number: a game with difficulty levels and a high-score table."""
import json
import random
from pathlib import Path

LEVELS = {
    "easy": (1, 50, 10),       # (lowest, highest, allowed guesses)
    "normal": (1, 100, 7),
    "hard": (1, 1000, 10),
}
SCORES_FILE = Path("guess_scores.json")


def ask_int(prompt, low, high):
    """Ask until the player types a whole number from low to high."""
    while True:
        text = input(prompt).strip()
        try:
            value = int(text)
        except ValueError:
            print("  Please type a whole number.")
            continue
        if low <= value <= high:
            return value
        print(f"  Please pick a number from {low} to {high}.")


def choose_level():
    names = ", ".join(LEVELS)
    while True:
        level = input(f"Choose a level ({names}): ").strip().lower()
        if level in LEVELS:
            return level
        print("  Unknown level.")


def hint(guess, secret):
    """Return a hint about how close the guess is."""
    distance = abs(guess - secret)
    direction = "higher" if guess < secret else "lower"
    if distance <= 3:
        return f"Very close! Go {direction}."
    if distance <= 10:
        return f"Close. Go {direction}."
    return f"Go {direction}."


def play_round(level, rng=random):
    """Play one round. Return the number of guesses used, or None if lost."""
    low, high, allowed = LEVELS[level]
    secret = rng.randint(low, high)
    print(f"I'm thinking of a number from {low} to {high}. "
          f"You have {allowed} guesses.")
    for attempt in range(1, allowed + 1):
        guess = ask_int(f"Guess #{attempt}: ", low, high)
        if guess == secret:
            print(f"Correct! You got it in {attempt} guesses.")
            return attempt
        print("  " + hint(guess, secret))
    print(f"Out of guesses! The number was {secret}.")
    return None


def load_scores():
    if SCORES_FILE.exists():
        return json.loads(SCORES_FILE.read_text())
    return {}


def save_score(level, guesses):
    """Keep the lowest score per level. Return True for a new record."""
    scores = load_scores()
    best = scores.get(level)
    if best is None or guesses < best:
        scores[level] = guesses
        SCORES_FILE.write_text(json.dumps(scores, indent=2))
        return True
    return False


def main(rng=random):
    print("=== Guess the Number ===")
    while True:
        level = choose_level()
        result = play_round(level, rng)
        if result is not None and save_score(level, result):
            print("New record for this level!")
        best = load_scores().get(level)
        if best is not None:
            print(f"Best score on {level}: {best} guesses")
        again = input("Play again? (y/n): ").strip().lower()
        if again != "y":
            print("Thanks for playing!")
            break


if __name__ == "__main__":
    main()
