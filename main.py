import pygame
import sys
import time
import threading
from select_map import select_map
from map_data import maps
from solvers.astar_solver import solve_astar
from solvers.bfs_solver import solve_bfs
from solvers.csp_solver import solve_csp
from solvers.sa_solver import solve_sa

# ==== Select Map + Settings ====
size, map_number, algorithm = select_map()
start_goals = maps[size][map_number]
ROWS = COLS = int(size)

print(f"Selected: Size = {size}, Map = {map_number}, Algorithm = {algorithm}")

# ==== Pygame Setup ====
pygame.init()
WIDTH, HEIGHT = 600, 600
CELL_SIZE = WIDTH // COLS
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flow Free Solver")

# ==== Global ====
solving_done = False
path = None

directions = {"up": (-1, 0), "down": (1, 0), "left": (0, -1), "right": (0, 1)}
color_map = {
    "Y": (255, 255, 0),
    "B": (0, 0, 255),
    "G": (0, 255, 0),
    "R": (255, 0, 0),
    "O": (255, 165, 0),
    "P": (128, 0, 128),
    "C": (0, 255, 255),
    "M": (255, 0, 255),
    "A": (139, 69, 19),
    "S": (192, 192, 192),
}


def center_of(pos):
    row, col = pos
    return (col * CELL_SIZE + CELL_SIZE // 2, row * CELL_SIZE + CELL_SIZE // 2)


def draw_board(screen, visited):
    screen.fill((0, 0, 0))
    for row in range(ROWS):
        for col in range(COLS):
            rect = pygame.Rect(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, (50, 50, 50), rect, 1)
            if visited[row][col]:
                s = pygame.Surface((CELL_SIZE, CELL_SIZE))
                s.set_alpha(70)
                s.fill(color_map[visited[row][col]])
                screen.blit(s, rect.topleft)


def draw_flows(screen, flows_path):
    for color, positions in flows_path.items():
        if len(positions) >= 2:
            points = [center_of(p) for p in positions]
            pygame.draw.lines(screen, color_map[color], False, points, width=30)
            pygame.draw.lines(screen, color_map[color], False, points, width=20)
        if positions:
            pygame.draw.circle(
                screen, color_map[color], center_of(positions[0]), CELL_SIZE // 3
            )
        goal_pos = start_goals[color][1]
        pygame.draw.circle(
            screen, color_map[color], center_of(goal_pos), CELL_SIZE // 3
        )


def draw_loading_text():
    font = pygame.font.SysFont(None, 48)
    text = font.render("Solving...", True, (255, 255, 255))
    rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(text, rect)


def draw_start_goal_only():
    for color in start_goals:
        start_pos = start_goals[color][0]
        goal_pos = start_goals[color][1]
        pygame.draw.circle(
            screen, color_map[color], center_of(start_pos), CELL_SIZE // 3
        )
        pygame.draw.circle(
            screen, color_map[color], center_of(goal_pos), CELL_SIZE // 3
        )


def animate_solution(path):
    matrix = [[None for _ in range(COLS)] for _ in range(ROWS)]
    flows = {}
    for color, (start, _) in start_goals.items():
        r, c = start
        matrix[r][c] = color
        flows[color] = (r, c)

    flows_path = {color: [pos] for color, pos in flows.items()}
    visited = [[None for _ in range(COLS)] for _ in range(ROWS)]

    running = True
    idx = 0
    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        draw_board(screen, visited)

        if idx < len(path):
            color, direction = path[idx]
            r, c = flows[color]
            dr, dc = directions[direction]
            nr, nc = r + dr, c + dc
            flows[color] = (nr, nc)
            flows_path[color].append((nr, nc))
            visited[nr][nc] = color
            idx += 1

        draw_flows(screen, flows_path)
        pygame.display.update()
        clock.tick(10)

    pygame.quit()
    sys.exit()


def draw_no_solution_text():
    font = pygame.font.SysFont(None, 50)
    text = font.render("No solution found!", True, (255, 0, 0))
    rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(text, rect)


# ==== Thread Run ====
def solver_thread_fn():
    global path, solving_done

    result = None
    if algorithm == "A*":
        result = solve_astar(start_goals, ROWS, COLS)
    elif algorithm == "BFS":
        result = solve_bfs(start_goals, ROWS, COLS)
    elif algorithm == "CSP":
        result = solve_csp(start_goals, ROWS, COLS)
    elif algorithm == "SA":
        result = solve_sa(start_goals, ROWS, COLS)

    if result:
        path, time_used, nodes_generated, nodes_expanded, max_depth = result
        if path:
            print(f"Solved using algorithm: {algorithm}")
            print(f"Number of steps to goal: {len(path)}")
            print(f"Time taken: {time_used:.4f} seconds")
            if nodes_generated is not None:
                print(f"Nodes generated: {nodes_generated}")
            if nodes_expanded is not None:
                print(f"Nodes expanded: {nodes_expanded}")
            if max_depth is not None:
                print(f"Maximum depth reached: {max_depth}")
        else:
            print(f"{algorithm}: Không tìm thấy lời giải.")
    else:
        print(f"{algorithm}: Solver chưa được triển khai.")

    solving_done = True


# ==== Main Run ====
draw_board(screen, [[None for _ in range(COLS)] for _ in range(ROWS)])
draw_start_goal_only()
pygame.display.update()
time.sleep(1)

solver_thread = threading.Thread(target=solver_thread_fn)
solver_thread.start()

running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if solving_done:
        if path is not None:
            animate_solution(path)
            running = False
        else:
            draw_board(screen, [[None for _ in range(COLS)] for _ in range(ROWS)])
            draw_start_goal_only()
            draw_no_solution_text()
    else:
        draw_board(screen, [[None for _ in range(COLS)] for _ in range(ROWS)])
        draw_loading_text()

    pygame.display.update()
    clock.tick(60)

pygame.quit()
