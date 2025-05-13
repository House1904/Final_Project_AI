import pygame
import pygame_menu
from pygame_menu.widgets import HighlightSelection
from map_data import maps

pygame.init()

# ==== Global Variables ====
size = "5"
map_number = 1
algorithm = "A*"

available_sizes = list(maps.keys())


def set_algorithm(selected, value):
    global algorithm
    algorithm = value


def set_size(selected, value):
    global size
    size = value


def set_map(selected, value):
    global map_number
    map_number = value


def start_game():
    global menu_running
    menu_running = False  # Đóng menu


# ==== Pygame Window ====
surface = pygame.display.set_mode((600, 500))
pygame.display.set_caption("Select Flow Free Map")

# ==== Theme ====
theme = pygame_menu.themes.Theme(
    background_color=(30, 30, 30),
    title_background_color=(50, 50, 50),
    title_font_shadow=True,
    title_font_size=60,
    widget_font=pygame_menu.font.FONT_FRANCHISE,
    widget_font_size=40,
    widget_font_color=(220, 220, 220),
    selection_color=(255, 153, 51),
    widget_selection_effect=HighlightSelection(
        border_width=4, margin_x=15, margin_y=15
    ),
)
theme.widget_background_color = (70, 70, 70)
theme.widget_background_color_selected = (100, 100, 255)

# ==== Menu ====
menu = pygame_menu.Menu("Select Map", 600, 500, theme=theme)

menu.add.selector("Size   :", [(s, s) for s in available_sizes], onchange=set_size)
menu.add.selector("Map    :", [(str(i), i) for i in range(1, 11)], onchange=set_map)
menu.add.selector(
    "Solver :",
    [
        ("A*", "A*"),
        ("BFS", "BFS"),
        ("CSP", "CSP"),
        ("SA", "SA"),
    ],
    onchange=set_algorithm,
)

menu.add.button("Start", start_game)
menu.add.button("Exit", pygame_menu.events.EXIT)

menu_running = True


def select_map():
    global menu_running
    while menu_running:
        surface.fill((0, 0, 0))
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                exit()
        menu.update(events)
        menu.draw(surface)
        pygame.display.update()

    pygame.quit()
    return size, map_number, algorithm


if __name__ == "__main__":
    s, m, algo = select_map()
    print(f"Selected: Size={s}, Map={m}, Algorithm={algo}")
