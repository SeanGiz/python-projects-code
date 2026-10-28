"""To-do manager: a command-line task list stored in SQLite."""
import argparse
import sqlite3
from datetime import date
from pathlib import Path

DB_PATH = Path("todo.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS tasks (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    title     TEXT NOT NULL,
    priority  INTEGER NOT NULL DEFAULT 2 CHECK (priority BETWEEN 1 AND 3),
    due       TEXT,
    done      INTEGER NOT NULL DEFAULT 0,
    created   TEXT NOT NULL
)
"""
PRIORITY_NAMES = {1: "high", 2: "normal", 3: "low"}


def connect(path=DB_PATH):
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row          # rows behave like dictionaries
    conn.execute(SCHEMA)
    return conn


def add_task(conn, title, priority=2, due=None):
    if due is not None:
        date.fromisoformat(due)             # raises ValueError if invalid
    with conn:                              # commits, or rolls back on error
        cur = conn.execute(
            "INSERT INTO tasks (title, priority, due, created) "
            "VALUES (?, ?, ?, ?)",
            (title, priority, due, date.today().isoformat()),
        )
    return cur.lastrowid


def list_tasks(conn, show_done=False):
    sql = "SELECT * FROM tasks"
    if not show_done:
        sql += " WHERE done = 0"
    sql += " ORDER BY done, priority, due IS NULL, due, id"
    return conn.execute(sql).fetchall()


def complete_task(conn, task_id):
    with conn:
        cur = conn.execute("UPDATE tasks SET done = 1 WHERE id = ?",
                           (task_id,))
    return cur.rowcount == 1


def delete_task(conn, task_id):
    with conn:
        cur = conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    return cur.rowcount == 1


def search_tasks(conn, text):
    return conn.execute(
        "SELECT * FROM tasks WHERE title LIKE ? ORDER BY id",
        (f"%{text}%",),
    ).fetchall()


def format_task(row, today=None):
    today = today or date.today()
    box = "[x]" if row["done"] else "[ ]"
    line = f"{row['id']:>3} {box} {row['title']:<28} " \
           f"{PRIORITY_NAMES[row['priority']]:<7}"
    if row["due"]:
        due = date.fromisoformat(row["due"])
        days = (due - today).days
        if row["done"]:
            note = ""
        elif days < 0:
            note = f" OVERDUE by {-days}d"
        elif days == 0:
            note = " due TODAY"
        else:
            note = f" in {days}d"
        line += f"{row['due']}{note}"
    return line


def build_parser():
    p = argparse.ArgumentParser(prog="todo", description="A to-do list.")
    sub = p.add_subparsers(dest="command", required=True)

    add = sub.add_parser("add", help="add a task")
    add.add_argument("title")
    add.add_argument("-p", "--priority", type=int, choices=[1, 2, 3],
                     default=2, help="1=high, 2=normal, 3=low")
    add.add_argument("-d", "--due", help="due date as YYYY-MM-DD")

    ls = sub.add_parser("list", help="show tasks")
    ls.add_argument("-a", "--all", action="store_true",
                    help="include completed tasks")

    for name in ("done", "delete"):
        cmd = sub.add_parser(name, help=f"{name} a task by id")
        cmd.add_argument("id", type=int)

    find = sub.add_parser("find", help="search task titles")
    find.add_argument("text")
    return p


def main(argv=None, db_path=DB_PATH, today=None):
    args = build_parser().parse_args(argv)
    conn = connect(db_path)
    try:
        if args.command == "add":
            try:
                task_id = add_task(conn, args.title, args.priority, args.due)
            except ValueError:
                print("Due date must look like 2026-12-31.")
                return 1
            print(f"Added task {task_id}.")
        elif args.command == "list":
            rows = list_tasks(conn, args.all)
            if not rows:
                print("Nothing to do!")
            for row in rows:
                print(format_task(row, today))
        elif args.command in ("done", "delete"):
            action = complete_task if args.command == "done" else delete_task
            if not action(conn, args.id):
                print(f"No task with id {args.id}.")
                return 1
            verb = "completed" if args.command == "done" else "deleted"
            print(f"Task {args.id} {verb}.")
        elif args.command == "find":
            for row in search_tasks(conn, args.text):
                print(format_task(row, today))
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
