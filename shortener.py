"""URL shortener: a small Flask web app with a SQLite database."""
import secrets
import sqlite3
import string
from urllib.parse import urlparse

from flask import Flask, abort, g, jsonify, redirect, request

ALPHABET = string.ascii_letters + string.digits
PAGE = """<!doctype html>
<title>Shorty</title>
<h1>Shorty URL shortener</h1>
<form method="post" action="/shorten">
  <input name="url" size="50" placeholder="https://..." required>
  <button>Shorten</button>
</form>
{result}
"""


def create_app(database="shortener.db"):
    app = Flask(__name__)
    app.config["DATABASE"] = database

    def db():
        if "db" not in g:
            g.db = sqlite3.connect(app.config["DATABASE"])
            g.db.row_factory = sqlite3.Row
            g.db.execute("CREATE TABLE IF NOT EXISTS links ("
                         "code TEXT PRIMARY KEY, url TEXT NOT NULL, "
                         "hits INTEGER NOT NULL DEFAULT 0)")
        return g.db

    @app.teardown_appcontext
    def close_db(exc):
        conn = g.pop("db", None)
        if conn is not None:
            conn.close()

    def valid_url(url):
        parts = urlparse(url)
        return parts.scheme in ("http", "https") and bool(parts.netloc)

    def new_code(length=6):
        while True:
            code = "".join(secrets.choice(ALPHABET) for _ in range(length))
            exists = db().execute("SELECT 1 FROM links WHERE code = ?",
                                  (code,)).fetchone()
            if not exists:
                return code

    def shorten(url):
        row = db().execute("SELECT code FROM links WHERE url = ?",
                           (url,)).fetchone()
        if row:
            return row["code"]
        code = new_code()
        with db():
            db().execute("INSERT INTO links (code, url) VALUES (?, ?)",
                         (code, url))
        return code

    @app.get("/")
    def home():
        return PAGE.format(result="")

    @app.post("/shorten")
    def shorten_form():
        url = request.form.get("url", "").strip()
        if not valid_url(url):
            return PAGE.format(result="<p>Please enter a full http(s) URL."
                                      "</p>"), 400
        short = request.host_url + shorten(url)
        return PAGE.format(result=f'<p>Short link: <a href="{short}">'
                                  f"{short}</a></p>")

    @app.post("/api/links")
    def api_create():
        data = request.get_json(silent=True) or {}
        url = data.get("url", "")
        if not valid_url(url):
            return jsonify(error="a valid http(s) url is required"), 400
        code = shorten(url)
        return jsonify(code=code, short_url=request.host_url + code), 201

    @app.get("/api/links/<code>")
    def api_stats(code):
        row = db().execute("SELECT * FROM links WHERE code = ?",
                           (code,)).fetchone()
        if row is None:
            return jsonify(error="not found"), 404
        return jsonify(dict(row))

    @app.get("/<code>")
    def follow(code):
        row = db().execute("SELECT url FROM links WHERE code = ?",
                           (code,)).fetchone()
        if row is None:
            abort(404)
        with db():
            db().execute("UPDATE links SET hits = hits + 1 WHERE code = ?",
                         (code,))
        return redirect(row["url"], code=302)

    return app


if __name__ == "__main__":
    create_app().run(debug=True)
