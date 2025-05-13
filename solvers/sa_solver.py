import copy
import random
import math
import time
from collections import deque

directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]


def is_inside(r, c, ROWS, COLS):
    return 0 <= r < ROWS and 0 <= c < COLS


def get_neighbors(pos, ROWS, COLS):
    r, c = pos
    return [
        (r + dr, c + dc)
        for dr, dc in directions
        if is_inside(r + dr, c + dc, ROWS, COLS)
    ]


def random_path(start, goal, ROWS, COLS):
    """Sinh path ngẫu nhiên từ start đến goal"""
    queue = deque([(start, [start])])
    visited = set()
    while queue:
        curr, path = queue.popleft()
        if curr == goal:
            return path
        visited.add(curr)
        random.shuffle(directions)
        for dr, dc in directions:
            nr, nc = curr[0] + dr, curr[1] + dc
            next_pos = (nr, nc)
            if (
                is_inside(nr, nc, ROWS, COLS)
                and next_pos not in visited
                and next_pos not in path
            ):
                queue.append((next_pos, path + [next_pos]))
    return None


def random_assignment(start_goals, ROWS, COLS):
    assignment = {}
    for color, (start, goal) in start_goals.items():
        path = random_path(start, goal, ROWS, COLS)
        if path:
            assignment[color] = path
    return assignment


def conflicts(assignment):
    seen = set()
    conflict = 0
    for path in assignment.values():
        for cell in path:
            if cell in seen:
                conflict += 1
            seen.add(cell)
    return conflict


def cost(assignment, ROWS, COLS):
    total = conflicts(assignment)
    # penalty cho ô chưa đi qua
    covered = set(cell for path in assignment.values() for cell in path)
    empty_cells = ROWS * COLS - len(covered)
    return total + empty_cells


def neighbor(assignment, start_goals, ROWS, COLS):
    """Tạo lân cận bằng cách đổi lại 1 path"""
    new_assignment = copy.deepcopy(assignment)
    color = random.choice(list(assignment.keys()))
    new_path = random_path(start_goals[color][0], start_goals[color][1], ROWS, COLS)
    if new_path:
        new_assignment[color] = new_path
    return new_assignment


def convert_to_moves(assignment):
    result = []
    for color, path in assignment.items():
        for i in range(1, len(path)):
            prev = path[i - 1]
            curr = path[i]
            dr, dc = curr[0] - prev[0], curr[1] - prev[1]
            if dr == -1:
                move = "up"
            elif dr == 1:
                move = "down"
            elif dc == -1:
                move = "left"
            elif dc == 1:
                move = "right"
            result.append((color, move))
    return result


def solve_sa(
    start_goals, ROWS=5, COLS=5, Tmax=700.0, Tmin=0.005, alpha=0.95, iter_per_temp=1500
):

    start_time = time.time()
    current = random_assignment(start_goals, ROWS, COLS)
    if not current:
        return None, None, None, None, None

    current_cost = cost(current, ROWS, COLS)
    best = current
    best_cost = current_cost
    T = Tmax

    while T > Tmin:
        for _ in range(iter_per_temp):
            next_state = neighbor(current, start_goals, ROWS, COLS)
            next_cost = cost(next_state, ROWS, COLS)
            delta = next_cost - current_cost
            if delta < 0 or random.random() < math.exp(-delta / T):
                current = next_state
                current_cost = next_cost
                if current_cost < best_cost:
                    best = current
                    best_cost = current_cost
                    if best_cost == 0:
                        steps = convert_to_moves(best)
                        return steps, time.time() - start_time, None, None, None
        T *= alpha

    if best_cost == 0:
        steps = convert_to_moves(best)
        return steps, time.time() - start_time, None, None, None
    return None, None, None, None, None
