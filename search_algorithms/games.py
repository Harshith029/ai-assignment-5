from dataclasses import dataclass


@dataclass(frozen=True)
class TTTState:
    board: tuple
    to_move: str

    def __str__(self):
        rows = [" ".join(self.board[i:i + 3]) for i in range(0, 9, 3)]
        return "\n".join(rows)


class TicTacToe:
    WIN_LINES = [
        (0, 1, 2), (3, 4, 5), (6, 7, 8),
        (0, 3, 6), (1, 4, 7), (2, 5, 8),
        (0, 4, 8), (2, 4, 6),
    ]

    def initial_state(self):
        return TTTState(tuple(["."] * 9), "X")

    def actions(self, s):
        if self._winner(s.board) is not None:
            return []
        return [i for i, c in enumerate(s.board) if c == "."]

    def result(self, s, a):
        assert s.board[a] == ".", "illegal move"
        new = list(s.board)
        new[a] = s.to_move
        nxt = "O" if s.to_move == "X" else "X"
        return TTTState(tuple(new), nxt)

    def terminal(self, s):
        return self._winner(s.board) is not None or "." not in s.board

    def utility(self, s, player):
        w = self._winner(s.board)
        if w is None or w == "draw":
            return 0
        return 1 if w == player else -1

    def to_move(self, s):
        return s.to_move

    def hash(self, s):
        return (s.board, s.to_move)

    def _winner(self, board):
        for a, b, c in self.WIN_LINES:
            if board[a] != "." and board[a] == board[b] == board[c]:
                return board[a]
        if "." not in board:
            return "draw"
        return None


ROWS, COLS = 6, 7


@dataclass(frozen=True)
class C4State:
    board: tuple   # rows bottom-up, row 0 is the bottom
    to_move: str

    def __str__(self):
        rows = []
        for r in range(ROWS - 1, -1, -1):
            rows.append(" ".join(self.board[r]))
        rows.append(" ".join(str(c) for c in range(COLS)))
        return "\n".join(rows)


class ConnectFour:

    def initial_state(self):
        empty = tuple(tuple(["."] * COLS) for _ in range(ROWS))
        return C4State(empty, "R")

    def actions(self, s):
        if self._winner(s.board) is not None:
            return []
        return [c for c in range(COLS) if s.board[ROWS - 1][c] == "."]

    def result(self, s, col):
        for r in range(ROWS):
            if s.board[r][col] == ".":
                new_board = [list(row) for row in s.board]
                new_board[r][col] = s.to_move
                nxt = "Y" if s.to_move == "R" else "R"
                return C4State(tuple(tuple(row) for row in new_board), nxt)
        raise ValueError(f"column {col} full")

    def terminal(self, s):
        if self._winner(s.board) is not None:
            return True
        return all(s.board[ROWS - 1][c] != "." for c in range(COLS))

    def utility(self, s, player):
        w = self._winner(s.board)
        if w is None or w == "draw":
            return 0
        return 1 if w == player else -1

    def to_move(self, s):
        return s.to_move

    def hash(self, s):
        return (s.board, s.to_move)

    def _winner(self, board):
        for r in range(ROWS):
            for c in range(COLS):
                p = board[r][c]
                if p == ".":
                    continue
                if c + 3 < COLS and all(board[r][c + i] == p for i in range(4)):
                    return p
                if r + 3 < ROWS and all(board[r + i][c] == p for i in range(4)):
                    return p
                if (r + 3 < ROWS and c + 3 < COLS
                        and all(board[r + i][c + i] == p for i in range(4))):
                    return p
                if (r + 3 < ROWS and c - 3 >= 0
                        and all(board[r + i][c - i] == p for i in range(4))):
                    return p
        if all(board[ROWS - 1][c] != "." for c in range(COLS)):
            return "draw"
        return None

    def heuristic(self, s, player):
        opp = "Y" if player == "R" else "R"
        score = 0.0
        b = s.board

        center = COLS // 2
        center_count = sum(1 for r in range(ROWS) if b[r][center] == player)
        score += center_count * 3

        def window_score(win):
            mine = win.count(player)
            theirs = win.count(opp)
            empty = win.count(".")
            if mine and theirs:
                return 0
            if mine == 4:    return 10000
            if mine == 3 and empty == 1: return 100
            if mine == 2 and empty == 2: return 10
            if mine == 1 and empty == 3: return 1
            if theirs == 4:  return -10000
            if theirs == 3 and empty == 1: return -120
            if theirs == 2 and empty == 2: return -10
            if theirs == 1 and empty == 3: return -1
            return 0

        windows = []
        for r in range(ROWS):
            for c in range(COLS - 3):
                windows.append([b[r][c + i] for i in range(4)])
        for c in range(COLS):
            for r in range(ROWS - 3):
                windows.append([b[r + i][c] for i in range(4)])
        for r in range(ROWS - 3):
            for c in range(COLS - 3):
                windows.append([b[r + i][c + i] for i in range(4)])
        for r in range(ROWS - 3):
            for c in range(3, COLS):
                windows.append([b[r + i][c - i] for i in range(4)])

        for w in windows:
            score += window_score(w)
        return score
