import math


DEPTH_LIMIT = 4
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


def static_score(board):
    won = winner(board)
    if won == "X":
        return 100
    if won == "O":
        return -100

    total = 0
    for line in WIN_LINES:
        cells = [board[i] for i in line]
        if "O" not in cells:
            total += 1 + cells.count("X")
        if "X" not in cells:
            total -= 1 + cells.count("O")
    return total


def search(board, depth, maximizing, alpha=-math.inf, beta=math.inf):
    if winner(board) is not None or not moves(board) or depth == 0:
        return static_score(board)

    if maximizing:
        value = -math.inf
        for move in moves(board):
            board[move] = "X"
            value = max(value, search(board, depth - 1, False, alpha, beta))
            board[move] = " "
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return value

    value = math.inf
    for move in moves(board):
        board[move] = "O"
        value = min(value, search(board, depth - 1, True, alpha, beta))
        board[move] = " "
        beta = min(beta, value)
        if alpha >= beta:
            break
    return value


def best_move(board):
    choice, best = None, -math.inf
    for move in moves(board):
        board[move] = "X"
        value = search(board, DEPTH_LIMIT, False)
        board[move] = " "
        if value > best:
            best, choice = value, move
    return choice, best


def show(board):
    for row in range(0, 9, 3):
        print(" | ".join(board[row:row + 3]))
        if row < 6:
            print("--+---+--")


def demo():
    board = ["O", "O", " ", "X", " ", " ", "X", " ", " "]
    print("Heuristic Alpha-Beta demo")
    show(board)
    move, value = best_move(board)
    print(f"Best move for X: {move}  heuristic={value}")


if __name__ == "__main__":
    demo()
