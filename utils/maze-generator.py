import random
import datetime
import logging

class Maze:
    def __init__(self, rows: int, cols: int):
        self.rows = rows
        self.cols = cols
        self.grid = [['@' for _ in range(cols)] for _ in range(rows)]  # fill grid with obstacles
        self.visited = [[False for _ in range(cols)] for _ in range(rows)] # set whole grid to unvisited
        self.directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # right, down, left, up

    def is_valid(self, x: int, y: int) -> bool:
        return 0 <= x < self.cols and 0 <= y < self.rows and not self.visited[y][x]

    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.cols and 0 <= y < self.rows

    def carve_path(self, start_x: int, start_y: int):
        """
        Carves path using backtracking algorithm
        """
        stack = [(start_x, start_y)]
        self.visited[start_y][start_x] = True
        self.grid[start_y][start_x] = '.'  # Carve passage

        while stack:
            x, y = stack[-1] # get current without pop
            neighbors = []
            for direction_x, direction_y in self.directions:
                neighbor_x, neighbors_y = x + direction_x * 2, y + direction_y * 2
                if self.in_bounds(neighbor_x, neighbors_y) and not self.visited[neighbors_y][neighbor_x]: # check for valid and unvisited 2 steps away (neighbor)
                    neighbors.append((neighbor_x, neighbors_y, direction_x, direction_y))

            if neighbors:
                neighbor_x, neighbors_y, direction_x, direction_y = random.choice(neighbors) # randomly select direction to move
                self.grid[y + direction_y][x + direction_x] = '.'  # set @ to . of current position == carve passage
                self.visited[neighbors_y][neighbor_x] = True
                self.grid[neighbors_y][neighbor_x] = '.'  # set @ to . for neighbor == carve passage
                stack.append((neighbor_x, neighbors_y))
            else:
                stack.pop()  # backtrack if no unvisited neighbors

    def generate_maze(self) -> None:
        """
        Generates maze and ensures connectivity from (1, 1) to (rows - 2, cols - 2)
        """
        start_x, start_y = 1, 1
        goal_x, goal_y = self.cols - 2, self.rows - 2

        self.carve_path(start_x, start_y) # builds maze foundation

        # carves actual path that is valid from start to goal
        self.carve_valid_path(start_x, start_y, goal_x, goal_y)


    def carve_valid_path(self, start_x: int, start_y: int, goal_x: int, goal_y: int) -> None:
        """
        Ensures that there is a valid path from start to goal - generates path using DFS
        """
        stack = [(start_x, start_y)]
        previous_cube = {(start_x, start_y): None}  # track the path back to the start
        found = False

        while stack:
            current_cube = stack.pop()  # get top cube from stack

            if current_cube == (goal_x, goal_y):
                found = True
                break

            # process neighbors of the current cube
            for dx, dy in self.directions:
                nx, ny = current_cube[0] + dx, current_cube[1] + dy  # calculate neighbor coordinates
                if self.in_bounds(nx, ny) and self.grid[ny][nx] == '@' and (nx, ny) not in previous_cube:
                    previous_cube[(nx, ny)] = current_cube  # map current_cube to previous
                    stack.append((nx, ny))  # add neighbor to stack for processing next

        # goal was found
        if found:
            path_x, path_y = goal_x, goal_y
            while (path_x, path_y) != (start_x, start_y):
                self.grid[path_y][path_x] = '.'  # carve the path
                path_x, path_y = previous_cube[(path_x, path_y)] # loop through previous_cube dictionary
            self.grid[start_y][start_x] = '.'  # mark start point

    def export_maze(self) -> None:
        def generate_maze_data():
            yield f"rows {self.rows}\n"
            yield f"cols {self.cols}\n"
            yield f"start 1,1\n"
            yield f"goal {self.cols - 1},{self.rows - 1}\n"

            for row in self.grid:
                yield ''.join(row) + '\n'

        current_time = datetime.datetime.now()
        timestamp = current_time.strftime("%Y_%m_%d-%H_%M_%S")
        filename = f"../maps/{self.rows}x{self.cols}_{timestamp}.txt"

        with open(filename, 'w') as f:
            for line in generate_maze_data():
                f.write(line)

        logging.debug(f"Maze saved under: {filename}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    maze = Maze(256, 256)
    maze.generate_maze()
    maze.export_maze()