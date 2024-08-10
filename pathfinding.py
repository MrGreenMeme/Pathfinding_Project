import pygame
import os
from tkinter import filedialog
import datetime
import time
from collections import deque
import logging

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
        self.dirty_rects = []
        self.path_cubes = set()
        self.visited_cubes = set()

    def draw_cube(self, screen, x, y, cube_size, offset_x, offset_y):
        cube = self.grid[y][x]
        rect = pygame.Rect(offset_x + x * cube_size, offset_y + y * cube_size, cube_size, cube_size)
        if (x, y) == self.start_cube:
            cube.color = "green"
        elif (x, y) == self.goal_cube:
            cube.color = "red"
        if cube.color != "white":
            pygame.draw.rect(screen, cube.color, rect)
        if cube_size > 2:
            pygame.draw.rect(screen, "black", rect, 1)
        return rect

    def center_grid(self, window_width, window_height, cube_size):
        grid_width = self.cols * cube_size
        grid_height = self.rows * cube_size
        offset_x = (window_width - grid_width) // 2
        offset_y = (window_height - grid_height) // 2
        return offset_x, offset_y

    def handle_click(self, x, y, cube_size, offset_x, offset_y, selected_tool):
        grid_x = (x - offset_x) // cube_size
        grid_y = (y - offset_y) // cube_size
        logging.debug(f"x: {x} y: {y} grid_x: {grid_x} grid_y: {grid_y} selected_tool: {selected_tool}")
        if 0 <= grid_x < self.cols and 0 <= grid_y < self.rows:
            cube = self.grid[grid_y][grid_x]
            if selected_tool == 0:
                if self.start_cube:
                    old_x, old_y = self.start_cube
                    self.start_cube = None
                    self.grid[old_y][old_x].traversable = True
                    self.grid[old_y][old_x].color = "white"
                    self.dirty_rects.append(self.draw_cube(screen, old_x, old_y, cube_size, offset_x, offset_y))
                self.start_cube = (grid_x, grid_y)
                self.grid[grid_y][grid_x].traversable = True
                cube.color = "green"
                self.dirty_rects.append(self.draw_cube(screen, grid_x, grid_y, cube_size, offset_x, offset_y))
            elif selected_tool == 1:
                if self.goal_cube:
                    old_x, old_y = self.goal_cube
                    self.goal_cube = None
                    self.grid[old_y][old_x].traversable = True
                    self.grid[old_y][old_x].color = "white"
                    self.dirty_rects.append(self.draw_cube(screen, old_x, old_y, cube_size, offset_x, offset_y))
                self.goal_cube = (grid_x, grid_y)
                self.grid[grid_y][grid_x].traversable = True
                cube.color = "red"
                self.dirty_rects.append(self.draw_cube(screen, grid_x, grid_y, cube_size, offset_x, offset_y))
            elif selected_tool == 2:
                cube.color = "grey"
                cube.traversable = False
                self.dirty_rects.append(self.draw_cube(screen, grid_x, grid_y, cube_size, offset_x, offset_y))
            elif selected_tool == 3:
                if (grid_x, grid_y)  == self.start_cube:
                    self.start_cube = None
                elif (grid_x, grid_y)  == self.goal_cube:
                    self.goal_cube = None
                cube.color = "white"
                cube.traversable = True
                self.dirty_rects.append(self.draw_cube(screen, grid_x, grid_y, cube_size, offset_x, offset_y))

    def export_grid(self, filename):
        with open(filename, 'w') as f:
            f.write(f"rows {self.rows}\n")
            f.write(f"cols {self.cols}\n")
            if self.start_cube:
                f.write(f"start {self.start_cube[0]},{self.start_cube[1]}\n")
            if self.goal_cube:
                f.write(f"goal {self.goal_cube[0]},{self.goal_cube[1]}\n")

            # Write grid data
            for row in self.grid:
                for cube in row:
                    f.write('@' if not cube.traversable else '.')
                f.write('\n')

        logging.debug(f"Map saved under: {filename}")

    def load_grid(self, filename):
        with open(filename, 'r') as f:
            lines = f.readlines()

            self.rows = int(lines[0].split()[1])
            self.cols = int(lines[1].split()[1])
            self.grid = [[Cube() for _ in range(self.cols)] for _ in range(self.rows)]

            y = 0
            for line in lines[2:]:
                if line.startswith("start"):
                    start_x, start_y = map(int, line.split()[1].split(','))
                    self.start_cube = (start_x, start_y)
                elif line.startswith("goal"):
                    goal_x, goal_y = map(int, line.split()[1].split(','))
                    self.goal_cube = (goal_x, goal_y)
                else:
                    row_data = line.strip()
                    for x, char in enumerate(row_data):
                        if char == '@':
                            self.grid[y][x].traversable = False
                            self.grid[y][x].color = "grey"
                        elif char == '.':
                            self.grid[y][x].traversable = True
                            self.grid[y][x].color = "white"
                    y += 1

            logging.debug(f"Loaded map from: {filename}")

    def resize(self, new_rows, new_cols):
        self.rows = new_rows
        self.cols = new_cols
        self.grid = [[Cube() for _ in range(new_cols)] for _ in range(new_rows)]
        self.start_cube = None
        self.goal_cube = None

    def bfs_get_neighbors(self, x,y ):
        neighbors = []
        for (move_x, move_y) in [(-1, 0), (1, 0), (0, -1), (0, 1)]: # left, right, up, down
            new_x, new_y = x + move_x, y + move_y
            if 0 <= new_x < self.cols and 0 <= new_y < self.rows and self.grid[new_y][new_x].traversable:
                neighbors.append((new_x, new_y))
        return neighbors

    def bfs(self, screen, cube_size, offset_x, offset_y):
        start_time = time.perf_counter()

        if not self.start_cube or not self.goal_cube:
            logging.info("Start or goal not set.")
            return None

        queue = deque([self.start_cube])
        previous_cube = {self.start_cube: None} # maps cube to the cube it came from
        self.visited_cubes = ({self.start_cube})

        while queue:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

            current_cube = queue.popleft()

            for neighbor in self.bfs_get_neighbors(*current_cube):
                if neighbor == self.goal_cube:
                    self.visited_cubes.add(neighbor)
                    path = []
                    while current_cube != self.start_cube:
                        path.append(current_cube)
                        current_cube = previous_cube[current_cube]
                    path.reverse() # start from start_cube
                    runtime = time.perf_counter() - start_time
                    self.save_statistics(len(path), len(self.visited_cubes) - 1, runtime, True) # -1 to remove start
                    return path

                if neighbor not in self.visited_cubes:
                    self.visited_cubes.add(neighbor)  # track visited cubes
                    queue.append(neighbor)
                    previous_cube[neighbor] = current_cube
                    self.grid[neighbor[1]][neighbor[0]].color = "yellow"
                    rect = self.draw_cube(screen, neighbor[0], neighbor[1], cube_size, offset_x, offset_y)
                    self.dirty_rects.append(rect)

            self.grid[current_cube[1]][current_cube[0]].color = "yellow"
            rect = self.draw_cube(screen, current_cube[0], current_cube[1], cube_size, offset_x, offset_y)
            self.dirty_rects.append(rect)
            pygame.display.update(self.dirty_rects)
            self.dirty_rects.clear()

        logging.info("No path found.")
        runtime = time.perf_counter() - start_time
        self.save_statistics(0, len(self.visited_cubes) - 1, runtime, False) # -1 to remove start
        return None

    def clear_path(self):
        for (x, y) in self.path_cubes:
            self.grid[y][x].color = "white"
        for (x, y) in self.visited_cubes:
            self.grid[y][x].color = "white"
        self.path_cubes.clear()
        self.visited_cubes.clear()
        self.dirty_rects.clear()

    def save_statistics(self, path_length, visited_cubes, runtime, found_goal):
        # statistics = {
        #     "path_length": path_length,
        #     "visited_cubes": visited_cubes,
        #     "runtime": runtime,
        #     "found_goal" : found_goal
        # }
        # filename = f"logs/statistics_{datetime.datetime.now().strftime('%Y_%m_%d-%H_%M_%S')}.json"
        # with open(filename, 'w') as f:
        #     json.dump(statistics, f)
        #logging.debug(f"Statistics saved to {filename}")
        logging.info(f"Stats: path_len: {path_length}, visited_cubes: {visited_cubes}, runtime: {runtime}, found_goal: {found_goal}")

class Toolbar:
    def __init__(self, tools, tool_size, tool_spacing):
        self.toolbar_rect = pygame.Rect(0, 0, (tool_size + tool_spacing) * len(tools), tool_size)
        self.tools = tools
        self.tool_size = tool_size
        self.tool_spacing = tool_spacing
        self.selected_tool = 0
        self.tool_rects = []

    def draw_toolbar(self, screen):
        for i, tool in enumerate(self.tools):
            x = i * (self.tool_size + self.tool_spacing)
            tool_rect = pygame.Rect(x, 0, self.tool_size, self.tool_size)
            self.tool_rects.append(tool_rect)
            if isinstance(tool[1], pygame.Surface):
                screen.blit(tool[1], (x, 0))
            else:
                pygame.draw.rect(screen, tool[1], tool_rect)
            if i == self.selected_tool:
                pygame.draw.rect(screen, "black", tool_rect, 3)

    def handle_click(self, x, y):
        for i, tool_rect in enumerate(self.tool_rects):
            if tool_rect.collidepoint(x, y):
                self.selected_tool = i
                return True
        return False

class InputField:
    def __init__(self, x, y, width, height, font, inactive_color, active_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = inactive_color
        self.inactive_color = inactive_color
        self.active_color = active_color
        self.text = ''
        self.font = font
        self.active = False

    def handle_input(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            self.color = self.active_color if self.active else self.inactive_color
        elif event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    logging.debug(f"Entered: {self.text}")
                    try:
                        new_rows, new_cols = map(int, self.text.lower().split('x'))
                        grid.resize(new_rows, new_cols)
                        redraw_screen()
                    except Exception:
                        logging.info("Format should be rowsxcols like 10x10")
                    self.draw(screen)
                    self.text = ''
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                    self.draw(screen)
                else:
                    self.text += event.unicode
                    self.draw(screen)

    def draw(self, screen):
        pygame.draw.rect(screen, "white", self)
        pygame.draw.rect(screen, self.color, self.rect, 2)
        text_surface = self.font.render(self.text, True, self.color)
        screen.blit(text_surface, (self.rect.x + 5, self.rect.y + 5))

    def shift(self, window_width):
        self.rect.x = window_width - 150

class Dropdown:
    def __init__(self, x, y, width, height, font, options):
        self.rect = pygame.Rect(x, y, width, height)
        self.option_rect = pygame.Rect(0, 0, 0, 0)
        self.font = font
        self.options = options
        self.selected = None
        self.open = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.open = not self.open
            elif self.open:
                for i, option in enumerate(self.options):
                    option_rect = pygame.Rect(self.rect.x, self.rect.y + (i + 1) * self.rect.height, self.rect.width, self.rect.height)
                    if option_rect.collidepoint(event.pos):
                        self.selected = option
                        self.open = False

    def draw(self, screen):
        pygame.draw.rect(screen, "white", self.rect) # clear previous color
        pygame.draw.rect(screen, "grey" if self.open else "black", self.rect)
        text = self.font.render(self.selected if self.selected else "Select Algo", True, "white")
        screen.blit(text, (self.rect.x + 5, self.rect.y + 5))

        if self.open:
            for i, option in enumerate(self.options):
                option_rect = pygame.Rect(self.rect.x, self.rect.y + (i + 1) * self.rect.height, self.rect.width, self.rect.height)
                pygame.draw.rect(screen, "black", option_rect)
                option_text = self.font.render(option, True, "white")
                screen.blit(option_text, (option_rect.x + 5, option_rect.y + 5))
            self.option_rect = pygame.Rect(self.rect.x, self.rect.y + self.rect.height, self.rect.width, self.rect.height * len(self.options))
        else:
            pygame.draw.rect(screen, "white", self.option_rect)
            self.option_rect = pygame.Rect(0, 0, 0, 0)

    def shift(self, window_width):
        self.rect.x = window_width - 350

def load_image(file_path, size):
    image = pygame.image.load(file_path)
    image = pygame.transform.scale(image, (size, size))
    return image.convert()

# pygame setup
pygame.init()

# logging setup
logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s] %(asctime)s - %(message)s')

# window setup
window_width, window_height = 1000, 1000
screen = pygame.display.set_mode((window_width, window_height), pygame.RESIZABLE)
pygame.display.set_caption("Pathfinding")

# grid setup
rows, cols = (15, 15)
grid = Grid(rows, cols)
cube_size = 45

# font setup
font_input_field = pygame.font.Font(None, 32)
font_drop_down = pygame.font.Font(None, 30)

# input field setup
input_field = InputField(window_width - 150, 10, 140, 32, font_input_field, pygame.Color('grey75'), pygame.Color('grey0'))

# dropdown setup
dropdown = Dropdown(window_width - 350, 10, 140, 30, font_drop_down, ["DFS", "BFS", "A*"])

# toolbar setup
tool_size = 50
flag_img = load_image('flag.png', tool_size)
eraser_img = load_image('eraser.png', tool_size)
play_img = load_image('play.png', tool_size)
clear_img = load_image('clear.png', tool_size)
save_img = load_image('save.png', tool_size)
load_img = load_image('load.png', tool_size)
toolbar = Toolbar([("start", "green"), ("goal", flag_img), ("obstacle", "grey"), ("eraser", eraser_img), ("play", play_img), ("clear", clear_img), ("save", save_img), ("load", load_img)], 50, 10)

# zoom
zoom_factor = 1.0
zoom_increment = 0.05

# center grid
center_x, center_y = grid.center_grid(window_width, window_height, int(cube_size * zoom_factor))

# Initial draw of the entire grid

def calculate_zoom_factor(window_width, window_height, grid_cols, grid_rows, cube_size):
    required_zoom_x = window_width / (grid_cols * cube_size)
    required_zoom_y = window_height / (grid_rows * cube_size)

    return min(required_zoom_x, required_zoom_y)
def redraw_screen():
    screen.fill("white")
    toolbar.draw_toolbar(screen)
    input_field.draw(screen)
    dropdown.draw(screen)
    for y in range(grid.rows):
        for x in range(grid.cols):
            grid.draw_cube(screen, x, y, int(cube_size * zoom_factor), center_x, center_y)
    pygame.display.flip()

redraw_screen()

# Game loop
clock = pygame.time.Clock()
running = True
mouse_down = False

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.VIDEORESIZE:
            new_window_width, new_window_height = event.size
            window_width, window_height = new_window_width, new_window_height
            logging.debug("New window_width: " +  str(new_window_width) + " new window_height: " + str(new_window_height))

            screen = pygame.display.set_mode((new_window_width, new_window_height), pygame.RESIZABLE)
            center_x, center_y = grid.center_grid(new_window_width, new_window_height, int(cube_size * zoom_factor))
            input_field.shift(new_window_width)
            dropdown.shift(new_window_width)
            redraw_screen()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: # only accept left-click
                x,y = event.pos
                if toolbar.toolbar_rect.collidepoint(event.pos):
                    if toolbar.handle_click(x, y):
                        toolbar.draw_toolbar(screen)
                    logging.debug("Toolbar clicked")
                    if toolbar.selected_tool == 4: # start algo
                        grid.clear_path()
                        redraw_screen()
                        if dropdown.selected == "BFS":
                            path = grid.bfs(screen, int(cube_size * zoom_factor), center_x, center_y)
                            if path:
                                for (x,y) in path:
                                    grid.grid[y][x].color = "purple"
                                    grid.dirty_rects.append(grid.draw_cube(screen, x, y, int(cube_size * zoom_factor), center_x, center_y))
                        redraw_screen()
                    if toolbar.selected_tool == 5: # clear algo
                        grid.clear_path()
                        redraw_screen()
                    if toolbar.selected_tool == 6: # export grid
                        current_time = datetime.datetime.now()
                        timestamp = current_time.strftime("%Y_%m_%d-%H_%M_%S")
                        grid.export_grid(f"maps/{grid.rows}x{grid.cols}_{timestamp}.txt")
                        logging.debug(f"Grid exported: grid_{timestamp}.json saved in map folder")
                    if toolbar.selected_tool == 7: # import grid
                        filename = filedialog.askopenfilename(initialdir=os.getcwd(), filetypes=[("Text files", "*.txt")])
                        if filename:
                            grid.start_cube = None
                            grid.goal_cube = None
                            grid.load_grid(filename)
                            zoom_factor = calculate_zoom_factor(window_width, window_height, grid.cols, grid.rows, cube_size)
                            logging.debug(f"Grid imported. Calculated zoom factor: {zoom_factor}")
                            center_x, center_y = grid.center_grid(window_width, window_height, int(cube_size * zoom_factor))
                            redraw_screen()
                elif dropdown.rect.collidepoint(event.pos) or dropdown.option_rect.collidepoint(event.pos):
                    dropdown.handle_event(event)
                    dropdown.draw(screen)
                elif input_field.rect.collidepoint(event.pos):
                    input_field.handle_input(event)
                    input_field.draw(screen)
                else:
                    mouse_down = True
                    input_field.active = False
                    input_field.color = pygame.Color('grey75')
                    input_field.draw(screen)
                    dropdown.open = False
                    dropdown.draw(screen)
                    grid.handle_click(x,y, int(cube_size * zoom_factor), center_x, center_y, toolbar.selected_tool)

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                mouse_down = False

        elif event.type == pygame.MOUSEMOTION:
            if mouse_down:
                x,y = event.pos
                if y > toolbar.tool_size:
                    grid.handle_click(x,y, int(cube_size * zoom_factor), center_x, center_y, toolbar.selected_tool)

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                zoom_factor += zoom_increment
                logging.debug(f"Zoomed in. New zoom factor: {zoom_factor}")
                center_x, center_y = grid.center_grid(window_width, window_height, int(cube_size * zoom_factor))
                redraw_screen()
            elif event.key == pygame.K_DOWN:
                zoom_factor = max(zoom_increment, zoom_factor - zoom_increment)
                logging.debug(f"Zoomed out. New zoom factor: {zoom_factor}")
                center_x, center_y = grid.center_grid(window_width, window_height, int(cube_size * zoom_factor))
                redraw_screen()
            input_field.handle_input(event)

    # redraw only dirty rectangles
    for rect in grid.dirty_rects:
        pygame.draw.rect(screen, "white", rect)  # Clear the previous color
        # Redraw the cube in the dirty rect
        x = (rect.x - center_x) // int(cube_size * zoom_factor)
        y = (rect.y - center_y) // int(cube_size * zoom_factor)
        grid.draw_cube(screen, x, y, int(cube_size * zoom_factor), center_x, center_y)

    grid.dirty_rects.clear()

    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick()
    #logging.debug(f"{clock.get_fps():.0f}")

pygame.quit()