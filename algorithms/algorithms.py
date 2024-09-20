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
    def generate_path(previous_cube, current_cube) -> list:
        """
        Generates a path from the start to the current cube using the previous_cube mapping.

        Args:
            previous_cube: A dictionary mapping each cube to the cube it came from.
            current_cube: The ending cube from which the path is generated.

        Returns:
            A list of cubes representing the path from start to the current cube.
        """
        path = [current_cube] # current cube is goal
        while current_cube in previous_cube:
            current_cube = previous_cube[current_cube]
            path.append(current_cube)
        path.reverse() # reverse list for correct order (start to goal)
        return path

    def clear_path(self) -> None:
        """Clears the path by resetting the color of all visited cubes to white."""
        for (x, y) in self.visited_cubes:
            self.grid.grid[y][x].color = "white"
        self.visited_cubes.clear()

    def get_neighbors(self, x: int, y: int):
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
            # make sure new coordinates are within the grid + traversable
            if 0 <= new_x < self.grid.cols and 0 <= new_y < self.grid.rows and self.grid.grid[new_y][new_x].traversable:
                neighbors.append((new_x, new_y))
        return neighbors

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
        # do not save stats with memory_tracing_enabled to not alter runs with higher runtime due to tracemalloc slowing the process down
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
        start_time = time.perf_counter() # get start_time for runtime-calculation
        queue = deque([self.grid.start_cube]) # initialize queue with start_cube
        previous_cube = {} # dictionary to track the path (cube to its predecessor)
        self.visited_cubes = {self.grid.start_cube} # keep track of visited cubes
        max_queue_size = 1 # track max size of queue
        while queue:
            # handle window close while algorithm is running
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

            max_queue_size = max(1, len(queue)) # update max queue size
            current_cube = queue.popleft() # get first element to process from queue

            # goal found
            if current_cube == self.grid.goal_cube:
                path = self.generate_path(previous_cube, current_cube)
                runtime = time.perf_counter() - start_time
                self.save_statistics(len(path) - 2, len(self.visited_cubes) - 1, max_queue_size, runtime, True, "BFS", self.grid.current_map_file, trace_memory_enabled) # -1 to remove start
                return path

            # process neighbors of current_cube
            for neighbor in self.get_neighbors(*current_cube):
                if neighbor not in self.visited_cubes:
                    previous_cube[neighbor] = current_cube # map current_cube to previous_cube
                    queue.append(neighbor) # add neighbor to queue to get processed next
                    self.visited_cubes.add(neighbor) # mark cube as visited
                    self.grid.grid[neighbor[1]][neighbor[0]].color = "yellow" # update color of cube to yellow
                    # add cube to list of dirty_rects for updating the screen
                    self.grid.dirty_rects.append(self.grid.draw_cube(screen, neighbor[0], neighbor[1], cube_size, offset_x, offset_y))

            pygame.display.update(self.grid.dirty_rects) # update parts of screen where dirty_rects are
            self.grid.dirty_rects.clear() # clear dirty_rects

        # if no path to goal is found
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
        start_time = time.perf_counter() # get start_time for runtime-calculation
        stack = [self.grid.start_cube] # initialize stack with start_cube
        previous_cube = {}  # dictionary to track the path (cube to its predecessor)
        self.visited_cubes = {self.grid.start_cube} # keep track of visited cubes
        max_stack_size = 1 # track max size of stack
        while stack:
            # handle window close while algorithm is running
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

            max_stack_size = max(1, len(stack)) # update max stack size
            current_cube = stack.pop() # get top cube from stack

            # goal found
            if current_cube == self.grid.goal_cube:
                path = self.generate_path(previous_cube, current_cube)
                runtime = time.perf_counter() - start_time
                self.save_statistics(len(path) - 2, len(self.visited_cubes) - 1, max_stack_size, runtime, True, "DFS", self.grid.current_map_file, trace_memory_enabled)  # -1 to remove start
                return path

            # process neighbors of current_cube
            for neighbor in self.get_neighbors(*current_cube):
                if neighbor not in self.visited_cubes:
                    previous_cube[neighbor] = current_cube # map current_cube to previous_cube
                    stack.append(neighbor) # add neighbor to stack to get processed next
                    self.visited_cubes.add(neighbor) # mark cube as visited
                    self.grid.grid[neighbor[1]][neighbor[0]].color = "yellow" # update color of cube to yellow
                    # add cube to list of dirty_rects for updating the screen
                    self.grid.dirty_rects.append(self.grid.draw_cube(screen, neighbor[0], neighbor[1], cube_size, offset_x, offset_y))

            pygame.display.update(self.grid.dirty_rects) # update parts of screen where dirty_rects are
            self.grid.dirty_rects.clear() # clear dirty_rects

        # if no path to goal is found
        logging.info("No path found.")
        runtime = time.perf_counter() - start_time
        self.save_statistics(0, len(self.visited_cubes) - 1, max_stack_size, runtime, False, "DFS", self.grid.current_map_file, trace_memory_enabled)  # -1 to remove start
        return None

    @staticmethod
    def heuristic(neighbor_cube, goal_cube):
        """
        Calculates the heuristic value (Manhattan distance) between the neighbor cube and the goal cube.

        Args:
            neighbor_cube: The coordinates of the neighbor cube.
            goal_cube: The coordinates of the goal cube.

        Returns:
            The Manhattan distance between the neighbor cube and the goal cube.
        """
        return abs(neighbor_cube[0] - goal_cube[0]) + abs(neighbor_cube[1] - goal_cube[1])

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
        start_time = time.perf_counter() # get start_time for runtime-calculation
        open_set = [] # initialize open_set to store cubes for exploration
        heapq.heappush(open_set, (0, self.grid.start_cube))  # add start_cube to open_set with f_score of 0
        previous_cube = {} # dictionary to track the path (cube to its predecessor)
        g_score = {self.grid.start_cube: 0} # dictionary to track the cost of each cube
        self.visited_cubes = {self.grid.start_cube} # keep track of visited cubes
        max_queue_size = 1 # track max size of open_set during search
        while open_set:
            # handle window close while algorithm is running
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

            max_queue_size = max(max_queue_size, len(open_set)) # update max queue size
            current_cube = heapq.heappop(open_set)[1] # get cube with lowest f_score from open_set

            # goal found
            if current_cube == self.grid.goal_cube:
                path = self.generate_path(previous_cube, current_cube)
                runtime = time.perf_counter() - start_time
                self.save_statistics(len(path) - 2, len(self.visited_cubes) - 1, max_queue_size ,runtime, True, "A*", self.grid.current_map_file, trace_memory_enabled)  # -2: remove start + goal || -1: remove start
                return path

            # process neighbors of current_cube
            for neighbor in self.get_neighbors(*current_cube):
                temp_g_score = g_score[current_cube] + 1  # calculate temp_g_score for neighbor (all edges have a weight of 1)
                if neighbor not in g_score or temp_g_score < g_score[neighbor]:
                    self.visited_cubes.add(neighbor) # mark cube as visited
                    g_score[neighbor] = temp_g_score # set/update g_score of the neighbor
                    f_score = temp_g_score + self.heuristic(neighbor, self.grid.goal_cube) # f_score = heuristic (h_score) + g_score
                    heapq.heappush(open_set, (f_score, neighbor)) # push neighbor into open_set with its f_score
                    previous_cube[neighbor] = current_cube # map current_cube to previous_cube
                    self.grid.grid[neighbor[1]][neighbor[0]].color = "yellow" # update color of cube to yellow
                    # add cube to list of dirty_rects for updating the screen
                    self.grid.dirty_rects.append(self.grid.draw_cube(screen, neighbor[0], neighbor[1], cube_size, offset_x, offset_y))

            pygame.display.update(self.grid.dirty_rects) # update parts of screen where dirty_rects are
            self.grid.dirty_rects.clear() # clear dirty_rects

        # if no path to goal is found
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
        start_time = time.perf_counter() # get start_time for runtime-calculation
        open_set = [] # initialize open_set to store cubes for exploration
        heapq.heappush(open_set, (0, self.grid.start_cube))  # add start_cube to open_set with f_score of 0
        previous_cube = {} # dictionary to track the path (cube to its predecessor)
        g_score = {self.grid.start_cube: 0} # dictionary to track the cost of each cube
        self.visited_cubes = {self.grid.start_cube}  # keep track of visited cubes
        max_queue_size = 1 # track max size of open_set during search
        while open_set:
            # handle window close while algorithm is running
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

            max_queue_size = max(max_queue_size, len(open_set)) # update max queue size
            current_cube = heapq.heappop(open_set)[1] # get cube with lowest g_score

            # goal found
            if current_cube == self.grid.goal_cube:
                path = self.generate_path(previous_cube, current_cube)
                runtime = time.perf_counter() - start_time
                self.save_statistics(len(path) - 2, len(self.visited_cubes) - 1, max_queue_size, runtime, True, "Dijkstra", self.grid.current_map_file, trace_memory_enabled)
                return path

            # process neighbors of current_cube
            for neighbor in self.get_neighbors(*current_cube):
                temp_g_score = g_score[current_cube] + 1  # all edges have a weight of 1
                if neighbor not in g_score or temp_g_score < g_score[neighbor]:
                    self.visited_cubes.add(neighbor) # mark cube as visited
                    g_score[neighbor] = temp_g_score # set/update g_score of the neighbor
                    heapq.heappush(open_set, (temp_g_score, neighbor)) # push neighbor into open_set with its g_score
                    previous_cube[neighbor] = current_cube # map current_cube to previous_cube
                    self.grid.grid[neighbor[1]][neighbor[0]].color = "yellow" # update color of cube to yellow
                    # add cube to list of dirty_rects for updating the screen
                    self.grid.dirty_rects.append(self.grid.draw_cube(screen, neighbor[0], neighbor[1], cube_size, offset_x, offset_y))

            pygame.display.update(self.grid.dirty_rects) # update parts of screen where dirty_rects are
            self.grid.dirty_rects.clear() # clear dirty_rects

        # if no path to goal is found
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
        start_time = time.perf_counter() # get start_time for runtime-calculation
        open_set = [] # initialize open_set to store cubes for exploration
        heapq.heappush(open_set, (0, self.grid.start_cube))  # add start_cube to open_set with h_score of 0
        previous_cube = {} # dictionary to track the path (cube to its predecessor)
        self.visited_cubes = {self.grid.start_cube} # keep track of visited cubes
        max_queue_size = 1 # track max size of open_set during search
        while open_set:
            # handle window close while algorithm is running
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

            max_queue_size = max(max_queue_size, len(open_set)) # update max queue size
            current_cube = heapq.heappop(open_set)[1] # get cube with lowest h_score

            # goal found
            if current_cube == self.grid.goal_cube:
                path = self.generate_path(previous_cube, current_cube)
                runtime = time.perf_counter() - start_time
                self.save_statistics(len(path) - 2, len(self.visited_cubes) - 1, max_queue_size, runtime, True, "Greedy-BeFs", self.grid.current_map_file, trace_memory_enabled)
                return path

            # process neighbors of current_cube
            for neighbor in self.get_neighbors(*current_cube):
                if neighbor not in self.visited_cubes:
                    self.visited_cubes.add(neighbor) # mark cube as visited
                    h_score = self.heuristic(neighbor, self.grid.goal_cube) # calculate heuristic score (h_score) from neighbor to goal_cube
                    heapq.heappush(open_set, (h_score, neighbor)) # push neighbor into open_set with its h_score
                    previous_cube[neighbor] = current_cube # map current_cube to previous_cube
                    self.grid.grid[neighbor[1]][neighbor[0]].color = "yellow" # update color of cube to yellow
                    # add cube to list of dirty_rects for updating the screen
                    self.grid.dirty_rects.append(self.grid.draw_cube(screen, neighbor[0], neighbor[1], cube_size, offset_x, offset_y))

            pygame.display.update(self.grid.dirty_rects) # update parts of screen where dirty_rects are
            self.grid.dirty_rects.clear() # clear dirty_rects

        # if no path to goal is found
        logging.info("No path found.")
        runtime = time.perf_counter() - start_time
        self.save_statistics(0, len(self.visited_cubes) - 1, max_queue_size, runtime, False, "Greedy-BeFs", self.grid.current_map_file, trace_memory_enabled)
        return None