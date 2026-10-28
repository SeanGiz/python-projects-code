"""Tests for every project in Python Projects. Run: pytest book3/tests"""
import json
import os
import random
import shutil
import sys
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

CODE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(CODE))
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")


def feed(monkeypatch, *answers):
    it = iter(answers)
    monkeypatch.setattr("builtins.input", lambda prompt="": next(it))


# 1 ------------------------------------------------------------- guess
def test_guess_hint():
    import guess
    assert guess.hint(50, 52) == "Very close! Go higher."
    assert guess.hint(60, 52) == "Close. Go lower."
    assert guess.hint(10, 90) == "Go higher."


def test_guess_round_and_scores(monkeypatch, tmp_path, capsys):
    import guess
    monkeypatch.setattr(guess, "SCORES_FILE", tmp_path / "s.json")
    rng = random.Random(3)
    secret = random.Random(3).randint(1, 50)
    feed(monkeypatch, "abc", "99", "25", str(secret))
    assert guess.play_round("easy", rng) == 2
    assert guess.save_score("easy", 2) is True
    assert guess.save_score("easy", 5) is False
    assert guess.load_scores() == {"easy": 2}


# 2 ------------------------------------------------------------- passwords
def test_password_has_every_class():
    import passwords
    for _ in range(200):
        pw = passwords.generate_password(12)
        assert len(pw) == 12
        assert any(c.islower() for c in pw) and any(c.isupper() for c in pw)
        assert any(c.isdigit() for c in pw)
        assert any(c in passwords.SYMBOLS for c in pw)


def test_password_options_and_rating():
    import passwords
    pw = passwords.generate_password(20, digits=False, symbols=False)
    assert pw.isalpha()
    with pytest.raises(ValueError):
        passwords.generate_password(3)
    assert passwords.rate("password")[0] == "weak"
    assert passwords.rate("Tr0ub4dor&3xyz!Q")[0] in ("strong", "excellent")
    assert len(passwords.generate_passphrase(5).split("-")) == 5


# 3 ------------------------------------------------------------- quiz
def test_quiz(monkeypatch, capsys):
    import quiz
    questions = quiz.load_questions(CODE / "questions.json")
    assert len(questions) == 8
    q = quiz.Question("2+2?", ["3", "4"], 1)
    rng = random.Random(0)
    order = list(range(2))
    random.Random(0).shuffle(order)
    right_label = "AB"[order.index(1)]
    feed(monkeypatch, "z", right_label)
    assert quiz.ask(q, 1, rng) is True
    with pytest.raises(ValueError):
        quiz.Question.from_dict({"text": "x", "choices": ["a"], "answer": 3})


# 4 ------------------------------------------------------------- hangman
def test_hangman():
    import hangman
    g = hangman.Game("mango")
    assert g.masked == "_ _ _ _ _"
    assert "appears 1" in g.guess("m")
    assert "already" in g.guess("m")
    assert "single letter" in g.guess("ab")
    g.guess("z")
    assert g.misses == 1
    for ch in "ango":
        g.guess(ch)
    assert g.won and not g.lost


# 5 ------------------------------------------------------------- tic-tac-toe
def test_tictactoe_never_loses():
    import tictactoe as t
    for seed in range(300):
        for human in "XO":
            rng = random.Random(seed)
            board, turn, comp = " " * 9, "X", t.other(human)
            while t.winner(board) is None and not t.is_full(board):
                if turn == human:
                    i = rng.choice([k for k, c in enumerate(board) if c == " "])
                else:
                    i = t.best_move(board, comp)
                board = board[:i] + turn + board[i + 1:]
                turn = t.other(turn)
            assert t.winner(board) != human


def test_tictactoe_takes_win():
    import tictactoe as t
    assert t.best_move("OO XX    ", "X") == 5
    assert t.best_move("OO XX    ", "O") == 2


# 6 ------------------------------------------------------------- todo
def test_todo(tmp_path, capsys):
    import todo
    db = tmp_path / "t.db"
    today = date(2026, 10, 28)
    assert todo.main(["add", "Write report", "-p", "1", "-d", "2026-10-30"],
                     db, today) == 0
    todo.main(["add", "Buy milk"], db, today)
    todo.main(["add", "Pay rent", "-d", "2026-10-27"], db, today)
    assert todo.main(["add", "Bad", "-d", "31/12/2026"], db, today) == 1
    todo.main(["done", "2"], db, today)
    assert todo.main(["delete", "99"], db, today) == 1
    capsys.readouterr()
    todo.main(["list"], db, today)
    out = capsys.readouterr().out
    assert "Write report" in out and "Buy milk" not in out
    assert "OVERDUE by 1d" in out and "in 2d" in out


# 7 ------------------------------------------------------------- budget
def test_budget(tmp_path, monkeypatch):
    import make_statement
    import budget
    monkeypatch.chdir(tmp_path)
    n = make_statement.make_statement("s.csv")
    rows = list(budget.read_transactions("s.csv"))
    assert len(rows) == n
    income, by_cat, by_month = budget.summarize(rows)
    assert income == pytest.approx(9600)
    assert set(by_month) == {"2026-07", "2026-08", "2026-09"}
    assert budget.categorize("Corner Cafe") == "dining"
    assert budget.save_charts(by_cat, by_month, "c.png").exists()


# 8 ------------------------------------------------------------- organizer
def test_organizer(tmp_path, capsys):
    import organizer
    for name in ["a.JPG", "b.pdf", "c.csv", "notes.txt", "x.unknown",
                 ".hidden"]:
        (tmp_path / name).write_text("x")
    (tmp_path / "Images").mkdir()
    (tmp_path / "Images" / "a.JPG").write_text("old")
    counts = organizer.organize(tmp_path, dry_run=True)
    assert (tmp_path / "a.JPG").exists()
    assert counts == {"Images": 1, "Documents": 2, "Spreadsheets": 1,
                      "Other": 1}
    organizer.organize(tmp_path, dry_run=False)
    assert (tmp_path / "Images" / "a (1).JPG").exists()
    assert (tmp_path / "Documents" / "notes.txt").exists()
    assert (tmp_path / ".hidden").exists()


# 9 ------------------------------------------------------------- logs
def test_log_analyzer():
    import loganalyzer
    with open(CODE / "access.log") as f:
        stats = loganalyzer.analyze(f)
    assert stats["total"] == 14 and stats["bad_lines"] == 1
    assert stats["paths"].most_common(1)[0] == ("/shop", 4)
    assert stats["slow"][0] == (2350, "/checkout")
    assert stats["status"][400] == 3


# 10 ------------------------------------------------------------ adventure
def test_adventure_walkthrough():
    import adventure
    game = adventure.Game()
    for cmd in ["take driftwood", "examine driftwood", "north", "in"]:
        game.handle(cmd)
    assert "locked" in game.handle("in")
    assert "screech" in game.handle("use rusty key")
    game.handle("in")
    game.handle("take lantern oil")
    game.handle("up")
    assert "You win" in game.handle("use lantern oil")
    assert game.finished
    # A new game starts fresh: items were copied, not shared.
    assert "driftwood" in adventure.Game().here["items"]


# 11 ------------------------------------------------------------ bank
def test_bank(tmp_path):
    import bank
    b = bank.Bank()
    a = b.open("Ana")
    s = b.open("Ana", "savings", rate=Decimal("0.06"))
    a.deposit("100.10")
    b.transfer(a.number, s.number, "40")
    assert a.balance == Decimal("60.10") and s.balance == Decimal("40.00")
    with pytest.raises(bank.InsufficientFunds):
        b.transfer(a.number, s.number, 1000)
    assert a.balance == Decimal("60.10")
    with pytest.raises(bank.BankError):
        a.deposit(-5)
    with pytest.raises(bank.AccountNotFound):
        b.get("AC9")
    assert s.add_monthly_interest() == Decimal("0.20")
    b.save(tmp_path / "bank.json")
    b2 = bank.Bank.load(tmp_path / "bank.json")
    assert b2.get(s.number).balance == Decimal("40.20")
    assert isinstance(b2.get(s.number), bank.SavingsAccount)
    assert b2.open("Ben").number == "AC1003"


# 12 ------------------------------------------------------------ scraper
def test_scraper():
    import scraper
    html = (CODE / "news.html").read_text()
    heads = scraper.extract_headlines(html, "https://example.com/")
    assert [h["title"] for h in heads] == [
        "New Python release brings faster startup",
        "City expands bike lanes & parking",
        "Telescope spots three new comets",
    ]
    assert heads[0]["url"] == "https://example.com/2026/10/python-release"
    assert heads[2]["url"] == "https://other.example.org/space"


# 13 ------------------------------------------------------------ shortener
def test_shortener(tmp_path):
    import shortener
    app = shortener.create_app(str(tmp_path / "s.db"))
    client = app.test_client()
    assert client.get("/").status_code == 200
    r = client.post("/api/links", json={"url": "https://python.org/"})
    assert r.status_code == 201
    code = r.get_json()["code"]
    again = client.post("/api/links", json={"url": "https://python.org/"})
    assert again.get_json()["code"] == code
    assert client.post("/api/links", json={"url": "nope"}).status_code == 400
    hop = client.get(f"/{code}")
    assert hop.status_code == 302 and hop.location == "https://python.org/"
    assert client.get(f"/api/links/{code}").get_json()["hits"] == 1
    assert client.get("/zzzzzz").status_code == 404
    form = client.post("/shorten", data={"url": "https://example.com/a"})
    assert b"Short link" in form.data


# 14 ------------------------------------------------------------ life
def test_life():
    import life
    blinker = life.place("blinker", 2, 2)
    after = life.step(blinker, 10, 10)
    assert after == {(2, 3), (3, 3), (4, 3)}
    assert life.step(after, 10, 10) == blinker
    glider = life.place("glider")
    g = glider
    for _ in range(4):
        g = life.step(g, 20, 20)
    assert g == {(r + 1, c + 1) for r, c in glider}


# 15 ------------------------------------------------------------ snake
def test_snake_logic():
    import snake
    s = snake.Snake()
    start = s.head
    s.turn(snake.LEFT)                 # reversal ignored
    s.move()
    assert s.head == (start[0] + 1, start[1])
    s.grow = 2
    s.move()
    s.move()
    assert len(s.body) == 5
    game = snake.Game(random.Random(1))
    game.food = (game.snake.head[0] + 1, game.snake.head[1])
    game.update()
    assert game.score == 1
    for _ in range(40):
        game.update()
    assert game.over


def test_snake_draws_headless():
    import pygame
    import snake
    pygame.init()
    screen = pygame.display.set_mode((snake.WIDTH, snake.HEIGHT))
    game = snake.Game(random.Random(2))
    game.draw(screen, pygame.font.Font(None, 30))
    pygame.quit()
