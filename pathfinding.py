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
        self.dirty_rects = []

    def draw_cube(self, screen, x, y, cube_size, offset_x, offset_y):
        cube = self.grid[y][x]
        rect = pygame.Rect(offset_x + x * cube_size, offset_y + y * cube_size, cube_size, cube_size)
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
        print(f"x: {x} y: {y} grid_x: {grid_x} grid_y: {grid_y} selected_tool: {selected_tool}")
        if 0 <= grid_x < self.cols and 0 <= grid_y < self.rows:
            cube = self.grid[grid_y][grid_x]
            if selected_tool == 0:
                if self.start_cube:
                    old_x, old_y = self.start_cube
                    self.grid[old_y][old_x].color = "white"
                    self.dirty_rects.append(self.draw_cube(screen, old_x, old_y, cube_size, offset_x, offset_y))
                self.start_cube = grid_x,grid_y
                cube.color = "green"
            elif selected_tool == 1:
                if self.goal_cube:
                    old_x, old_y = self.goal_cube
                    self.grid[old_y][old_x].color = "white"
                    self.dirty_rects.append(self.draw_cube(screen, old_x, old_y, cube_size, offset_x, offset_y))
                self.goal_cube = grid_x,grid_y
                cube.color = "red"
            elif selected_tool == 2:
                cube.color = "black"
                cube.traversable = False
            elif selected_tool == 3:
                cube.color = "white"
            self.dirty_rects.append(self.draw_cube(screen, grid_x, grid_y, cube_size, offset_x, offset_y))

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

    def resize(self, new_rows, new_cols):
        self.rows = new_rows
        self.cols = new_cols
        self.grid = [[Cube() for _ in range(new_cols)] for _ in range(new_rows)]
        self.start_cube = None
        self.goal_cube = None


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
                    print(f"Entered: {self.text}")
                    try:
                        new_rows, new_cols = map(int, self.text.lower().split('x'))
                        grid.resize(new_rows, new_cols)
                        redraw_screen()
                    except Exception:
                        print("Format should be rowsxcols like 10x10")
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
            print(f"optionsect{self.option_rect}")
        else:
            pygame.draw.rect(screen, "white", self.option_rect)
            self.option_rect = pygame.Rect(0, 0, 0, 0)

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
rows, cols = (15, 15)
grid = Grid(rows, cols)
cube_size = 50

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
play_img = load_image('play.png', tool_size)
save_img = load_image('save.png', tool_size)
load_img = load_image('load.png', tool_size)
eraser_img = load_image('eraser.png', tool_size)
toolbar = Toolbar([("start", "green"), ("goal", flag_img), ("obstacle", "grey"), ("eraser", eraser_img), ("play", play_img), ("save", save_img), ("load", load_img)], 50, 10)

# zoom
zoom_factor = 1.0
zoom_increment = 0.05

# center grid
center_x, center_y = grid.center_grid(window_width, window_height, int(cube_size * zoom_factor))

# Initial draw of the entire grid
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
            print("x: " +  str(new_window_width) + " y: " + str(new_window_height))

            screen = pygame.display.set_mode((new_window_width, new_window_height), pygame.RESIZABLE)
            center_x, center_y = grid.center_grid(new_window_width, new_window_height, int(cube_size * zoom_factor))
            redraw_screen()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: # only accept left-click
                x,y = event.pos
                if toolbar.toolbar_rect.collidepoint(event.pos):
                    if toolbar.handle_click(x, y):
                        toolbar.draw_toolbar(screen)
                    print("Toolbar clicked")
                    if toolbar.selected_tool == 5:
                        current_time = datetime.datetime.now()
                        timestamp = current_time.strftime("%Y_%m_%d-%H_%M_%S")
                        grid.export_grid(f"maps/grid_{timestamp}.json")
                        print(f"Map: grid_{timestamp}.json saved in map folder")
                    if toolbar.selected_tool == 6:
                        filename = filedialog.askopenfilename(initialdir=os.getcwd(), filetypes=[("JSON files", "*.json")])
                        if filename:
                            grid.load_grid(filename)
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
                center_x, center_y = grid.center_grid(window_width, window_height, int(cube_size * zoom_factor))
                redraw_screen()
            elif event.key == pygame.K_DOWN:
                print(f"cubesize{int(cube_size * zoom_factor)}")
                zoom_factor = max(zoom_increment, zoom_factor - zoom_increment)
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
    #print(round(clock.get_fps()))

pygame.quit()