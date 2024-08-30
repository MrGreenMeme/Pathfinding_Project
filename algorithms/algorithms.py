import pygame
import time
from collections import deque
import heapq
import csv
import logging

class Algorithms:
    """
    A class that implements various pathfinding algorithms for a grid-based system.

    Attributes:
        grid: An instance of the Grid class that contains the grid to be processed.
        visited_cubes: A set of visited cube coordinates during the algorithm's execution.
    """
    def __init__(self, grid):
        """
        Initializes the Algorithms class with a grid.

        Args:
            grid: An instance of the Grid class that contains the grid to be processed.
        """
        self.grid = grid
        self.visited_cubes = set()
    @staticmethod
    def generate_path(previous_cube, current_cube):
        """
        Generates a path from the start to the current cube using the previous_cube mapping.

        Args:
            previous_cube: A dictionary mapping each cube to the cube it came from.
            current_cube: The ending cube from which the path is generated.

        Returns:
            A list of cubes representing the path from start to the current cube.
        """
        path = [current_cube]
        while current_cube in previous_cube:
            current_cube = previous_cube[current_cube]
            path.append(current_cube)
        path.reverse()
        return path
    def clear_path(self) -> None:
        """Clears the path by resetting the color of all visited cubes to white."""
        for (x, y) in self.visited_cubes:
            self.grid.grid[y][x].color = "white"
        self.visited_cubes.clear()

    def get_neighbors(self, x, y):
        """
        Gets the neighboring cubes of a given cube that are traversable.

        Args:
            x: The x-coordinate of the current cube.
            y: The y-coordinate of the current cube.

        Returns:
            A list of tuples representing the coordinates of the neighboring traversable cubes.
        """
        neighbors = []
        for (move_x, move_y) in [(-1, 0), (1, 0), (0, -1), (0, 1)]: # left, right, up, down
            new_x, new_y = x + move_x, y + move_y
            if 0 <= new_x < self.grid.cols and 0 <= new_y < self.grid.rows and self.grid.grid[new_y][new_x].traversable:
                neighbors.append((new_x, new_y))
        return neighbors

    def bfs(self, screen, cube_size: int, offset_x: int, offset_y: int, trace_memory_enabled: bool):
        """
        Performs Breadth-First Search (BFS) to find a path from the start cube to the goal cube.

        Args:
            screen: The Pygame screen surface to draw the grid on.
            cube_size: The size of each cube in the grid.
            offset_x: The horizontal offset for drawing the cubes.
            offset_y: The vertical offset for drawing the cubes.
            trace_memory_enabled: A boolean flag indicating if memory tracing is enabled.

        Returns:
            A list of cubes representing the path from the start cube to the goal cube, or None if no path is found.
        """
        start_time = time.perf_counter()
        queue = deque([self.grid.start_cube])
        previous_cube = {} # maps cube to the cube it came from
        self.visited_cubes = {self.grid.start_cube}
        max_queue_size = 1
        while queue:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

            max_queue_size = max(1, len(queue))
            current_cube = queue.popleft()

            if current_cube == self.grid.goal_cube:
                path = self.generate_path(previous_cube, current_cube)
                runtime = time.perf_counter() - start_time
                self.save_statistics(len(path) - 2, len(self.visited_cubes) - 1, max_queue_size, runtime, True, "BFS", self.grid.current_map_file, trace_memory_enabled) # -1 to remove start
                return path

            for neighbor in self.get_neighbors(*current_cube):
                if neighbor not in self.visited_cubes:
                    previous_cube[neighbor] = current_cube
                    queue.append(neighbor)
                    self.visited_cubes.add(neighbor)
                    self.grid.grid[neighbor[1]][neighbor[0]].color = "yellow"
                    self.grid.dirty_rects.append(self.grid.draw_cube(screen, neighbor[0], neighbor[1], cube_size, offset_x, offset_y))

            pygame.display.update(self.grid.dirty_rects)
            self.grid.dirty_rects.clear()

        logging.info("No path found.")
        runtime = time.perf_counter() - start_time
        self.save_statistics(0, len(self.visited_cubes) - 1, max_queue_size, runtime, False, "BFS", self.grid.current_map_file, trace_memory_enabled) # -1 to remove start
        return None

    def dfs(self, screen, cube_size: int, offset_x: int, offset_y: int, trace_memory_enabled: bool):
        """
        Performs Depth-First Search (DFS) to find a path from the start cube to the goal cube.

        Args:
            screen: The Pygame screen surface to draw the grid on.
            cube_size: The size of each cube in the grid.
            offset_x: The horizontal offset for drawing the cubes.
            offset_y: The vertical offset for drawing the cubes.
            trace_memory_enabled: A boolean flag indicating if memory tracing is enabled.

        Returns:
            A list of cubes representing the path from the start cube to the goal cube, or None if no path is found.
        """
        start_time = time.perf_counter()
        stack = [self.grid.start_cube]
        previous_cube = {}  # Maps cube to the cube it came from
        self.visited_cubes = {self.grid.start_cube}
        max_queue_size = 1
        while stack:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

            max_queue_size = max(1, len(stack))
            current_cube = stack.pop()

            if current_cube == self.grid.goal_cube:
                path = self.generate_path(previous_cube, current_cube)
                runtime = time.perf_counter() - start_time
                self.save_statistics(len(path) - 2, len(self.visited_cubes) - 1, max_queue_size, runtime, True, "DFS", self.grid.current_map_file, trace_memory_enabled)  # -1 to remove start
                return path

            for neighbor in self.get_neighbors(*current_cube):
                if neighbor not in self.visited_cubes:
                    previous_cube[neighbor] = current_cube
                    stack.append(neighbor)
                    self.visited_cubes.add(neighbor)
                    self.grid.grid[neighbor[1]][neighbor[0]].color = "yellow"
                    self.grid.dirty_rects.append(self.grid.draw_cube(screen, neighbor[0], neighbor[1], cube_size, offset_x, offset_y))

            pygame.display.update(self.grid.dirty_rects)
            self.grid.dirty_rects.clear()

        logging.info("No path found.")
        runtime = time.perf_counter() - start_time
        self.save_statistics(0, len(self.visited_cubes) - 1, max_queue_size, runtime, False, "DFS", self.grid.current_map_file, trace_memory_enabled)  # -1 to remove start
        return None

    @staticmethod
    def heuristic(a, b):
        """
        Calculates the heuristic value (Manhattan distance) between two cubes.

        Args:
            a: The coordinates of the first cube.
            b: The coordinates of the second cube.

        Returns:
            The Manhattan distance between the two cubes.
        """
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def a_star(self, screen, cube_size: int, offset_x: int, offset_y: int, trace_memory_enabled: bool):
        """
        Performs A* search algorithm to find the shortest path from the start cube to the goal cube.

        Args:
            screen: The Pygame screen surface to draw the grid on.
            cube_size: The size of each cube in the grid.
            offset_x: The horizontal offset for drawing the cubes.
            offset_y: The vertical offset for drawing the cubes.
            trace_memory_enabled: A boolean flag indicating if memory tracing is enabled.

        Returns:
            A list of cubes representing the path from the start cube to the goal cube, or None if no path is found.
        """
        start_time = time.perf_counter()
        open_set = []
        heapq.heappush(open_set, (0, self.grid.start_cube))  # (f_score, node)
        previous_cube = {} # maps cube to previous cube
        g_score = {self.grid.start_cube: 0}
        self.visited_cubes = {self.grid.start_cube}
        max_queue_size = 1
        while open_set:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

            max_queue_size = max(max_queue_size, len(open_set))
            current_cube = heapq.heappop(open_set)[1] # get cube with lowest f_score

            if current_cube == self.grid.goal_cube:
                path = self.generate_path(previous_cube, current_cube)
                runtime = time.perf_counter() - start_time
                self.save_statistics(len(path) - 2, len(self.visited_cubes) - 1, max_queue_size ,runtime, True, "A*", self.grid.current_map_file, trace_memory_enabled)  # -2: remove start + goal || -1: remove start
                return path

            for neighbor in self.get_neighbors(*current_cube):
                temp_g_score = g_score[current_cube] + 1  # all edges have a weight of 1
                if neighbor not in g_score or temp_g_score < g_score[neighbor]:
                    self.visited_cubes.add(neighbor)
                    g_score[neighbor] = temp_g_score
                    f_score = temp_g_score + self.heuristic(neighbor, self.grid.goal_cube) # f_score = heuristic (h_score) + g_score
                    heapq.heappush(open_set, (f_score, neighbor))
                    previous_cube[neighbor] = current_cube
                    self.grid.grid[neighbor[1]][neighbor[0]].color = "yellow"
                    self.grid.dirty_rects.append(self.grid.draw_cube(screen, neighbor[0], neighbor[1], cube_size, offset_x, offset_y))

            pygame.display.update(self.grid.dirty_rects)
            self.grid.dirty_rects.clear()

        logging.info("No path found.")
        runtime = time.perf_counter() - start_time
        self.save_statistics(0, len(self.visited_cubes) - 1, max_queue_size, runtime, False, "A*", self.grid.current_map_file, trace_memory_enabled)  # -1 to remove start
        return None

    def dijkstra(self, screen, cube_size: int, offset_x: int, offset_y: int, trace_memory_enabled: bool):
        """
        Performs Dijkstra's algorithm to find the shortest path from the start cube to the goal cube.

        Args:
            screen: The Pygame screen surface to draw the grid on.
            cube_size: The size of each cube in the grid.
            offset_x: The horizontal offset for drawing the cubes.
            offset_y: The vertical offset for drawing the cubes.
            trace_memory_enabled: A boolean flag indicating if memory tracing is enabled.

        Returns:
            A list of cubes representing the path from the start cube to the goal cube, or None if no path is found.
        """
        start_time = time.perf_counter()
        open_set = []
        heapq.heappush(open_set, (0, self.grid.start_cube))  # (g_score, node)
        previous_cube = {} # maps cube to previous cube
        g_score = {self.grid.start_cube: 0}
        self.visited_cubes = {self.grid.start_cube}
        max_queue_size = 1
        while open_set:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

            max_queue_size = max(max_queue_size, len(open_set))
            current_cube = heapq.heappop(open_set)[1] # get cube with lowest g_score

            if current_cube == self.grid.goal_cube:
                path = self.generate_path(previous_cube, current_cube)
                runtime = time.perf_counter() - start_time
                self.save_statistics(len(path) - 2, len(self.visited_cubes) - 1, max_queue_size, runtime, True, "Dijkstra", self.grid.current_map_file, trace_memory_enabled)
                return path

            for neighbor in self.get_neighbors(*current_cube):
                temp_g_score = g_score[current_cube] + 1  # all edges have a weight of 1
                if neighbor not in g_score or temp_g_score < g_score[neighbor]:
                    self.visited_cubes.add(neighbor)
                    g_score[neighbor] = temp_g_score
                    heapq.heappush(open_set, (temp_g_score, neighbor))
                    previous_cube[neighbor] = current_cube
                    self.grid.grid[neighbor[1]][neighbor[0]].color = "yellow"
                    self.grid.dirty_rects.append(self.grid.draw_cube(screen, neighbor[0], neighbor[1], cube_size, offset_x, offset_y))

            pygame.display.update(self.grid.dirty_rects)
            self.grid.dirty_rects.clear()

        logging.info("No path found.")
        runtime = time.perf_counter() - start_time
        self.save_statistics(0, len(self.visited_cubes) - 1, max_queue_size, runtime, False, "Dijkstra", self.grid.current_map_file, trace_memory_enabled)
        return None

    def greedy_best_first_search(self, screen, cube_size: int, offset_x: int, offset_y: int, trace_memory_enabled: bool):
        """
        Performs Greedy Best-First Search to find a path from the start cube to the goal cube.

        Args:
            screen: The Pygame screen surface to draw the grid on.
            cube_size: The size of each cube in the grid.
            offset_x: The horizontal offset for drawing the cubes.
            offset_y: The vertical offset for drawing the cubes.
            trace_memory_enabled: A boolean flag indicating if memory tracing is enabled.

        Returns:
            A list of cubes representing the path from the start cube to the goal cube, or None if no path is found.
        """
        start_time = time.perf_counter()
        open_set = []
        heapq.heappush(open_set, (0, self.grid.start_cube))  # (h_score, node)
        previous_cube = {} # maps cube to previous cube
        self.visited_cubes = {self.grid.start_cube}
        max_queue_size = 1
        while open_set:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

            max_queue_size = max(max_queue_size, len(open_set))
            current_cube = heapq.heappop(open_set)[1] # get cube with lowest h_score

            if current_cube == self.grid.goal_cube:
                path = self.generate_path(previous_cube, current_cube)
                runtime = time.perf_counter() - start_time
                self.save_statistics(len(path) - 2, len(self.visited_cubes) - 1, max_queue_size, runtime, True, "Greedy-BeFs", self.grid.current_map_file, trace_memory_enabled)
                return path

            for neighbor in self.get_neighbors(*current_cube):
                if neighbor not in self.visited_cubes:
                    self.visited_cubes.add(neighbor)
                    h_score = self.heuristic(neighbor, self.grid.goal_cube)
                    heapq.heappush(open_set, (h_score, neighbor))
                    previous_cube[neighbor] = current_cube
                    self.grid.grid[neighbor[1]][neighbor[0]].color = "yellow"
                    self.grid.dirty_rects.append(self.grid.draw_cube(screen, neighbor[0], neighbor[1], cube_size, offset_x, offset_y))

            pygame.display.update(self.grid.dirty_rects)
            self.grid.dirty_rects.clear()

        logging.info("No path found.")
        runtime = time.perf_counter() - start_time
        self.save_statistics(0, len(self.visited_cubes) - 1, max_queue_size, runtime, False, "Greedy-BeFs", self.grid.current_map_file, trace_memory_enabled)
        return None

    @staticmethod
    def save_statistics(path_length: int, visited_cubes: int, max_queue_size: int, runtime: float, found_goal: bool, algorithm: str, current_map_file, memory_tracing_enabled: bool) -> None:
        """
        Saves pathfinding statistics to a CSV file.

        Args:
            path_length: The length of the found path (excluding start and goal).
            visited_cubes: The number of cubes visited during the search.
            max_queue_size: The maximum size of the queue during the search.
            runtime: The time taken to perform the search.
            found_goal: Boolean flag indicating if the goal was found.
            algorithm: The name of the algorithm used.
            current_map_file: The name of the current map file used for the search.
            memory_tracing_enabled: A boolean flag indicating if memory tracing is enabled.
        """
        if memory_tracing_enabled:
            return None
        with open("results/Stats.csv", "a", newline="") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow([algorithm, path_length, visited_cubes, max_queue_size, runtime, found_goal, current_map_file if current_map_file else 'not found'])
        logging.info(f"Stats: {algorithm} => path_len: {path_length}, visited_cubes: {visited_cubes}, max_queue_size: {max_queue_size}, runtime: {runtime}, found_goal: {found_goal}, map: {current_map_file if current_map_file else 'na'}")

    @staticmethod
    def save_memory_statistics(stat, algorithm: str, map_file) -> None:
        """
        Saves memory consumption statistics to a CSV file.

        Args:
            stat: An object containing memory usage statistics.
            algorithm: The name of the algorithm used.
            map_file: The name of the map file used.
        """
        with open("results/Memory-Consumption.csv", "a", newline="") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow([algorithm, map_file if map_file else 'not found', stat.size / 1024, stat.count, stat.size / stat.count])