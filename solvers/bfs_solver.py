import copy
import time
from collections import deque

directions = {
    "up": (-1, 0),
    "down": (1, 0),
    "left": (0, -1),
    "right": (0, 1),
}  # Hướng di chuyển trong ma trận


class Node:
    def __init__(self, matrix, flows, parent=None, move=None, depth=0):
        self.matrix = matrix  # Ma trận hiện tại
        self.flows = flows  # Vị trí hiện tại từng luồng màu
        self.parent = parent  # Node cha
        self.move = move  # Di chuyển từ node cha đến node này
        self.depth = depth  # Độ sâu của node trong cây tìm kiếm


# Mã hóa trạng thái của ma trận và luồng màu
def encode_state(matrix, flows):
    parts = []
    for row in matrix:
        for cell in row:
            parts.append(cell if cell else ".")
    for color, pos in sorted(flows.items()):
        parts.append(f"{color}{pos[0]}{pos[1]}")
    return "".join(parts)


# Kiểm tra xem node hiện tại có phải là trạng thái mục tiêu không
def is_goal(node, start_goals):
    for color, (_, goal) in start_goals.items():
        if node.flows[color] != goal:
            return False
    return all(cell is not None for row in node.matrix for cell in row)


# Lấy các ô lân cận của ô (r, c)
def get_neighbors(r, c, ROWS, COLS):
    return [
        (r + dr, c + dc)
        for dr, dc in directions.values()
        if 0 <= r + dr < ROWS and 0 <= c + dc < COLS
    ]


# Di chuyển luồng màu từ vị trí hiện tại đến vị trí mới
def move_flow(matrix, flows, color, direction):
    r, c = flows[color]
    dr, dc = directions[direction]
    nr, nc = r + dr, c + dc
    new_matrix = copy.deepcopy(matrix)
    new_flows = flows.copy()
    new_matrix[nr][nc] = color
    new_flows[color] = (nr, nc)
    return new_matrix, new_flows


# Hàm này dùng để lấy đường đi từ node hiện tại về node gốc
def reconstruct_path(node):
    path = []
    while node.parent:
        path.append(node.move)
        node = node.parent
    return path[::-1]


# Hàm này dùng để lấy thứ tự ưu tiên di chuyển cho các luồng màu
def color_priority(matrix, flows, goals, ROWS, COLS):
    result = []
    for color, pos in flows.items():
        if pos == goals[color]:
            continue
        dist = abs(pos[0] - goals[color][0]) + abs(pos[1] - goals[color][1])
        neighbors = sum(
            1
            for nr, nc in get_neighbors(pos[0], pos[1], ROWS, COLS)
            if matrix[nr][nc] is None  # Đếm số ô trống xung quanh vị trí hiện tại
        )
        result.append(
            (dist - neighbors, color)
        )  # Sắp xếp theo khoảng cách và số ô trống
    result.sort()  # Ưu tiên các màu vừa gần goal vừa dễ bị kẹt.
    return [color for _, color in result]


# Giải bài toán bằng thuật toán BFS với giới hạn số node mở rộng là max_nodes
def solve_bfs(start_goals, ROWS, COLS, max_nodes=1000000):
    start_time = time.time()
    matrix = [[None for _ in range(COLS)] for _ in range(ROWS)]  # Ma trận ban đầu
    flows = {}  # Vị trí hiện tại của từng luồng màu
    goal_positions = {}  # Vị trí mục tiêu của từng luồng màu

    # Khởi tạo ma trận và vị trí luồng màu
    for color, (start, goal) in start_goals.items():
        matrix[start[0]][start[1]] = color
        matrix[goal[0]][goal[1]] = color
        flows[color] = start
        goal_positions[color] = goal

    # Khởi tạo node bắt đầu
    start_node = Node(matrix, flows)
    queue = deque([start_node])
    visited = set([encode_state(matrix, flows)])

    # Khởi tạo các biến đếm
    nodes_generated = 1
    nodes_expanded = 0
    max_depth = 0

    while queue:
        if nodes_expanded >= max_nodes:
            print(f"BFS: Vượt quá giới hạn mở rộng {max_nodes} node.")
            break

        node = queue.popleft()
        nodes_expanded += 1

        if is_goal(node, start_goals):
            time_used = time.time() - start_time
            return (
                reconstruct_path(node),
                time_used,
                nodes_generated,
                nodes_expanded,
                max_depth,
            )

        for color in color_priority(
            node.matrix, node.flows, goal_positions, ROWS, COLS
        ):
            r, c = node.flows[color]
            goal = goal_positions[color]

            for dir_name, (dr, dc) in directions.items():
                nr, nc = r + dr, c + dc
                if not (0 <= nr < ROWS and 0 <= nc < COLS):
                    continue
                if (nr, nc) in [
                    goal_positions[c2] for c2 in start_goals if c2 != color
                ]:
                    continue

                target = node.matrix[nr][nc]
                if target is None or (nr, nc) == goal:
                    new_matrix, new_flows = move_flow(
                        node.matrix, node.flows, color, dir_name
                    )
                    state_key = encode_state(new_matrix, new_flows)

                    if state_key in visited:
                        continue

                    visited.add(state_key)

                    child = Node(
                        new_matrix,
                        new_flows,
                        parent=node,
                        move=(color, dir_name),
                        depth=node.depth + 1,
                    )

                    max_depth = max(max_depth, child.depth)

                    queue.append(child)
                    nodes_generated += 1

    return None, None, nodes_generated, nodes_expanded, max_depth
