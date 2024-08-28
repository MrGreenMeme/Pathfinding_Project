import pygame
import logging
from .cube import Cube

class Grid:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.grid = [[Cube() for _ in range(cols)] for _ in range(rows)]
        self.start_cube = None
        self.goal_cube = None
        self.dirty_rects = []
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

    def resize_grid(self, new_rows, new_cols):
        self.rows = new_rows
        self.cols = new_cols
        self.grid = [[Cube() for _ in range(new_cols)] for _ in range(new_rows)]
        self.start_cube = None
        self.goal_cube = None