"""Web scraper: collect article headlines and links from an HTML page."""
import csv
import sys
from html.parser import HTMLParser
from urllib.parse import urljoin
from urllib.request import Request, urlopen


class HeadlineParser(HTMLParser):
    """Collect the text and link of every <a> inside an <h2 class="title">."""

    def __init__(self, base_url=""):
        super().__init__()
        self.base_url = base_url
        self.in_title = False
        self.current_link = None
        self.text_parts = []
        self.headlines = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "h2" and "title" in attrs.get("class", "").split():
            self.in_title = True
        elif tag == "a" and self.in_title:
            self.current_link = urljoin(self.base_url, attrs.get("href", ""))
            self.text_parts = []

    def handle_data(self, data):
        if self.current_link is not None:
            self.text_parts.append(data)

    def handle_endtag(self, tag):
        if tag == "a" and self.current_link is not None:
            text = " ".join("".join(self.text_parts).split())
            if text:
                self.headlines.append({"title": text,
                                       "url": self.current_link})
            self.current_link = None
        elif tag == "h2":
            self.in_title = False


def fetch(url, timeout=10):
    """Download a page politely, identifying ourselves with a User-Agent."""
    request = Request(url, headers={"User-Agent": "PythonPathScraper/1.0"})
    with urlopen(request, timeout=timeout) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        return response.read().decode(charset, errors="replace")


def extract_headlines(html, base_url=""):
    parser = HeadlineParser(base_url)
    parser.feed(html)
    parser.close()
    return parser.headlines


def save_csv(headlines, path):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["title", "url"])
        writer.writeheader()
        writer.writerows(headlines)


def main(source):
    if source.startswith(("http://", "https://")):
        html = fetch(source)
        base = source
    else:
        with open(source, encoding="utf-8") as f:
            html = f.read()
        base = "https://example.com/"
    headlines = extract_headlines(html, base)
    for i, h in enumerate(headlines, start=1):
        print(f"{i}. {h['title']}\n   {h['url']}")
    save_csv(headlines, "headlines.csv")
    print(f"\nSaved {len(headlines)} headlines to headlines.csv")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "news.html")
