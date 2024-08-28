import pygame
import time
from collections import deque
import heapq
import csv
import logging

class Algorithms:
    def __init__(self, grid):
        self.grid = grid
        self.visited_cubes = set()
    @staticmethod
    def generate_path(previous_cube, current_cube):
        path = [current_cube]
        while current_cube in previous_cube:
            current_cube = previous_cube[current_cube]
            path.append(current_cube)
        path.reverse()  # Start from start_cube
        return path
    def clear_path(self):
        for (x, y) in self.visited_cubes:
            self.grid.grid[y][x].color = "white"
        self.visited_cubes.clear()

    def get_neighbors(self, x, y):
        neighbors = []
        for (move_x, move_y) in [(-1, 0), (1, 0), (0, -1), (0, 1)]: # left, right, up, down
            new_x, new_y = x + move_x, y + move_y
            if 0 <= new_x < self.grid.cols and 0 <= new_y < self.grid.rows and self.grid.grid[new_y][new_x].traversable:
                neighbors.append((new_x, new_y))
        return neighbors

    def bfs(self, screen, cube_size, offset_x, offset_y, trace_memory_enabled):
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

    def dfs(self, screen, cube_size, offset_x, offset_y, trace_memory_enabled):
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
        return abs(a[0] - b[0]) + abs(a[1] - b[1]) # manhattan distance

    def a_star(self, screen, cube_size, offset_x, offset_y, trace_memory_enabled):
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

    def dijkstra(self, screen, cube_size, offset_x, offset_y, trace_memory_enabled):
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

    def greedy_best_first_search(self, screen, cube_size, offset_x, offset_y, trace_memory_enabled):
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