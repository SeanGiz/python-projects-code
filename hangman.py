"""Hangman: guess the word one letter at a time."""
import random

WORDS = {
    "animals": ["giraffe", "penguin", "dolphin", "kangaroo", "octopus"],
    "fruits": ["banana", "mango", "pineapple", "blueberry", "apricot"],
    "tech": ["python", "keyboard", "network", "algorithm", "database"],
}

STAGES = [
    "",
    "\n\n\n\n\n=========",
    "\n  |\n  |\n  |\n  |\n  |\n=========",
    "  +---+\n  |\n  |\n  |\n  |\n  |\n=========",
    "  +---+\n  |   |\n  |   O\n  |\n  |\n  |\n=========",
    "  +---+\n  |   |\n  |   O\n  |   |\n  |\n  |\n=========",
    "  +---+\n  |   |\n  |   O\n  |  /|\\\n  |\n  |\n=========",
    "  +---+\n  |   |\n  |   O\n  |  /|\\\n  |  / \\\n  |\n=========",
]
MAX_MISSES = len(STAGES) - 1


class Game:
    def __init__(self, word):
        self.word = word.lower()
        self.guessed = set()
        self.misses = 0

    @property
    def masked(self):
        return " ".join(c if c in self.guessed else "_" for c in self.word)

    @property
    def won(self):
        return set(self.word) <= self.guessed

    @property
    def lost(self):
        return self.misses >= MAX_MISSES

    def guess(self, letter):
        """Apply a guess; return a message describing what happened."""
        letter = letter.lower()
        if len(letter) != 1 or not letter.isalpha():
            return "Please type a single letter."
        if letter in self.guessed:
            return f"You already tried '{letter}'."
        self.guessed.add(letter)
        if letter in self.word:
            count = self.word.count(letter)
            return f"Yes! '{letter}' appears {count} time(s)."
        self.misses += 1
        return f"No '{letter}'. {MAX_MISSES - self.misses} misses left."


def play(word, category):
    game = Game(word)
    print(f"Category: {category} ({len(word)} letters)")
    while not (game.won or game.lost):
        print(STAGES[game.misses])
        print("\nWord:", game.masked)
        tried = " ".join(sorted(game.guessed)) or "-"
        print("Tried:", tried)
        print(game.guess(input("Letter: ").strip()))
    print(STAGES[game.misses])
    if game.won:
        print(f"\nYou won! The word was '{word}'.")
    else:
        print(f"\nYou lost! The word was '{word}'.")
    return game.won


def main(rng=random):
    category = rng.choice(sorted(WORDS))
    word = rng.choice(WORDS[category])
    play(word, category)


if __name__ == "__main__":
    main()
