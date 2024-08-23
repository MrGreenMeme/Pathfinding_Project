import pygame
import os
from tkinter import filedialog
import datetime
import time
from collections import deque
import logging
import heapq
import cProfile
import pstats
import tracemalloc
import csv

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
        self.current_map_file = None

    def draw_cube(self, screen, x, y, cube_size, offset_x, offset_y):
        rect = pygame.Rect(offset_x + x * cube_size, offset_y + y * cube_size, cube_size, cube_size)
        color = self.grid[y][x].color
        if (x, y) == self.start_cube:
            color = "green"
        elif (x, y) == self.goal_cube:
            color = "red"
        if color != "white":
            pygame.draw.rect(screen, color, rect)
        if cube_size > 9:
            pygame.draw.rect(screen, "black", rect, 1)
        return rect

    def center_grid(self, window_width, window_height, cube_size):
        grid_width = self.cols * cube_size
        grid_height = self.rows * cube_size
        offset_x = (window_width - grid_width) // 2
        offset_y = (window_height - grid_height) // 2
        return offset_x, offset_y

    def handle_click(self, x, y, screen, cube_size, offset_x, offset_y, selected_tool):
        grid_x = (x - offset_x) // cube_size
        grid_y = (y - offset_y) // cube_size
        logging.debug(f"x: {x} y: {y} grid_x: {grid_x} grid_y: {grid_y} selected_tool: {selected_tool}")
        if 0 <= grid_x < self.cols and 0 <= grid_y < self.rows:
            if selected_tool == 0:
                if self.start_cube:
                    old_x, old_y = self.start_cube
                    self.start_cube = None
                    self.grid[old_y][old_x].traversable = True
                    self.grid[old_y][old_x].color = "white"
                    self.dirty_rects.append(self.draw_cube(screen, old_x, old_y, cube_size, offset_x, offset_y))
                self.start_cube = (grid_x, grid_y)
                self.grid[grid_y][grid_x].traversable = True
                self.grid[grid_y][grid_x].color = "green"
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
                self.grid[grid_y][grid_x].color = "red"
                self.dirty_rects.append(self.draw_cube(screen, grid_x, grid_y, cube_size, offset_x, offset_y))
            elif selected_tool == 2:
                self.grid[grid_y][grid_x].color = "grey"
                self.grid[grid_y][grid_x].traversable = False
                self.dirty_rects.append(self.draw_cube(screen, grid_x, grid_y, cube_size, offset_x, offset_y))
            elif selected_tool == 3:
                if (grid_x, grid_y)  == self.start_cube:
                    self.start_cube = None
                elif (grid_x, grid_y)  == self.goal_cube:
                    self.goal_cube = None
                self.grid[grid_y][grid_x].color = "white"
                self.grid[grid_y][grid_x].traversable = True
                self.dirty_rects.append(self.draw_cube(screen, grid_x, grid_y, cube_size, offset_x, offset_y))

    def export_grid(self, filename):
        def generate_grid_data():
            yield f"rows {self.rows}\n"
            yield f"cols {self.cols}\n"
            if self.start_cube:
                yield f"start {self.start_cube[0]},{self.start_cube[1]}\n"
            if self.goal_cube:
                yield f"goal {self.goal_cube[0]},{self.goal_cube[1]}\n"

            # Generate grid data
            for row in self.grid:
                yield ''.join('@' if not cube.traversable else '.' for cube in row) + '\n'

        with open(filename, 'w') as f:
            for line in generate_grid_data():
                f.write(line)

        self.current_map_file = filename.rsplit('/',1)[1]
        logging.debug(f"Map saved under: {filename}")
    def load_grid(self, filename):
        with open(filename, 'r') as f:
            lines = f.readlines()

            self.rows = int(lines[0].split()[1])
            self.cols = int(lines[1].split()[1])
            self.grid = [[Cube() for _ in range(self.cols)] for _ in range(self.rows)]
            self.current_map_file = filename.rsplit('/',1)[1]

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

    @staticmethod
    def generate_path(previous_cube, current_cube):
        path = [current_cube]
        while current_cube in previous_cube:
            current_cube = previous_cube[current_cube]
            path.append(current_cube)
        path.reverse()  # Start from start_cube
        return path

    def get_neighbors(self, x, y):
        neighbors = []
        for (move_x, move_y) in [(-1, 0), (1, 0), (0, -1), (0, 1)]: # left, right, up, down
            new_x, new_y = x + move_x, y + move_y
            if 0 <= new_x < self.cols and 0 <= new_y < self.rows and self.grid[new_y][new_x].traversable:
                neighbors.append((new_x, new_y))
        return neighbors

    def bfs(self, screen, cube_size, offset_x, offset_y, trace_memory_enabled):
        start_time = time.perf_counter()
        queue = deque([self.start_cube])
        previous_cube = {} # maps cube to the cube it came from
        self.visited_cubes = {self.start_cube}
        max_queue_size = 1
        while queue:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

            max_queue_size = max(1, len(queue))
            current_cube = queue.popleft()

            if current_cube == self.goal_cube:
                path = self.generate_path(previous_cube, current_cube)
                runtime = time.perf_counter() - start_time
                self.save_statistics(len(path) - 2, len(self.visited_cubes) - 1, max_queue_size, runtime, True, "BFS", self.current_map_file, trace_memory_enabled) # -1 to remove start
                return path

            for neighbor in self.get_neighbors(*current_cube):
                if neighbor not in self.visited_cubes:
                    previous_cube[neighbor] = current_cube
                    queue.append(neighbor)
                    self.visited_cubes.add(neighbor)
                    self.grid[neighbor[1]][neighbor[0]].color = "yellow"
                    self.dirty_rects.append(self.draw_cube(screen, neighbor[0], neighbor[1], cube_size, offset_x, offset_y))

            pygame.display.update(self.dirty_rects)
            self.dirty_rects.clear()

        logging.info("No path found.")
        runtime = time.perf_counter() - start_time
        self.save_statistics(0, len(self.visited_cubes) - 1, max_queue_size, runtime, False, "BFS", self.current_map_file, trace_memory_enabled) # -1 to remove start
        return None

    def dfs(self, screen, cube_size, offset_x, offset_y, trace_memory_enabled):
        start_time = time.perf_counter()
        stack = [self.start_cube]
        previous_cube = {}  # Maps cube to the cube it came from
        self.visited_cubes = {self.start_cube}
        max_queue_size = 1
        while stack:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

            max_queue_size = max(1, len(stack))
            current_cube = stack.pop()

            if current_cube == self.goal_cube:
                path = self.generate_path(previous_cube, current_cube)
                runtime = time.perf_counter() - start_time
                self.save_statistics(len(path) - 2, len(self.visited_cubes) - 1, max_queue_size, runtime, True, "DFS", self.current_map_file, trace_memory_enabled)  # -1 to remove start
                return path

            for neighbor in self.get_neighbors(*current_cube):
                if neighbor not in self.visited_cubes:
                    previous_cube[neighbor] = current_cube
                    stack.append(neighbor)
                    self.visited_cubes.add(neighbor)
                    self.grid[neighbor[1]][neighbor[0]].color = "yellow"
                    self.dirty_rects.append(self.draw_cube(screen, neighbor[0], neighbor[1], cube_size, offset_x, offset_y))

            pygame.display.update(self.dirty_rects)
            self.dirty_rects.clear()

        logging.info("No path found.")
        runtime = time.perf_counter() - start_time
        self.save_statistics(0, len(self.visited_cubes) - 1, max_queue_size, runtime, False, "DFS", self.current_map_file, trace_memory_enabled)  # -1 to remove start
        return None

    @staticmethod
    def heuristic(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1]) # manhattan distance

    def a_star(self, screen, cube_size, offset_x, offset_y, trace_memory_enabled):
        start_time = time.perf_counter()
        open_set = []
        heapq.heappush(open_set, (0, self.start_cube))  # (f_score, node)
        previous_cube = {} # maps cube to previous cube
        g_score = {self.start_cube: 0}
        self.visited_cubes = {self.start_cube}
        max_queue_size = 1
        while open_set:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

            max_queue_size = max(max_queue_size, len(open_set))
            current_cube = heapq.heappop(open_set)[1] # get cube with lowest f_score

            if current_cube == self.goal_cube:
                path = self.generate_path(previous_cube, current_cube)
                runtime = time.perf_counter() - start_time
                self.save_statistics(len(path) - 2, len(self.visited_cubes) - 1, max_queue_size ,runtime, True, "A*", self.current_map_file, trace_memory_enabled)  # -2: remove start + goal || -1: remove start
                return path

            for neighbor in self.get_neighbors(*current_cube):
                temp_g_score = g_score[current_cube] + 1  # all edges have a weight of 1
                if neighbor not in g_score or temp_g_score < g_score[neighbor]:
                    self.visited_cubes.add(neighbor)
                    g_score[neighbor] = temp_g_score
                    f_score = temp_g_score + self.heuristic(neighbor, self.goal_cube) # f_score = heuristic (h_score) + g_score
                    heapq.heappush(open_set, (f_score, neighbor))
                    previous_cube[neighbor] = current_cube
                    self.grid[neighbor[1]][neighbor[0]].color = "yellow"
                    self.dirty_rects.append(self.draw_cube(screen, neighbor[0], neighbor[1], cube_size, offset_x, offset_y))

            pygame.display.update(self.dirty_rects)
            self.dirty_rects.clear()

        logging.info("No path found.")
        runtime = time.perf_counter() - start_time
        self.save_statistics(0, len(self.visited_cubes) - 1, max_queue_size, runtime, False, "A*", self.current_map_file, trace_memory_enabled)  # -1 to remove start
        return None

    def dijkstra(self, screen, cube_size, offset_x, offset_y, trace_memory_enabled):
        start_time = time.perf_counter()
        open_set = []
        heapq.heappush(open_set, (0, self.start_cube))  # (g_score, node)
        previous_cube = {} # maps cube to previous cube
        g_score = {self.start_cube: 0}
        self.visited_cubes = {self.start_cube}
        max_queue_size = 1
        while open_set:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

            max_queue_size = max(max_queue_size, len(open_set))
            current_cube = heapq.heappop(open_set)[1] # get cube with lowest g_score

            if current_cube == self.goal_cube:
                path = self.generate_path(previous_cube, current_cube)
                runtime = time.perf_counter() - start_time
                self.save_statistics(len(path) - 2, len(self.visited_cubes) - 1, max_queue_size, runtime, True, "Dijkstra", self.current_map_file, trace_memory_enabled)
                return path

            for neighbor in self.get_neighbors(*current_cube):
                temp_g_score = g_score[current_cube] + 1  # all edges have a weight of 1
                if neighbor not in g_score or temp_g_score < g_score[neighbor]:
                    self.visited_cubes.add(neighbor)
                    g_score[neighbor] = temp_g_score
                    heapq.heappush(open_set, (temp_g_score, neighbor))
                    previous_cube[neighbor] = current_cube
                    self.grid[neighbor[1]][neighbor[0]].color = "yellow"
                    self.dirty_rects.append(self.draw_cube(screen, neighbor[0], neighbor[1], cube_size, offset_x, offset_y))

            pygame.display.update(self.dirty_rects)
            self.dirty_rects.clear()

        logging.info("No path found.")
        runtime = time.perf_counter() - start_time
        self.save_statistics(0, len(self.visited_cubes) - 1, max_queue_size, runtime, False, "Dijkstra", self.current_map_file, trace_memory_enabled)
        return None

    def greedy_best_first_search(self, screen, cube_size, offset_x, offset_y, trace_memory_enabled):
        start_time = time.perf_counter()
        open_set = []
        heapq.heappush(open_set, (0, self.start_cube))  # (h_score, node)
        previous_cube = {} # maps cube to previous cube
        self.visited_cubes = {self.start_cube}
        max_queue_size = 1
        while open_set:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

            max_queue_size = max(max_queue_size, len(open_set))
            current_cube = heapq.heappop(open_set)[1] # get cube with lowest h_score

            if current_cube == self.goal_cube:
                path = self.generate_path(previous_cube, current_cube)
                runtime = time.perf_counter() - start_time
                self.save_statistics(len(path) - 2, len(self.visited_cubes) - 1, max_queue_size, runtime, True, "Greedy-BeFs", self.current_map_file, trace_memory_enabled)
                return path

            for neighbor in self.get_neighbors(*current_cube):
                if neighbor not in self.visited_cubes:
                    self.visited_cubes.add(neighbor)
                    h_score = self.heuristic(neighbor, self.goal_cube)
                    heapq.heappush(open_set, (h_score, neighbor))
                    previous_cube[neighbor] = current_cube
                    self.grid[neighbor[1]][neighbor[0]].color = "yellow"
                    self.dirty_rects.append(self.draw_cube(screen, neighbor[0], neighbor[1], cube_size, offset_x, offset_y))

            pygame.display.update(self.dirty_rects)
            self.dirty_rects.clear()

        logging.info("No path found.")
        runtime = time.perf_counter() - start_time
        self.save_statistics(0, len(self.visited_cubes) - 1, max_queue_size, runtime, False, "Greedy-BeFs", self.current_map_file, trace_memory_enabled)
        return None

    def clear_path(self):
        for (x, y) in self.visited_cubes:
            self.grid[y][x].color = "white"
        self.visited_cubes.clear()

    @staticmethod
    def save_statistics(path_length, visited_cubes, max_queue_size, runtime, found_goal, algorithm, current_map_file, memory_tracing_enabled):
        if memory_tracing_enabled:
            return None
        with open("results/Stats.csv", "a", newline="") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow([algorithm, path_length, visited_cubes, max_queue_size, runtime, found_goal, current_map_file if current_map_file else 'not found'])
        logging.info(f"Stats: {algorithm} => path_len: {path_length}, visited_cubes: {visited_cubes}, max_queue_size: {max_queue_size}, runtime: {runtime}, found_goal: {found_goal}, map: {current_map_file if current_map_file else 'na'}")

    @staticmethod
    def save_memory_statistics(stat, algorithm, map_file):
        with open("results/Memory-Consumption.csv", "a", newline="") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow([algorithm, map_file if map_file else 'not found', stat.size / 1024, stat.count, stat.size / stat.count])
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
        pygame.display.update(self.toolbar_rect)

    def handle_click(self, x, y):
        for i, tool_rect in enumerate(self.tool_rects):
            if tool_rect.collidepoint(x, y):
                if self.selected_tool == i:
                    self.selected_tool = None
                else:
                    self.selected_tool = i
                return True
        return False

class InputField:
    def __init__(self, x, y, width, height, font, inactive_color, active_color, redraw_screen):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = inactive_color
        self.inactive_color = inactive_color
        self.active_color = active_color
        self.text = ''
        self.font = font
        self.active = False
        self.redraw_screen = redraw_screen

    def handle_click(self, event):
        if self.rect.collidepoint(event.pos):
            self.active = not self.active
        self.color = self.active_color if self.active else self.inactive_color

    def handle_input(self, event, screen, grid):
        if self.active:
            if event.key == pygame.K_RETURN:
                logging.debug(f"Entered: {self.text}")
                try:
                    new_rows, new_cols = map(int, self.text.lower().split('x'))
                    grid.resize(new_rows, new_cols)
                    self.redraw_screen()
                except Exception:
                    logging.info("Format should be rowsxcols like 10x10")
                self.text = ''
                self.draw(screen)
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
        pygame.display.update(self.rect)

    def shift(self, window_width):
        self.rect.x = window_width - 270

class Dropdown:
    def __init__(self, x, y, width, height, font, options):
        self.rect = pygame.Rect(x, y, width, height)
        self.option_rect = pygame.Rect(0, 0, 0, 0)
        self.font = font
        self.options = options
        self.selected = None
        self.open = False

    def handle_click(self, event):
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
            pygame.display.flip()
        else:
            pygame.draw.rect(screen, "white", self.option_rect)
            self.option_rect = pygame.Rect(0, 0, 0, 0)
            pygame.display.flip()

    def shift(self, window_width):
        self.rect.x = window_width - 400

class ToggleButton:
    def __init__(self, x, y, width, height, offset, font, text):
        self.offset = offset
        self.rect = pygame.Rect(x, y, width, height)
        self.font = font
        self.text = text
        self.state = False
        self.color_on = pygame.Color('green')
        self.color_off = pygame.Color('grey')

    def draw(self, screen):
        color = self.color_on if self.state else self.color_off
        pygame.draw.rect(screen, color, self.rect)
        text = self.font.render(self.text, True, "white")
        screen.blit(text, (self.rect.x + 3, self.rect.y + 10))
        pygame.display.update(self.rect)
    def handle_click(self):
        self.state = not self.state

    def shift(self, window_width):
        self.rect.x = window_width - self.offset


def main():
    # pygame setup
    pygame.init()

    # logging setup
    logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s] %(asctime)s - %(message)s')

    # window setup
    window_width, window_height = 1000, 1000
    screen = pygame.display.set_mode((window_width, window_height), pygame.RESIZABLE)
    pygame.display.set_caption("Pathfinding")
    def redraw_screen():
        screen.fill("white")
        toolbar.draw_toolbar(screen)
        input_field.draw(screen)
        dropdown.draw(screen)
        memory_tracing_toggle.draw(screen)
        run_ten_times_toggle.draw(screen)
        for y in range(grid.rows):
            for x in range(grid.cols):
                grid.draw_cube(screen, x, y, int(cube_size * zoom_factor), center_x, center_y)
        pygame.display.flip()

    # grid setup
    rows, cols = (15, 15)
    grid = Grid(rows, cols)
    cube_size = 45

    # font setup
    font_input_field = pygame.font.Font(None, 28)
    font_drop_down = pygame.font.Font(None, 24)
    memory_tracing_toggle_button = pygame.font.Font(None, 12)
    run_ten_times_toogle_button = pygame.font.Font(None, 18)

    # input field setup
    input_field = InputField(window_width - 270, 10, 120, 30, font_input_field, pygame.Color('grey75'), pygame.Color('grey0'), redraw_screen)

    # dropdown setup
    dropdown = Dropdown(window_width - 400, 10, 120, 25, font_drop_down, ["DFS", "BFS", "A*", "Dijkstra", "Greedy-BeFs"])

    # toggle button setup
    memory_tracing_toggle = ToggleButton(window_width - 140, 10, 60, 30, 140, memory_tracing_toggle_button, "Trace-Memory")
    run_ten_times_toggle = ToggleButton(window_width - 70, 10, 30, 30, 70, run_ten_times_toogle_button, "10x")

    # toolbar setup
    def load_image(file_path, size):
        image = pygame.image.load(file_path)
        image = pygame.transform.scale(image, (size, size))
        return image.convert()

    tool_size = 50
    flag_img = load_image('flag.png', tool_size)
    eraser_img = load_image('eraser.png', tool_size)
    play_img = load_image('play.png', tool_size)
    clear_img = load_image('clear.png', tool_size)
    save_img = load_image('save.png', tool_size)
    load_img = load_image('load.png', tool_size)
    toolbar = Toolbar([("start", "green"), ("goal", flag_img), ("obstacle", "grey"), ("eraser", eraser_img), ("play", play_img), ("clear", clear_img), ("save", save_img), ("load", load_img)], 50, 10)

    # zoom
    def calculate_zoom_factor(window_width, window_height, grid_cols, grid_rows, cube_size):
        required_zoom_x = window_width / (grid_cols * cube_size)
        required_zoom_y = window_height / (grid_rows * cube_size)
        return min(required_zoom_x, required_zoom_y)

    zoom_factor = 1.0
    zoom_increment = 0.05

    # center grid
    center_x, center_y = grid.center_grid(window_width, window_height, int(cube_size * zoom_factor))

    # Initial draw of the entire grid
    redraw_screen()

    # Game loop
    clock = pygame.time.Clock()
    running = True
    mouse_down = False
    move_grid = False
    move_grid_x = 0
    move_grid_y = 0

    # Algorithms
    def run_algorithm(grid, algorithm, screen, cube_size, center_x, center_y):
        pathfinding_algorithms = {
            "BFS": grid.bfs,
            "A*": grid.a_star,
            "DFS": grid.dfs,
            "Dijkstra": grid.dijkstra,
            "Greedy-BeFs": grid.greedy_best_first_search
        }
        if algorithm in pathfinding_algorithms:

            algo_runs = 10 if run_ten_times_toggle.state else 1

            for _ in range(algo_runs):
                grid.clear_path()
                redraw_screen()

                if memory_tracing_toggle.state:
                    tracemalloc.start()

                path = pathfinding_algorithms[algorithm](screen, cube_size, center_x, center_y, memory_tracing_toggle.state)

                if memory_tracing_toggle.state:
                    snapshot = tracemalloc.take_snapshot()
                    top_stats = snapshot.statistics('filename')
                    grid.save_memory_statistics(top_stats[0], algorithm, grid.current_map_file)
                    tracemalloc.stop()

                if path:
                    for (x, y) in path:
                        grid.grid[y][x].color = "purple"
                        grid.dirty_rects.append(grid.draw_cube(screen, x, y, cube_size, center_x, center_y))
                    pygame.display.flip()
                    grid.dirty_rects.clear()

    while running:
        clock.tick(60)
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
                memory_tracing_toggle.shift(new_window_width)
                run_ten_times_toggle.shift(new_window_width)
                redraw_screen()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # only accept left-click
                    x,y = event.pos
                    if toolbar.toolbar_rect.collidepoint(event.pos): # toolbar
                        if toolbar.handle_click(x, y):
                            toolbar.draw_toolbar(screen)
                        #logging.debug("Toolbar clicked")
                        if toolbar.selected_tool == 4: # start algo
                            grid.clear_path()
                            redraw_screen()
                            if dropdown.selected in ["BFS", "A*", "DFS", "Dijkstra", "Greedy-BeFs"] and grid.start_cube and grid.goal_cube:
                                run_algorithm(grid, dropdown.selected, screen, int(cube_size * zoom_factor), center_x, center_y)
                        if toolbar.selected_tool == 5: # clear algo
                            grid.clear_path()
                            redraw_screen()
                        if toolbar.selected_tool == 6: # export grid
                            current_time = datetime.datetime.now()
                            timestamp = current_time.strftime("%Y_%m_%d-%H_%M_%S")
                            grid.export_grid(f"maps/{grid.rows}x{grid.cols}_{timestamp}.txt")
                            logging.debug(f"Grid exported: grid_{timestamp}.json saved in map folder")
                        elif toolbar.selected_tool == 7: # import grid
                            filename = filedialog.askopenfilename(initialdir=os.getcwd(), filetypes=[("Text files", "*.txt")])
                            if filename:
                                grid.start_cube = None
                                grid.goal_cube = None
                                grid.visited_cubes.clear()
                                grid.load_grid(filename)
                                zoom_factor = calculate_zoom_factor(window_width, window_height, grid.cols, grid.rows, cube_size)
                                logging.debug(f"Grid imported. Calculated zoom factor: {zoom_factor}")
                                center_x, center_y = grid.center_grid(window_width, window_height, int(cube_size * zoom_factor))
                                redraw_screen()
                                toolbar.selected_tool = None
                    elif dropdown.rect.collidepoint(event.pos) or dropdown.option_rect.collidepoint(event.pos): # dropdown
                        dropdown.handle_click(event)
                        dropdown.draw(screen)
                    elif input_field.rect.collidepoint(event.pos): # input_field
                        input_field.handle_click(event)
                        input_field.draw(screen)
                    elif memory_tracing_toggle.rect.collidepoint(event.pos):  # toggle button
                        memory_tracing_toggle.handle_click()
                        memory_tracing_toggle.draw(screen)
                    elif run_ten_times_toggle.rect.collidepoint(event.pos):  # toggle button
                        run_ten_times_toggle.handle_click()
                        run_ten_times_toggle.draw(screen)
                    else: # grid
                        mouse_down = True
                        input_field.active = False
                        input_field.color = pygame.Color('grey75')
                        input_field.draw(screen)
                        dropdown.open = False
                        dropdown.draw(screen)
                        if toolbar.selected_tool is None:
                            move_grid_x, move_grid_y = event.pos
                            move_grid = True
                        else:
                            grid.handle_click(x, y, screen, int(cube_size * zoom_factor), center_x, center_y, toolbar.selected_tool)

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    mouse_down = False
                    if move_grid:
                        redraw_screen()
                    move_grid = False

            elif event.type == pygame.MOUSEMOTION:
                if mouse_down:
                    x,y = event.pos
                    if move_grid:
                        shift_x = x - move_grid_x
                        shift_y = y - move_grid_y
                        center_x += shift_x
                        center_y += shift_y
                        move_grid_x = x
                        move_grid_y = y
                    else:
                        grid.handle_click(x, y, screen, int(cube_size * zoom_factor), center_x, center_y, toolbar.selected_tool)

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    zoom_factor += zoom_increment
                    logging.debug(f"Zoomed in. New zoom factor: {zoom_factor} + {int(cube_size * zoom_factor)}")
                    center_x, center_y = grid.center_grid(window_width, window_height, int(cube_size * zoom_factor))
                    redraw_screen()
                elif event.key == pygame.K_DOWN:
                    zoom_factor = max(zoom_increment, zoom_factor - zoom_increment)
                    logging.debug(f"Zoomed out. New zoom factor: {zoom_factor} + {int(cube_size * zoom_factor)}")
                    center_x, center_y = grid.center_grid(window_width, window_height, int(cube_size * zoom_factor))
                    redraw_screen()
                input_field.handle_input(event, screen, grid)

        # redraw only dirty rectangles
        for rect in grid.dirty_rects:
            pygame.draw.rect(screen, "white", rect)  # Clear the previous color
            # Redraw the cube in the dirty rect
            x = (rect.x - center_x) // int(cube_size * zoom_factor)
            y = (rect.y - center_y) // int(cube_size * zoom_factor)
            grid.draw_cube(screen, x, y, int(cube_size * zoom_factor), center_x, center_y)

        if grid.dirty_rects:
            pygame.display.flip()
            grid.dirty_rects.clear()

    pygame.quit()

if __name__ == '__main__':
    main()
    # cProfile.run('main()', 'profiling_results.prof')
    # p = pstats.Stats('profiling_results.prof')
    # p.strip_dirs().sort_stats('time').print_stats(10)