import time
from collections import defaultdict

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


def find_all_paths(start, goal, matrix, color, ROWS, COLS, max_length=20):
    paths = []
    stack = [(start, [start])]
    while stack:
        (r, c), path = stack.pop()
        if len(path) > max_length:
            continue
        if (r, c) == goal:
            paths.append(path)
            continue
        for nr, nc in get_neighbors((r, c), ROWS, COLS):
            if (matrix[nr][nc] is None or (nr, nc) == goal) and (nr, nc) not in path:
                stack.append(((nr, nc), path + [(nr, nc)]))
    return paths


def paths_conflict(p1, p2):
    return any(cell in p2 for cell in p1)


def compute_degrees(start_goals, ROWS, COLS):
    color_neighbors = defaultdict(set)
    color_positions = {c: [start, goal] for c, (start, goal) in start_goals.items()}
    for c1, positions1 in color_positions.items():
        for c2, positions2 in color_positions.items():
            if c1 == c2:
                continue
            for p1 in positions1:
                for p2 in positions2:
                    if abs(p1[0] - p2[0]) + abs(p1[1] - p2[1]) == 1:
                        color_neighbors[c1].add(c2)
    return {c: len(neigh) for c, neigh in color_neighbors.items()}


def order_colors(domains, degrees):
    return sorted(
        domains.keys(), key=lambda c: (len(domains[c]), -degrees.get(c, 0))
    )  # MRV + Degree


def order_paths(color, domains, remaining_colors):
    # LCV: path ít xung đột với các path còn lại
    paths = domains[color]
    score_path_pairs = []
    for path in paths:
        score = 0
        for other in remaining_colors:
            for other_path in domains[other]:
                if paths_conflict(path[1:], other_path[1:]):
                    score += 1
        score_path_pairs.append((score, path))
    score_path_pairs.sort()
    return [p for _, p in score_path_pairs]


def forward_check(domains, color, selected_path):
    new_domains = {}
    for other_color in domains:
        if other_color == color:
            continue
        new_list = [
            p
            for p in domains[other_color]
            if not paths_conflict(selected_path[1:], p[1:])
        ]
        if not new_list:
            return None  # fail early
        new_domains[other_color] = new_list
    return new_domains


def validate_fill(assignments, ROWS, COLS):
    grid = [[None for _ in range(COLS)] for _ in range(ROWS)]
    for color, path in assignments.items():
        for r, c in path:
            if grid[r][c] is not None:
                return False
            grid[r][c] = color

    for r in range(ROWS):
        for c in range(COLS):
            if grid[r][c] is None:
                return False
    return True


def backtrack(assignments, domains, colors, index, start_goals, ROWS, COLS):
    if index == len(colors):
        return validate_fill(assignments, ROWS, COLS)

    color = colors[index]
    remaining_colors = colors[index + 1 :]
    ordered_paths = order_paths(color, domains, remaining_colors)

    for path in ordered_paths:
        assignments[color] = path
        new_domains = forward_check(domains, color, path)
        if new_domains is not None:
            new_domains[color] = [path]  # fix current
            if backtrack(
                assignments, new_domains, colors, index + 1, start_goals, ROWS, COLS
            ):
                return True
        del assignments[color]

    return False


def direction_from(p1, p2):
    dr = p2[0] - p1[0]
    dc = p2[1] - p1[1]
    if dr == -1:
        return "up"
    if dr == 1:
        return "down"
    if dc == -1:
        return "left"
    if dc == 1:
        return "right"
    return ""


def convert_paths_to_moves(assignments):
    result = []
    for color, path in assignments.items():
        prev = path[0]
        for curr in path[1:]:
            result.append((color, direction_from(prev, curr)))
            prev = curr
    return result


def solve_csp(start_goals, ROWS, COLS):
    matrix = [[None for _ in range(COLS)] for _ in range(ROWS)]
    for color, (start, goal) in start_goals.items():
        matrix[start[0]][start[1]] = color
        matrix[goal[0]][goal[1]] = color

    start_time = time.time()
    domains = {}
    for color, (start, goal) in start_goals.items():
        paths = find_all_paths(
            start, goal, matrix, color, ROWS, COLS, max_length=ROWS * COLS
        )
        if not paths:
            return None, None, None, None, None
        domains[color] = paths

    degrees = compute_degrees(start_goals, ROWS, COLS)
    colors = order_colors(domains, degrees)

    assignments = {}
    success = backtrack(assignments, domains, colors, 0, start_goals, ROWS, COLS)

    if success:
        time_used = time.time() - start_time
        path = convert_paths_to_moves(assignments)
        return path, time_used, None, None, None

    return None, None, None, None, None
