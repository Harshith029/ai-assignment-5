"""
Minimax, alpha-beta, heuristic alpha-beta, MCTS.
Each takes (game, state) and returns (action, stats).
"""

import math
import random
import time


INF = float("inf")


def minimax(game, state):
    stats = {"nodes": 0}
    me = game.to_move(state)

    def max_value(s):
        stats["nodes"] += 1
        if game.terminal(s):
            return game.utility(s, me), None
        v, best = -INF, None
        for a in game.actions(s):
            v2, _ = min_value(game.result(s, a))
            if v2 > v:
                v, best = v2, a
        return v, best

    def min_value(s):
        stats["nodes"] += 1
        if game.terminal(s):
            return game.utility(s, me), None
        v, best = INF, None
        for a in game.actions(s):
            v2, _ = max_value(game.result(s, a))
            if v2 < v:
                v, best = v2, a
        return v, best

    _, action = max_value(state)
    return action, stats


def alphabeta(game, state):
    stats = {"nodes": 0}
    me = game.to_move(state)

    def max_value(s, alpha, beta):
        stats["nodes"] += 1
        if game.terminal(s):
            return game.utility(s, me), None
        v, best = -INF, None
        for a in game.actions(s):
            v2, _ = min_value(game.result(s, a), alpha, beta)
            if v2 > v:
                v, best = v2, a
                alpha = max(alpha, v)
            if v >= beta:
                return v, best
        return v, best

    def min_value(s, alpha, beta):
        stats["nodes"] += 1
        if game.terminal(s):
            return game.utility(s, me), None
        v, best = INF, None
        for a in game.actions(s):
            v2, _ = max_value(game.result(s, a), alpha, beta)
            if v2 < v:
                v, best = v2, a
                beta = min(beta, v)
            if v <= alpha:
                return v, best
        return v, best

    _, action = max_value(state, -INF, INF)
    return action, stats


def heuristic_alphabeta(game, state, depth=4, eval_fn=None):
    if eval_fn is None:
        eval_fn = getattr(game, "heuristic", None)
        if eval_fn is None:
            raise ValueError("need an eval_fn or game.heuristic")

    stats = {"nodes": 0, "cutoffs": 0}
    me = game.to_move(state)

    def ordered_actions(s, maximising):
        scored = []
        for a in game.actions(s):
            child = game.result(s, a)
            if game.terminal(child):
                scored.append((game.utility(child, me) * 10000, a))
            else:
                scored.append((eval_fn(child, me), a))
        scored.sort(reverse=maximising)
        return [a for _, a in scored]

    def max_value(s, alpha, beta, d):
        stats["nodes"] += 1
        if game.terminal(s):
            return game.utility(s, me) * 10000, None
        if d == 0:
            return eval_fn(s, me), None
        v, best = -INF, None
        for a in ordered_actions(s, True):
            v2, _ = min_value(game.result(s, a), alpha, beta, d - 1)
            if v2 > v:
                v, best = v2, a
                alpha = max(alpha, v)
            if v >= beta:
                stats["cutoffs"] += 1
                return v, best
        return v, best

    def min_value(s, alpha, beta, d):
        stats["nodes"] += 1
        if game.terminal(s):
            return game.utility(s, me) * 10000, None
        if d == 0:
            return eval_fn(s, me), None
        v, best = INF, None
        for a in ordered_actions(s, False):
            v2, _ = max_value(game.result(s, a), alpha, beta, d - 1)
            if v2 < v:
                v, best = v2, a
                beta = min(beta, v)
            if v <= alpha:
                stats["cutoffs"] += 1
                return v, best
        return v, best

    _, action = max_value(state, -INF, INF, depth)
    return action, stats


class _Node:
    __slots__ = ("state", "parent", "action", "children",
                 "untried", "visits", "wins", "to_move")

    def __init__(self, state, parent, action, game):
        self.state = state
        self.parent = parent
        self.action = action
        self.children = []
        self.untried = list(game.actions(state))
        random.shuffle(self.untried)
        self.visits = 0
        self.wins = 0.0
        self.to_move = game.to_move(state)

    def is_fully_expanded(self):
        return not self.untried

    def best_child(self, c):
        log_n = math.log(self.visits)
        best, best_score = None, -INF
        for ch in self.children:
            exploit = ch.wins / ch.visits
            explore = c * math.sqrt(log_n / ch.visits)
            score = exploit + explore
            if score > best_score:
                best_score, best = score, ch
        return best


def mcts(game, state, iterations=1000, time_limit=None,
         c=math.sqrt(2), rollout_policy=None):
    if rollout_policy is None:
        def rollout_policy(g, s):
            return random.choice(g.actions(s))

    root_player = game.to_move(state)
    root = _Node(state, None, None, game)
    stats = {"nodes": 1, "rollouts": 0}

    def tree_policy(node):
        while not game.terminal(node.state):
            if not node.is_fully_expanded():
                a = node.untried.pop()
                child = _Node(game.result(node.state, a), node, a, game)
                node.children.append(child)
                stats["nodes"] += 1
                return child
            node = node.best_child(c)
        return node

    def default_policy(s):
        while not game.terminal(s):
            s = game.result(s, rollout_policy(game, s))
        return game.utility(s, root_player)

    def backup(node, reward):
        # flip sign at opponent nodes so their best-child = our worst-case
        while node is not None:
            node.visits += 1
            if node.parent is not None:
                mover = node.parent.to_move
                node.wins += reward if mover == root_player else -reward
            else:
                node.wins += reward
            node = node.parent

    start = time.time()
    i = 0
    while True:
        if time_limit is not None:
            if time.time() - start >= time_limit:
                break
        elif i >= iterations:
            break
        leaf = tree_policy(root)
        reward = default_policy(leaf.state)
        backup(leaf, reward)
        stats["rollouts"] += 1
        i += 1

    if not root.children:
        return None, stats

    best = max(root.children, key=lambda ch: ch.visits)
    stats["root_children"] = [
        (ch.action, ch.visits, round(ch.wins / max(ch.visits, 1), 3))
        for ch in root.children
    ]
    return best.action, stats
