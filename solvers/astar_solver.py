import copy
import heapq
import time

directions = {"up": (-1, 0), "down": (1, 0), "left": (0, -1), "right": (0, 1)}


class Node:
    def __init__(self, matrix, flows, parent=None, move=None, cost=0):
        self.matrix = matrix
        self.flows = flows
        self.parent = parent
        self.move = move
        self.cost = cost
        self.f = 0

    def __lt__(self, other):
        return self.f < other.f


def encode_state(matrix, flows):
    m_str = "".join(cell if cell else "." for row in matrix for cell in row)
    f_str = "".join(f"{c}{r}{col}" for c, (r, col) in sorted(flows.items()))
    return m_str + f_str


def is_goal(node):
    return all(cell is not None for row in node.matrix for cell in row)


def can_move(node, color, direction, ROWS, COLS, start_goals):
    r, c = node.flows[color]
    dr, dc = directions[direction]
    nr, nc = r + dr, c + dc
    if 0 <= nr < ROWS and 0 <= nc < COLS:
        target = node.matrix[nr][nc]
        if target is None or (target == color and (nr, nc) == start_goals[color][1]):
            return True
    return False


def move_flow(matrix, flows, color, direction):
    r, c = flows[color]
    dr, dc = directions[direction]
    nr, nc = r + dr, c + dc
    new_matrix = copy.deepcopy(matrix)
    new_flows = flows.copy()
    new_matrix[nr][nc] = color
    new_flows[color] = (nr, nc)
    return new_matrix, new_flows


def path_exists(matrix, start, goal, color, ROWS, COLS):
    queue = [start]
    visited = set()
    while queue:
        r, c = queue.pop()
        if (r, c) == goal:
            return True
        visited.add((r, c))
        for dr, dc in directions.values():
            nr, nc = r + dr, c + dc
            if 0 <= nr < ROWS and 0 <= nc < COLS:
                if (matrix[nr][nc] is None or (nr, nc) == goal) and (
                    nr,
                    nc,
                ) not in visited:
                    queue.append((nr, nc))
    return False


def detect_dead_end(node, start_goals, ROWS, COLS):
    for color in start_goals:
        r, c = node.flows[color]
        goal_r, goal_c = start_goals[color][1]
        if not path_exists(node.matrix, (r, c), (goal_r, goal_c), color, ROWS, COLS):
            return True
    return False


def count_valid_moves(node, color, ROWS, COLS, start_goals):
    return sum(
        1 for d in directions if can_move(node, color, d, ROWS, COLS, start_goals)
    )


def choose_flow(node, start_goals, ROWS, COLS):
    best_color = None
    best_score = float("inf")
    for color in start_goals:
        if node.flows[color] != start_goals[color][1]:
            moves = count_valid_moves(node, color, ROWS, COLS, start_goals)
            goal = start_goals[color][1]
            pos = node.flows[color]
            dist = abs(goal[0] - pos[0]) + abs(goal[1] - pos[1])
            score = moves + dist
            if score < best_score:
                best_score = score
                best_color = color
    return best_color


def generate_successors(node, start_goals, ROWS, COLS):
    successors = []
    color = choose_flow(node, start_goals, ROWS, COLS)
    if color is None:
        return []
    for direction in directions:
        if can_move(node, color, direction, ROWS, COLS, start_goals):
            new_matrix, new_flows = move_flow(node.matrix, node.flows, color, direction)
            child = Node(
                new_matrix,
                new_flows,
                parent=node,
                move=(color, direction),
                cost=node.cost + 1,
            )
            if not detect_dead_end(child, start_goals, ROWS, COLS):
                successors.append(child)
    return successors


def heuristic(node, start_goals):
    return sum(
        abs(goal[0] - pos[0]) + abs(goal[1] - pos[1])
        for color, pos in node.flows.items()
        for goal in [start_goals[color][1]]
    )


def reconstruct_path(node):
    path = []
    while node.parent:
        path.append(node.move)
        node = node.parent
    path.reverse()
    return path


def solve_astar(start_goals, ROWS, COLS):
    matrix = [[None for _ in range(COLS)] for _ in range(ROWS)]
    flows = {}
    for color, (start, _) in start_goals.items():
        r, c = start
        matrix[r][c] = color
        flows[color] = (r, c)

    start_node = Node(matrix, flows)
    open_list = []
    heapq.heappush(open_list, (start_node.f, start_node))
    state_cost = {}

    nodes_generated = 0
    nodes_expanded = 0
    max_depth = 0
    start_time = time.time()

    while open_list:
        _, current = heapq.heappop(open_list)
        nodes_expanded += 1
        max_depth = max(max_depth, current.cost)

        if is_goal(current):
            end_time = time.time()
            return (
                reconstruct_path(current),
                end_time - start_time,
                nodes_generated,
                nodes_expanded,
                max_depth,
            )

        current_state = encode_state(current.matrix, current.flows)
        if current_state in state_cost and state_cost[current_state] <= current.cost:
            continue
        state_cost[current_state] = current.cost

        for child in generate_successors(current, start_goals, ROWS, COLS):
            nodes_generated += 1
            child_state = encode_state(child.matrix, child.flows)
            if child_state in state_cost and state_cost[child_state] <= child.cost:
                continue
            child.f = child.cost + heuristic(child, start_goals)
            heapq.heappush(open_list, (child.f, child))

    return None, None, nodes_generated, nodes_expanded, max_depth
