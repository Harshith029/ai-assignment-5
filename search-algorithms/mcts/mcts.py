import math
import random


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


def finished(board):
    return winner(board) is not None or not moves(board)


def other(player):
    return "O" if player == "X" else "X"


class Node:
    def __init__(self, board, player_to_move, parent=None, move=None):
        self.board = board[:]
        self.player_to_move = player_to_move
        self.parent = parent
        self.move = move
        self.children = []
        self.untried = moves(board)
        self.visits = 0
        self.wins = 0.0

    def best_child(self, c=1.41):
        return max(self.children, key=lambda child: child.uct(c))

    def uct(self, c):
        if self.visits == 0:
            return math.inf
        return self.wins / self.visits + c * math.sqrt(math.log(self.parent.visits) / self.visits)

    def expand(self):
        move = self.untried.pop()
        board = self.board[:]
        board[move] = self.player_to_move
        child = Node(board, other(self.player_to_move), self, move)
        self.children.append(child)
        return child


def rollout(board, player):
    board = board[:]
    turn = player
    while not finished(board):
        move = random.choice(moves(board))
        board[move] = turn
        turn = other(turn)
    return winner(board)


def backpropagate(node, result, root_player):
    while node is not None:
        node.visits += 1
        if result == root_player:
            node.wins += 1
        elif result is None:
            node.wins += 0.5
        node = node.parent


def mcts(board, player="X", simulations=1000):
    root = Node(board, player)

    for _ in range(simulations):
        node = root
        while not finished(node.board) and not node.untried:
            node = node.best_child()
        if not finished(node.board) and node.untried:
            node = node.expand()
        result = rollout(node.board, node.player_to_move)
        backpropagate(node, result, player)

    if not root.children:
        return None, []

    stats = [
        (child.move, child.visits, round(child.wins / child.visits, 3))
        for child in sorted(root.children, key=lambda item: item.move)
    ]
    best = max(root.children, key=lambda child: child.visits)
    return best.move, stats


def show(board):
    for row in range(0, 9, 3):
        print(" | ".join(board[row:row + 3]))
        if row < 6:
            print("--+---+--")


def demo():
    random.seed(7)
    board = ["X", "X", " ", "O", "O", " ", " ", " ", " "]
    print("MCTS demo")
    show(board)
    move, stats = mcts(board, "X", simulations=1500)
    print(f"Best move: {move}")
    print("move visits win_rate")
    for row in stats:
        print(row)


if __name__ == "__main__":
    demo()
