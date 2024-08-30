import pygame
import logging
import datetime
from .cube import Cube

class Grid:
    """
    A class representing a grid consisting of Cube objects.

    The Grid class manages a 2D grid of Cube objects, allowing for setting the start and
    goal positions, adding obstacles, loading, exporting and resizing the grid and drawing paths.

    Attributes:
        rows: Number of rows in the grid.
        cols: Number of columns in the grid.
        grid: A 2D list representing the grid of cubes.
        start_cube: Coordinates of the start cube.
        goal_cube: Coordinates of the goal cube.
        dirty_rects: List of rectangles that need to be redrawn.
        current_map_file: Filename of the current map file.
    """

    def __init__(self, rows: int, cols: int):
        """
        Initializes a new Grid object with specified rows and columns.

        Args:
            rows (int): Number of rows in the grid.
            cols (int): Number of columns in the grid.
        """
        self.rows = rows
        self.cols = cols
        self.grid = [[Cube() for _ in range(cols)] for _ in range(rows)]
        self.start_cube = None
        self.goal_cube = None
        self.dirty_rects = []
        self.current_map_file = None

    def draw_cube(self, screen, x: int, y: int, cube_size: int, offset_x: int, offset_y: int):
        """
        Draws a single cube on the screen at the specified grid position.

        Args:
            screen: The Pygame surface to draw on.
            x: The x-coordinate of the cube in the grid.
            y: The y-coordinate of the cube in the grid.
            cube_size: The size of each cube in pixels.
            offset_x: The horizontal offset for drawing the grid on the screen.
            offset_y: The vertical offset for drawing the grid on the screen.

        Returns:
            pygame.Rect: The rectangle representing the drawn cube.
        """
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

    def handle_click(self, x: int, y: int, screen, cube_size: int, offset_x: int, offset_y: int, selected_tool: int) -> None:
        """
        Handles mouse click events on the grid and updates the grid state based on the selected tool.

        Args:
            x: The x-coordinate of the mouse click on the screen.
            y: The y-coordinate of the mouse click on the screen.
            screen: The Pygame surface to draw on.
            cube_size: The size of each cube in pixels.
            offset_x: The horizontal offset for drawing the grid on the screen.
            offset_y: The vertical offset for drawing the grid on the screen.
            selected_tool: The currently selected tool (0: Start, 1: Goal, 2: Obstacle, 3: Eraser).
        """
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

    def export_grid(self) -> None:
        """
        Exports the current grid configuration to a text file.

        The file is saved with a timestamp and includes the grid dimensions,
        start and goal positions, and the grid layout.
        """
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

        current_time = datetime.datetime.now()
        timestamp = current_time.strftime("%Y_%m_%d-%H_%M_%S")
        filename = f"maps/{self.rows}x{self.cols}_{timestamp}.txt"

        with open(filename, 'w') as f:
            for line in generate_grid_data():
                f.write(line)

        self.current_map_file = filename.rsplit('/',1)[1]
        logging.debug(f"Map saved under: {filename}")
    def load_grid(self, filename: str) -> None:
        """
        Loads a grid configuration from a specified file.

        The grid layout, start, and goal positions are restored from the file.

        Args:
            filename: The path to the file to be loaded.
        """
        self.start_cube = None
        self.goal_cube = None
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

    def resize_grid(self, new_rows: int, new_cols: int) -> None:
        """
        Resizes the grid to new dimensions and resets the grid state.

        Args:
            new_rows: The new number of rows for the grid.
            new_cols: The new number of columns for the grid.
        """
        self.rows = new_rows
        self.cols = new_cols
        self.grid = [[Cube() for _ in range(new_cols)] for _ in range(new_rows)]
        self.start_cube = None
        self.goal_cube = None

    def draw_path(self, path, screen, cube_size: int, offset_x: int, offset_y: int) -> None:
        """
        Draws a path on the grid by coloring the cubes along the path.

        Args:
            path: A list of (x, y) tuples representing the path.
            screen: The Pygame surface to draw on.
            cube_size: The size of each cube in pixels.
            offset_x: The horizontal offset for drawing the grid on the screen.
            offset_y: The vertical offset for drawing the grid on the screen.
        """
        for (x, y) in path:
            self.grid[y][x].color = "purple"
            self.dirty_rects.append(self.draw_cube(screen, x, y, cube_size, offset_x, offset_y))
        pygame.display.flip()
        self.dirty_rects.clear()

    def redraw_dirty_rects(self, screen, cube_size: int, offset_x: int, offset_y: int) -> None:
        """
        Redraws only the dirty rectangles on the screen.

        Args:
            screen: The Pygame surface to draw on.
            cube_size: The size of each cube in pixels.
            offset_x: The horizontal offset for drawing the grid on the screen.
            offset_y: The vertical offset for drawing the grid on the screen.
        """
        for rect in self.dirty_rects:
            pygame.draw.rect(screen, "white", rect)  # Clear the previous color
            # Redraw the cube in the dirty rect
            x = (rect.x - offset_x) // cube_size
            y = (rect.y - offset_y) // cube_size
            self.draw_cube(screen, x, y, cube_size, offset_x, offset_y)

        if self.dirty_rects:
            pygame.display.flip()
            self.dirty_rects.clear()