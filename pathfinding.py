import pygame
import os
import json
from tkinter import filedialog
import datetime
import time

class Cube:
    def __init__(self, color="white", traversable=True):
        self.color = color
        self.traversable = traversable


class Grid:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.grid = [[Cube() for _ in range(cols)] for _ in range(rows)]
        self.start_cube = None
        self.goal_cube = None

    def draw_cube(self, screen, x, y, cube_size, offset_x, offset_y):
        cube = self.grid[y][x]
        # inside cell
        if cube.color != "white":
            pygame.draw.rect(screen, cube.color, (offset_x + x * cube_size, offset_y + y * cube_size, cube_size, cube_size))
        # outline of cell
        pygame.draw.rect(screen, "black", (offset_x + x * cube_size, offset_y + y * cube_size, cube_size, cube_size), 1)

    def center_grid(self, window_width, window_height, cube_size):
        grid_width = self.cols * cube_size
        grid_height = self.rows * cube_size
        offset_x = (window_width - grid_width) // 2
        offset_y = (window_height - grid_height) // 2
        return offset_x, offset_y

    def handle_click(self, x, y, cube_size, offset_x, offset_y, selected_tool):
        grid_x = (x - offset_x) // cube_size
        grid_y = (y - offset_y) // cube_size
        print(f"x: {x} y: {y} grid_x: {grid_x} grid_y: {grid_y} selected_tool: {selected_tool}")
        if 0 <= grid_x < self.cols and 0 <= grid_y < self.rows:
            cube = self.grid[grid_y][grid_x]
            if selected_tool == 0:
                if self.start_cube:
                    old_x, old_y = self.start_cube
                    self.grid[old_y][old_x].color = "white"
                self.start_cube = grid_x,grid_y
                cube.color = "green"
            elif selected_tool == 1:
                if self.goal_cube:
                    old_x, old_y = self.goal_cube
                    self.grid[old_y][old_x].color = "white"
                self.goal_cube = grid_x,grid_y
                cube.color = "red"
            elif selected_tool == 2:
                cube.color = "grey"
                cube.traversable = False

    def export_grid(self, filename):
        data = {
            "rows": self.rows,
            "cols": self.cols,
            "grid": [[{"color": cube.color, "traversable": cube.traversable} for cube in row] for row in self.grid],
            "start_cube": self.start_cube,
            "goal_cube": self.goal_cube,
        }
        with open(filename, 'w') as f:
            json.dump(data, f)
        print(f"Map saved under: {filename} with data: {data}")

    def load_grid(self, filename):
        with open(filename, 'r') as f:
            data = json.load(f)
        self.rows = data["rows"]
        self.cols = data["cols"]
        self.grid = [[Cube(**cube_data) for cube_data in row] for row in data["grid"]]
        self.start_cube = data["start_cube"]
        self.goal_cube = data["goal_cube"]
        print(f"Loaded map from: {filename} with data: {data}")

class Toolbar:
    def __init__(self, tools, tool_size, tool_spacing):
        self.tools = tools
        self.tool_size = tool_size
        self.tool_spacing = tool_spacing
        self.selected_tool = 0

    def draw_toolbar(self, screen):
        for i, tool in enumerate(self.tools):
            x = i * (self.tool_size + self.tool_spacing)
            if isinstance(tool[1], pygame.Surface):
                screen.blit(tool[1], (x, 0))
            else:
                pygame.draw.rect(screen, tool[1], (x, 0, self.tool_size, self.tool_size))
            if i == self.selected_tool:
                pygame.draw.rect(screen, "black", (x, 0, self.tool_size, self.tool_size), 3)

    def handle_click(self, x, y):
        if y < self.tool_size and x < (self.tool_size * (len(self.tools) + 1)):
            self.selected_tool = x // (self.tool_size + self.tool_spacing)

def load_image(file_path, size):
    image = pygame.image.load(file_path)
    image = pygame.transform.scale(image, (size, size))
    return image.convert()

# pygame setup
pygame.init()

# window setup
window_width, window_height = 1000, 1000
screen = pygame.display.set_mode((window_width, window_height), pygame.RESIZABLE)
pygame.display.set_caption("Pathfinding")

# grid setup
rows, cols = (20, 20)
grid = Grid(rows, cols)
cube_size = 40

# toolbar setup
tool_size = 50
flag_img = load_image('flag.png', tool_size)
play_img = load_image('play.png', tool_size)
save_img = load_image('save.png', tool_size)
load_img = load_image('load.png', tool_size)
toolbar = Toolbar([("start", "green"), ("goal", flag_img), ("obstacle", "grey"), ("play", play_img), ("save", save_img), ("load", load_img)], 50, 10)

# zoom
zoom_factor = 1.0
zoom_increment = 0.1

# center grid
center_x, center_y = grid.center_grid(window_width, window_height, int(cube_size * zoom_factor))

# Game loop
clock = pygame.time.Clock()
running = True

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.VIDEORESIZE:
            new_window_width, new_window_height = event.size
            print("x: " +  str(new_window_width) + " y: " + str(new_window_height))

            screen = pygame.display.set_mode((new_window_width, new_window_height), pygame.RESIZABLE)
            center_x, center_y = grid.center_grid(new_window_width, new_window_height, int(cube_size * zoom_factor))

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: # only accept left-click
                x,y = event.pos
                print(f"x: {x} y: {y}")
                if y < toolbar.tool_size:
                    toolbar.handle_click(x,y)
                    print("Toolbar clicked")
                elif toolbar.selected_tool == 4:
                    current_time = datetime.datetime.now()
                    timestamp = current_time.strftime("%Y_%m_%d-%H_%M_%S")
                    grid.export_grid(f"maps/grid_{timestamp}.json")
                elif toolbar.selected_tool == 5:
                    filename = filedialog.askopenfilename(initialdir=os.getcwd(), filetypes=[("JSON files", "*.json")])
                    if filename:
                        grid.load_grid(filename)
                        center_x, center_y = grid.center_grid(window_width, window_height, int(cube_size * zoom_factor))
                else:
                    grid.handle_click(x,y, int(cube_size * zoom_factor), center_x, center_y, toolbar.selected_tool)

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                zoom_factor += zoom_increment
                center_x, center_y = grid.center_grid(window_width, window_height, int(cube_size * zoom_factor))
            elif event.key == pygame.K_DOWN:
                zoom_factor = max(zoom_increment, zoom_factor - zoom_increment)
                center_x, center_y = grid.center_grid(window_width, window_height, int(cube_size * zoom_factor))

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("white")

    # draw toolbar
    toolbar.draw_toolbar(screen)

    start_time = time.perf_counter()
    for y in range(grid.rows):
        for x in range(grid.cols):
            grid.draw_cube(screen, x, y, int(cube_size * zoom_factor), center_x, center_y)
    end_time = time.perf_counter()
    elapsed_time = (end_time - start_time) * 1000  # Convert to milliseconds
    print(f"Function executed in {elapsed_time:.2f} ms")

    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick()
    print(round(clock.get_fps()))

pygame.quit()
