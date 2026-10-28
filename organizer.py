"""File organizer: sort a messy folder into subfolders by file type."""
import argparse
import shutil
from pathlib import Path

CATEGORIES = {
    "Images": {".jpg", ".jpeg", ".png", ".gif", ".webp", ".heic", ".svg"},
    "Documents": {".pdf", ".docx", ".doc", ".txt", ".md", ".odt", ".rtf"},
    "Spreadsheets": {".xlsx", ".xls", ".csv", ".ods"},
    "Audio": {".mp3", ".wav", ".flac", ".m4a"},
    "Video": {".mp4", ".mov", ".mkv", ".avi"},
    "Archives": {".zip", ".tar", ".gz", ".7z", ".rar"},
    "Code": {".py", ".js", ".html", ".css", ".json", ".ipynb"},
}


def category_for(path):
    suffix = path.suffix.lower()
    for category, suffixes in CATEGORIES.items():
        if suffix in suffixes:
            return category
    return "Other"


def unique_destination(target):
    """Return target, or 'name (1).ext', 'name (2).ext'... if it exists."""
    if not target.exists():
        return target
    n = 1
    while True:
        candidate = target.with_name(f"{target.stem} ({n}){target.suffix}")
        if not candidate.exists():
            return candidate
        n += 1


def plan_moves(folder):
    """Return a list of (source, destination) pairs. Changes nothing."""
    moves = []
    for path in sorted(folder.iterdir()):
        if path.is_file() and not path.name.startswith("."):
            destination = folder / category_for(path) / path.name
            moves.append((path, destination))
    return moves


def organize(folder, dry_run=True):
    folder = Path(folder)
    moves = plan_moves(folder)
    counts = {}
    for source, destination in moves:
        category = destination.parent.name
        counts[category] = counts.get(category, 0) + 1
        if dry_run:
            print(f"would move {source.name} -> {category}/")
            continue
        destination.parent.mkdir(exist_ok=True)
        final = unique_destination(destination)
        shutil.move(source, final)
        print(f"moved {source.name} -> {category}/{final.name}")
    return counts


def build_parser():
    p = argparse.ArgumentParser(prog="organizer",
                                description="Sort files into folders by type.")
    p.add_argument("folder", type=Path)
    p.add_argument("--apply", action="store_true",
                   help="actually move files (default is a dry run)")
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    if not args.folder.is_dir():
        print(f"Not a folder: {args.folder}")
        return 1
    counts = organize(args.folder, dry_run=not args.apply)
    total = sum(counts.values())
    summary = ", ".join(f"{n} {c}" for c, n in sorted(counts.items()))
    verb = "Moved" if args.apply else "Would move"
    print(f"{verb} {total} files: {summary or 'nothing to do'}")
    if not args.apply and total:
        print("Run again with --apply to move them.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
