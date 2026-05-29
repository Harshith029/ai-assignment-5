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


def evaluate(board):
    won = winner(board)
    if won == "X":
        return 10
    if won == "O":
        return -10
    return 0


def finished(board):
    return winner(board) is not None or not moves(board)


def alpha_beta(board, maximizing, alpha=-math.inf, beta=math.inf, stats=None):
    if stats is not None:
        stats["nodes"] += 1

    if finished(board):
        return evaluate(board)

    if maximizing:
        value = -math.inf
        for move in moves(board):
            board[move] = "X"
            value = max(value, alpha_beta(board, False, alpha, beta, stats))
            board[move] = " "
            alpha = max(alpha, value)
            if alpha >= beta:
                if stats is not None:
                    stats["cutoffs"] += 1
                break
        return value

    value = math.inf
    for move in moves(board):
        board[move] = "O"
        value = min(value, alpha_beta(board, True, alpha, beta, stats))
        board[move] = " "
        beta = min(beta, value)
        if alpha >= beta:
            if stats is not None:
                stats["cutoffs"] += 1
            break
    return value


def best_move(board, player="X"):
    stats = {"nodes": 0, "cutoffs": 0}
    maximizing = player == "X"
    best = -math.inf if maximizing else math.inf
    choice = None

    for move in moves(board):
        board[move] = player
        value = alpha_beta(board, not maximizing, stats=stats)
        board[move] = " "

        if maximizing and value > best:
            best, choice = value, move
        if not maximizing and value < best:
            best, choice = value, move

    return choice, best, stats


def show(board):
    for row in range(0, 9, 3):
        print(" | ".join(board[row:row + 3]))
        if row < 6:
            print("--+---+--")


def demo():
    board = ["O", "O", " ", "X", " ", " ", "X", " ", " "]
    print("Alpha-Beta demo")
    show(board)
    move, value, stats = best_move(board, "X")
    print(f"Best move: {move}  score={value}")
    print(f"Nodes: {stats['nodes']}  cutoffs={stats['cutoffs']}")


if __name__ == "__main__":
    demo()
