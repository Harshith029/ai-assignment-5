import math


WIN_LINES = (
    (0, 1, 2), (3, 4, 5), (6, 7, 8),
    (0, 3, 6), (1, 4, 7), (2, 5, 8),
    (0, 4, 8), (2, 4, 6),
)


def moves(board):
    return [i for i, cell in enumerate(board) if cell == " "]


def winner(board):
    for a, b, c in WIN_LINES:
        if board[a] != " " and board[a] == board[b] == board[c]:
            return board[a]
    return None


def terminal(board):
    return winner(board) is not None or not moves(board)


def score(board):
    won = winner(board)
    if won == "X":
        return 10
    if won == "O":
        return -10
    return 0


def minimax(board, maximizing):
    if terminal(board):
        return score(board)

    if maximizing:
        best = -math.inf
        for move in moves(board):
            board[move] = "X"
            best = max(best, minimax(board, False))
            board[move] = " "
        return best

    best = math.inf
    for move in moves(board):
        board[move] = "O"
        best = min(best, minimax(board, True))
        board[move] = " "
    return best


def best_move(board, player="X"):
    maximizing = player == "X"
    best = -math.inf if maximizing else math.inf
    choice = None

    for move in moves(board):
        board[move] = player
        value = minimax(board, not maximizing)
        board[move] = " "

        if maximizing and value > best:
            best, choice = value, move
        if not maximizing and value < best:
            best, choice = value, move

    return choice, best


def show(board):
    for row in range(0, 9, 3):
        print(" | ".join(board[row:row + 3]))
        if row < 6:
            print("--+---+--")


def demo():
    cases = [
        ("X can win", ["X", "X", " ", "O", "O", " ", " ", " ", " "], "X"),
        ("X must block", ["O", "O", " ", "X", " ", " ", "X", " ", " "], "X"),
        ("Empty board", [" "] * 9, "X"),
    ]

    for label, board, player in cases:
        print(f"\n{label}")
        show(board)
        move, value = best_move(board, player)
        print(f"Best move for {player}: {move}  score={value}")


if __name__ == "__main__":
    demo()
