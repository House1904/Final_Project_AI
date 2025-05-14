import copy
import heapq
import time

directions = {
    "up": (-1, 0),
    "down": (1, 0),
    "left": (0, -1),
    "right": (0, 1),
}  # Hướng di chuyển trong ma trận


class Node:
    def __init__(self, matrix, flows, parent=None, move=None, cost=0):
        self.matrix = matrix  # Ma trận hiện tại
        self.flows = flows  # Vị trí hiện tại từng luồng màu
        self.parent = parent  # Node cha
        self.move = move  # Di chuyển từ node cha đến node này
        self.cost = cost  # Chi phí từ node cha đến node này
        self.f = 0  # Tổng chi phí (g + h)

    def __lt__(self, other):  # So sánh hai node dựa trên chi phí f
        return self.f < other.f


# Mã hóa trạng thái của ma trận và luồng màu
def encode_state(matrix, flows):
    m_str = "".join(cell if cell else "." for row in matrix for cell in row)
    f_str = "".join(f"{c}{r}{col}" for c, (r, col) in sorted(flows.items()))
    return m_str + f_str


# Kiểm tra xem node hiện tại có phải là trạng thái mục tiêu không?
def is_goal(node):
    return all(cell is not None for row in node.matrix for cell in row)


# Kiểm tra xem luồng color có thể đi direction không?
def can_move(node, color, direction, ROWS, COLS, start_goals):
    r, c = node.flows[color]
    dr, dc = directions[direction]
    nr, nc = r + dr, c + dc
    if 0 <= nr < ROWS and 0 <= nc < COLS:
        target = node.matrix[nr][nc]
        if target is None or (target == color and (nr, nc) == start_goals[color][1]):
            return True
    return False


# Tạo một ma trận mới và cập nhật vị trí của luồng color khi đi theo direction.
def move_flow(matrix, flows, color, direction):
    r, c = flows[color]
    dr, dc = directions[direction]
    nr, nc = r + dr, c + dc
    new_matrix = copy.deepcopy(matrix)
    new_flows = flows.copy()
    new_matrix[nr][nc] = color
    new_flows[color] = (nr, nc)
    return new_matrix, new_flows


# Kiểm tra tồn tại đường đi từ start đến goal
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


# Phát hiện xem có bị mắc kẹt không?
def detect_dead_end(node, start_goals, ROWS, COLS):
    for color in start_goals:
        r, c = node.flows[color]
        goal_r, goal_c = start_goals[color][1]
        if not path_exists(node.matrix, (r, c), (goal_r, goal_c), color, ROWS, COLS):
            return True
    return False


# Đếm số hướng có thể đi cho một luồng
def count_valid_moves(node, color, ROWS, COLS, start_goals):
    return sum(
        1 for d in directions if can_move(node, color, d, ROWS, COLS, start_goals)
    )


# Hàm này dùng để chọn luồng màu nào sẽ di chuyển tiếp theo
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


# Hàm này dùng để tạo ra các node con từ node hiện tại
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


# Hàm đánh giá h(n): tổng khoảng cách Manhattan từ vị trí hiện tại đến đích của từng luồng
def heuristic(node, start_goals):
    return sum(
        abs(goal[0] - pos[0]) + abs(goal[1] - pos[1])
        for color, pos in node.flows.items()
        for goal in [start_goals[color][1]]
    )


# Hàm này dùng để lấy đường đi từ node hiện tại về node gốc
def reconstruct_path(node):
    path = []
    while node.parent:
        path.append(node.move)
        node = node.parent
    path.reverse()
    return path


# Giải thuật chính A*
def solve_astar(start_goals, ROWS, COLS):
    matrix = [[None for _ in range(COLS)] for _ in range(ROWS)]  # Ma trận ban đầu
    flows = {}  # Vị trí hiện tại của từng luồng màu
    # Khởi tạo ma trận và vị trí luồng màu
    for color, (start, _) in start_goals.items():
        r, c = start
        matrix[r][c] = color
        flows[color] = (r, c)

    start_node = Node(matrix, flows)  # Khởi tạo node bắt đầu
    open_list = []  # Danh sách mở
    heapq.heappush(
        open_list, (start_node.f, start_node)  # (f, node)
    )  # Thêm node bắt đầu vào danh sách mở
    state_cost = {}  # Từ điển lưu trữ chi phí của các trạng thái đã duyệt

    # Khởi tạo các biến đếm
    nodes_generated = 0
    nodes_expanded = 0
    max_depth = 0
    start_time = time.time()

    # Duyệt qua danh sách mở
    while open_list:
        _, current = heapq.heappop(open_list)
        nodes_expanded += 1
        max_depth = max(max_depth, current.cost)

        # Kiểm tra đã đến đích chưa?
        if is_goal(current):
            end_time = time.time()
            return (
                reconstruct_path(current),
                end_time - start_time,
                nodes_generated,
                nodes_expanded,
                max_depth,
            )

        # Mã hóa trạng thái hiện tại
        current_state = encode_state(current.matrix, current.flows)
        # Kiểm tra trạng thái đã được duyệt chưa và chi phí có thấp hơn không?
        if current_state in state_cost and state_cost[current_state] <= current.cost:
            continue
        # Cập nhật chi phí của trạng thái hiện tại
        state_cost[current_state] = current.cost

        # Tạo các node con từ node hiện tại và duyệt chúng
        for child in generate_successors(current, start_goals, ROWS, COLS):
            nodes_generated += 1
            child_state = encode_state(child.matrix, child.flows)
            if child_state in state_cost and state_cost[child_state] <= child.cost:
                continue
            # Tính toán chi phí f = g + h
            child.f = child.cost + heuristic(child, start_goals)
            # Thêm node con vào danh sách mở
            heapq.heappush(open_list, (child.f, child))

    return None, None, nodes_generated, nodes_expanded, max_depth
