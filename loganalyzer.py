"""Log analyzer: extract statistics from a web server access log."""
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

# Example line (Common Log Format plus response time in ms):
# 203.0.113.9 - - [28/Oct/2026:13:55:36 +0000] "GET /shop HTTP/1.1" 200 2326 41
LINE_RE = re.compile(
    r'(?P<ip>\d{1,3}(?:\.\d{1,3}){3}) \S+ \S+ '
    r'\[(?P<time>[^\]]+)\] '
    r'"(?P<method>[A-Z]+) (?P<path>\S+) [^"]*" '
    r'(?P<status>\d{3}) (?P<size>\d+|-) (?P<ms>\d+)'
)


def parse_line(line):
    """Return a dict for a valid log line, or None."""
    match = LINE_RE.match(line)
    if not match:
        return None
    entry = match.groupdict()
    entry["time"] = datetime.strptime(entry["time"], "%d/%b/%Y:%H:%M:%S %z")
    entry["status"] = int(entry["status"])
    entry["size"] = 0 if entry["size"] == "-" else int(entry["size"])
    entry["ms"] = int(entry["ms"])
    return entry


def analyze(lines):
    stats = {
        "total": 0, "bad_lines": 0, "bytes": 0,
        "status": Counter(), "paths": Counter(), "ips": Counter(),
        "hours": Counter(), "errors": Counter(), "slow": [],
    }
    for line in lines:
        entry = parse_line(line)
        if entry is None:
            stats["bad_lines"] += 1
            continue
        stats["total"] += 1
        stats["bytes"] += entry["size"]
        stats["status"][entry["status"] // 100 * 100] += 1
        stats["paths"][entry["path"]] += 1
        stats["ips"][entry["ip"]] += 1
        stats["hours"][entry["time"].hour] += 1
        if entry["status"] >= 400:
            stats["errors"][(entry["status"], entry["path"])] += 1
        stats["slow"].append((entry["ms"], entry["path"]))
    stats["slow"] = sorted(stats["slow"], reverse=True)[:3]
    return stats


def report(stats):
    total = stats["total"]
    print(f"Requests: {total}   unreadable lines: {stats['bad_lines']}")
    print(f"Data sent: {stats['bytes'] / 1024:.1f} KB\n")
    print("Status classes:")
    for status, n in sorted(stats["status"].items()):
        print(f"  {status // 100}xx  {n:>4}  {n / total:6.1%}")
    print("\nTop pages:")
    for path, n in stats["paths"].most_common(3):
        print(f"  {n:>4}  {path}")
    print("\nTop visitors:")
    for ip, n in stats["ips"].most_common(2):
        print(f"  {n:>4}  {ip}")
    print("\nErrors:")
    for (status, path), n in stats["errors"].most_common():
        print(f"  {status}  {path}  x{n}")
    print("\nSlowest requests:")
    for ms, path in stats["slow"]:
        print(f"  {ms:>5} ms  {path}")
    busiest, n = stats["hours"].most_common(1)[0]
    print(f"\nBusiest hour: {busiest:02d}:00-{busiest:02d}:59 ({n} requests)")


def main(path="access.log"):
    with open(path, encoding="utf-8", errors="replace") as f:
        report(analyze(f))


if __name__ == "__main__":
    main(*sys.argv[1:2])
