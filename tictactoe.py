"""Tic-Tac-Toe against an unbeatable computer player (minimax)."""
from functools import cache

LINES = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),      # rows
    (0, 3, 6), (1, 4, 7), (2, 5, 8),      # columns
    (0, 4, 8), (2, 4, 6),                 # diagonals
]


def winner(board):
    """Return 'X' or 'O' if someone has three in a row, else None."""
    for a, b, c in LINES:
        if board[a] != " " and board[a] == board[b] == board[c]:
            return board[a]
    return None


def is_full(board):
    return " " not in board


def show(board):
    cells = [c if c != " " else str(i + 1) for i, c in enumerate(board)]
    rows = [" | ".join(cells[r:r + 3]) for r in (0, 3, 6)]
    print("\n" + "\n---------\n".join(" " + row for row in rows) + "\n")


def other(player):
    return "O" if player == "X" else "X"


@cache
def minimax(board, player, me):
    """Score `board` from `me`'s point of view, with `player` to move.

    A win for `me` scores 10 minus the number of moves it took, a loss
    scores the moves it took minus 10, and a draw scores 0. So the computer
    prefers fast wins and slow losses.
    """
    depth = 9 - board.count(" ")
    win = winner(board)
    if win == me:
        return 10 - depth
    if win is not None:
        return depth - 10
    if is_full(board):
        return 0
    scores = []
    for i, cell in enumerate(board):
        if cell == " ":
            child = board[:i] + player + board[i + 1:]
            scores.append(minimax(child, other(player), me))
    return max(scores) if player == me else min(scores)


def best_move(board, me):
    """Return the index of the best move for `me`."""
    best_score, best_index = None, None
    for i, cell in enumerate(board):
        if cell == " ":
            child = board[:i] + me + board[i + 1:]
            score = minimax(child, other(me), me)
            if best_score is None or score > best_score:
                best_score, best_index = score, i
    return best_index


def ask_move(board):
    while True:
        text = input("Your move (1-9): ").strip()
        if text.isdigit() and 1 <= int(text) <= 9:
            index = int(text) - 1
            if board[index] == " ":
                return index
            print("That square is taken.")
        else:
            print("Please type a number from 1 to 9.")


def play(human="X"):
    board = " " * 9                      # a string: immutable, so cacheable
    computer = other(human)
    turn = "X"
    show(board)
    while winner(board) is None and not is_full(board):
        if turn == human:
            index = ask_move(board)
        else:
            index = best_move(board, computer)
            print(f"Computer plays {index + 1}")
        board = board[:index] + turn + board[index + 1:]
        show(board)
        turn = other(turn)
    result = winner(board)
    if result == human:
        print("You win! (That shouldn't be possible...)")
    elif result == computer:
        print("The computer wins!")
    else:
        print("It's a draw.")
    return result


if __name__ == "__main__":
    play()
