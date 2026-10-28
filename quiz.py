"""Quiz Master: a multiple-choice quiz loaded from a JSON question bank."""
import json
import random
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Question:
    text: str
    choices: list[str]
    answer: int            # index of the correct choice
    category: str = "general"

    @classmethod
    def from_dict(cls, data):
        q = cls(data["text"], data["choices"], data["answer"],
                data.get("category", "general"))
        if not 0 <= q.answer < len(q.choices):
            raise ValueError(f"bad answer index in: {q.text!r}")
        return q


def load_questions(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return [Question.from_dict(item) for item in data]


def ask(question, number, rng=random):
    """Show one question with shuffled choices. Return True if correct."""
    order = list(range(len(question.choices)))
    rng.shuffle(order)
    print(f"\nQ{number}. {question.text}")
    for label, index in zip("ABCD", order):
        print(f"   {label}) {question.choices[index]}")
    valid = "ABCD"[:len(order)]
    while True:
        reply = input("Your answer: ").strip().upper()
        if len(reply) == 1 and reply in valid:
            break
        print(f"   Please type one of: {', '.join(valid)}")
    chosen = order[valid.index(reply)]
    if chosen == question.answer:
        print("   Correct!")
        return True
    correct_label = valid[order.index(question.answer)]
    print(f"   Wrong. The answer was {correct_label}) "
          f"{question.choices[question.answer]}")
    return False


def run_quiz(questions, how_many=5, rng=random):
    """Ask a random selection of questions; return (score, per-category)."""
    selected = rng.sample(questions, min(how_many, len(questions)))
    score = 0
    by_category = {}
    for number, q in enumerate(selected, start=1):
        correct = ask(q, number, rng)
        score += correct
        right, total = by_category.get(q.category, (0, 0))
        by_category[q.category] = (right + correct, total + 1)
    return score, len(selected), by_category


def report(score, total, by_category):
    percent = score / total * 100
    print(f"\nYou scored {score}/{total} ({percent:.0f}%).")
    for category, (right, count) in sorted(by_category.items()):
        print(f"  {category:<10} {right}/{count}")
    if percent == 100:
        print("Perfect score!")
    elif percent >= 60:
        print("Well done!")
    else:
        print("Keep practicing!")


def main(path="questions.json", rng=random):
    questions = load_questions(path)
    print(f"Quiz Master: {len(questions)} questions loaded.")
    report(*run_quiz(questions, rng=rng))


if __name__ == "__main__":
    main()
