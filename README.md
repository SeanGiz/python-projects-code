# Python Projects: Source Code

Companion code for *Python Projects* (The Python Path, Book 3) by Sean Giz.
Every file was tested with Python 3.14 and 3.13.

## Setup

```
python -m venv .venv
# Windows:        .venv\Scripts\activate
# macOS / Linux:  source .venv/bin/activate
pip install -r requirements.txt
```

## Projects

| # | Project | File |
|---|---|---|
| 1 | Guess the Number | guess.py |
| 2 | Password Toolkit | passwords.py |
| 3 | Quiz Master | quiz.py (uses questions.json) |
| 4 | Hangman | hangman.py |
| 5 | Unbeatable Tic-Tac-Toe | tictactoe.py |
| 6 | To-Do Manager with SQLite | todo.py |
| 7 | Budget Analyzer with Charts | budget.py (run make_statement.py first) |
| 8 | File Organizer | organizer.py |
| 9 | Log File Analyzer | loganalyzer.py (uses access.log) |
| 10 | Text Adventure | adventure.py |
| 11 | Bank Account System | bank.py |
| 12 | Web Scraper | scraper.py (uses news.html) |
| 13 | URL Shortener Web App | shortener.py |
| 14 | Conway's Game of Life | life.py |
| 15 | Snake | snake.py |

Run a project with `python guess.py` (use `python3` on macOS/Linux without an
active virtual environment). Run the tests with `pytest` from this folder.
