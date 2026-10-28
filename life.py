"""Conway's Game of Life in the terminal."""
import os
import random
import time

PATTERNS = {
    "glider": [(0, 1), (1, 2), (2, 0), (2, 1), (2, 2)],
    "blinker": [(1, 0), (1, 1), (1, 2)],
    "r_pentomino": [(0, 1), (0, 2), (1, 0), (1, 1), (2, 1)],
}


def random_cells(rows, cols, density=0.25, rng=random):
    return {(r, c) for r in range(rows) for c in range(cols)
            if rng.random() < density}


def neighbors(cell):
    r, c = cell
    return [(r + dr, c + dc)
            for dr in (-1, 0, 1) for dc in (-1, 0, 1)
            if (dr, dc) != (0, 0)]


def step(live, rows, cols):
    """Return the next generation. The board wraps around at the edges."""
    counts = {}
    for cell in live:
        for r, c in neighbors(cell):
            key = (r % rows, c % cols)
            counts[key] = counts.get(key, 0) + 1
    return {cell for cell, n in counts.items()
            if n == 3 or (n == 2 and cell in live)}


def render(live, rows, cols, alive="#", dead="."):
    return "\n".join(
        "".join(alive if (r, c) in live else dead for c in range(cols))
        for r in range(rows))


def place(pattern, top=0, left=0):
    return {(r + top, c + left) for r, c in PATTERNS[pattern]}


def run(live, rows=20, cols=40, generations=100, delay=0.1):
    seen = set()
    for gen in range(generations):
        os.system("cls" if os.name == "nt" else "clear")
        print(render(live, rows, cols))
        print(f"Generation {gen}  live cells: {len(live)}")
        state = frozenset(live)
        if state in seen:
            print("The pattern repeats; stopping.")
            break
        seen.add(state)
        live = step(live, rows, cols)
        time.sleep(delay)


if __name__ == "__main__":
    run(random_cells(20, 40))
