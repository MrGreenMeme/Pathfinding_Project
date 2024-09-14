import pygame
from grid import Grid, GridView
from algorithms import Algorithms
from ui import Toolbar, InputField, Dropdown, ToggleButton, DebugText
from tkinter import filedialog
import logging
import tracemalloc
import os

def main() -> None:
    """Main function to run the pathfinding application."""
    # pygame setup
    pygame.init()

    # logging setup
    logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s] %(asctime)s - %(message)s')

    # window setup
    window_width, window_height = 1000, 1000
    screen = pygame.display.set_mode((window_width, window_height), pygame.RESIZABLE)
    pygame.display.set_caption("Pathfinding")

    def redraw_screen(algorithm = None) -> None:
        """Redraw the entire screen.

        Args:
            algorithm: The algorithm currently running (optional).
        """
        screen.fill("white")
        toolbar.draw_toolbar(screen)
        input_field.draw(screen)
        dropdown.draw(screen)
        memory_tracing_toggle.draw(screen)
        run_ten_times_toggle.draw(screen)
        all_maps_toggle.draw(screen)
        for y in range(grid.rows):
            for x in range(grid.cols):
                grid.draw_cube(screen, x, y, int(grid_view.cube_size * grid_view.zoom_factor), grid_view.center_x, grid_view.center_y)

        if grid.current_map_file:
            debug_text.draw(screen, f"Current Map: {grid.current_map_file}", (10, grid_view.window_height - 30))

        if algorithm:
            debug_text.draw(screen, f"Running: {algorithm}", (grid_view.window_width - 170, grid_view.window_height - 30))

        pygame.display.flip()

    # grid setup
    rows, cols = (15, 15)
    grid = Grid(rows, cols)
    cube_size = 45

    # algorithms
    algorithms = Algorithms(grid)

    # grid_view setup
    grid_view = GridView(window_width, window_height, 1.0, 0.05, cube_size)

    # font setup
    font_input_field = pygame.font.Font(None, 28)
    font_drop_down = pygame.font.Font(None, 24)
    memory_tracing_toggle_button = pygame.font.Font(None, 12)
    run_ten_times_toggle_button = pygame.font.Font(None, 18)
    debug_font = pygame.font.Font(None, 22)

    # input field setup
    input_field = InputField(window_width - 270, 10, 100, 30, 270, font_input_field, pygame.Color('grey75'), pygame.Color('grey0'), redraw_screen)

    # dropdown setup
    dropdown = Dropdown(window_width - 400, 10, 120, 25, 400, font_drop_down, ["DFS", "BFS", "A*", "Dijkstra", "Greedy-BeFs", "Run all"])

    # toggle button setup
    memory_tracing_toggle = ToggleButton(window_width - 160, 10, 60, 30, 160, memory_tracing_toggle_button, "Trace-Memory")
    run_ten_times_toggle = ToggleButton(window_width - 90, 10, 30, 30, 90, run_ten_times_toggle_button, "10x")
    all_maps_toggle = ToggleButton(window_width - 50, 10, 40, 30, 50, memory_tracing_toggle_button, "All maps")

    # debug text setup
    debug_text = DebugText(debug_font, "black")

    # toolbar setup
    def load_image(file_path: str, size: int):
        """Load and scale an image.

        Args:
            file_path: Path to the image file.
            size: Size to scale the image to.

        Returns:
            pygame.Surface: The scaled image surface.
        """
        image = pygame.image.load(file_path)
        image = pygame.transform.scale(image, (size, size))
        return image.convert()

    tool_size = 50
    flag_img = load_image('assets/images/flag.png', tool_size)
    eraser_img = load_image('assets/images/eraser.png', tool_size)
    play_img = load_image('assets/images/play.png', tool_size)
    clear_img = load_image('assets/images/clear.png', tool_size)
    save_img = load_image('assets/images/save.png', tool_size)
    load_img = load_image('assets/images/load.png', tool_size)
    toolbar = Toolbar([("start", "green"), ("goal", flag_img), ("obstacle", "grey"), ("eraser", eraser_img), ("play", play_img), ("clear", clear_img), ("save", save_img), ("load", load_img)], 50, 10)

    # center grid
    grid_view.center_grid(grid.rows, grid.cols)

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
    def run_algorithm(grid, algorithms, grid_view, screen, algorithm: str) -> None:
        """Run a specified pathfinding algorithm.

        Args:
            grid: The grid object representing the map.
            algorithms: The algorithms object for pathfinding.
            grid_view: The view settings for the grid.
            screen: The display surface object.
            algorithm: The algorithm to run.
        """
        pathfinding_algorithms = {
            "DFS": algorithms.dfs,
            "BFS": algorithms.bfs,
            "A*": algorithms.a_star,
            "Dijkstra": algorithms.dijkstra,
            "Greedy-BeFs": algorithms.greedy_best_first_search
        }
        if algorithm in pathfinding_algorithms:

            algo_runs = 10 if run_ten_times_toggle.state else 1

            for _ in range(algo_runs):
                algorithms.clear_path()
                redraw_screen(algorithm)

                if memory_tracing_toggle.state:
                    tracemalloc.start()

                path = pathfinding_algorithms[algorithm](screen, int(grid_view.cube_size * grid_view.zoom_factor), grid_view.center_x, grid_view.center_y, memory_tracing_toggle.state)

                if memory_tracing_toggle.state:
                    snapshot = tracemalloc.take_snapshot()
                    top_stats = snapshot.statistics('filename')
                    algorithms.save_memory_statistics(top_stats[0], algorithm, grid.current_map_file)
                    tracemalloc.stop()

                if path:
                    grid.draw_path(path, screen, int(grid_view.cube_size * grid_view.zoom_factor), grid_view.center_x, grid_view.center_y)

    def run_all_algorithms(grid, algorithms, grid_view, screen) -> None:
        """Run all pathfinding algorithms in sequence.

        Args:
            grid: The grid object representing the map.
            algorithms: The algorithms object for pathfinding.
            grid_view: The view settings for the grid.
            screen: The display surface object.
        """
        algorithm_options = ["DFS", "BFS", "A*", "Dijkstra", "Greedy-BeFs"]
        for algorithm in algorithm_options:
            run_algorithm(grid, algorithms, grid_view, screen, algorithm)
            pygame.time.wait(500)

    def run_all_maps(grid, algorithms, grid_view, screen, selected_dropdown_option: str) -> None:
        """Run algorithms on all maps in the directory.

        Args:
            grid: The grid object representing the map.
            algorithms: The algorithms object for pathfinding.
            grid_view: The view settings for the grid.
            screen: The display surface object.
            selected_dropdown_option: The selected algorithm-option.
        """
        if selected_dropdown_option is None:
            return None

        map_dir = "maps"
        map_files = [f for f in os.listdir(map_dir) if f.endswith('.txt')]
        sorted_map_files = sorted(map_files, key=lambda map_name: [int(part) for part in map_name.replace('.txt', '').split('_') if part.isdigit()])

        for map_file in sorted_map_files:
            algorithms.visited_cubes.clear()

            map_path = os.path.join(map_dir, map_file).replace("\\", "/")
            grid.load_grid(map_path)
            grid_view.calculate_zoom_factor(grid.rows, grid.cols)
            grid_view.center_grid(grid.rows, grid.cols)
            redraw_screen()

            if selected_dropdown_option == "Run all":
                run_all_algorithms(grid, algorithms, grid_view, screen)
            else:
                run_algorithm(grid, algorithms, grid_view, screen, selected_dropdown_option)

    while running:
        clock.tick(60)
        # poll for events
        # pygame.QUIT event means the user clicked X to close your window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if toolbar.selected_tool == 7 and event.button == 1: # import grid
                toolbar.selected_tool = None
                map_dir = os.getcwd() + "/maps"
                filename = filedialog.askopenfilename(initialdir=map_dir, filetypes=[("Text files", "*.txt")])
                if filename:
                    algorithms.visited_cubes.clear()
                    grid.load_grid(filename)
                    grid_view.calculate_zoom_factor(grid.rows, grid.cols)
                    logging.debug(f"Grid imported. Calculated zoom factor: {grid_view.zoom_factor}")
                    grid_view.center_grid(grid.rows, grid.cols)
                    redraw_screen()

            elif event.type == pygame.VIDEORESIZE:
                new_window_width, new_window_height = event.size
                grid_view.window_width, grid_view.window_height = new_window_width, new_window_height
                logging.debug("New window_width: " +  str(new_window_width) + " new window_height: " + str(new_window_height))

                screen = pygame.display.set_mode((new_window_width, new_window_height), pygame.RESIZABLE)
                grid_view.calculate_zoom_factor(grid.rows, grid.cols)
                grid_view.center_grid(grid.rows, grid.cols)
                input_field.shift(new_window_width)
                dropdown.shift(new_window_width)
                memory_tracing_toggle.shift(new_window_width)
                run_ten_times_toggle.shift(new_window_width)
                all_maps_toggle.shift(new_window_width)
                redraw_screen()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # only accept left-click
                    x,y = event.pos
                    if toolbar.toolbar_rect.collidepoint(event.pos): # toolbar
                        if toolbar.handle_click(x, y):
                            toolbar.draw_toolbar(screen)
                        if toolbar.selected_tool == 4: # start algo
                            algorithms.clear_path()
                            redraw_screen()
                            if all_maps_toggle.state:
                                run_all_maps(grid, algorithms, grid_view, screen, dropdown.selected)
                            else:
                                if dropdown.selected in ["DFS", "BFS", "A*", "Dijkstra", "Greedy-BeFs"] and grid.start_cube and grid.goal_cube:
                                    run_algorithm(grid, algorithms, grid_view, screen, dropdown.selected)
                                elif dropdown.selected == "Run all" and grid.start_cube and grid.goal_cube:
                                    run_all_algorithms(grid, algorithms, grid_view, screen)
                        if toolbar.selected_tool == 5: # clear algo
                            algorithms.clear_path()
                            redraw_screen()
                        if toolbar.selected_tool == 6: # export grid
                            grid.export_grid()
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
                    elif all_maps_toggle.rect.collidepoint(event.pos):  # toggle button
                        all_maps_toggle.handle_click()
                        all_maps_toggle.draw(screen)
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
                            grid.handle_click(x, y, screen, int(grid_view.cube_size * grid_view.zoom_factor), grid_view.center_x, grid_view.center_y, toolbar.selected_tool)

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
                        grid_view.center_x += shift_x
                        grid_view.center_y += shift_y
                        move_grid_x = x
                        move_grid_y = y
                    else:
                        grid.handle_click(x, y, screen, int(grid_view.cube_size * grid_view.zoom_factor), grid_view.center_x, grid_view.center_y, toolbar.selected_tool)

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    grid_view.zoom_factor += grid_view.zoom_increment
                    logging.debug(f"Zoomed in. New zoom factor: {grid_view.zoom_factor} + {int(grid_view.cube_size * grid_view.zoom_factor)}")
                    grid_view.center_grid(grid.rows, grid.cols)
                    redraw_screen()
                elif event.key == pygame.K_DOWN:
                    grid_view.zoom_factor = max(grid_view.zoom_increment, grid_view.zoom_factor - grid_view.zoom_increment)
                    logging.debug(f"Zoomed out. New zoom factor: {grid_view.zoom_factor} + {int(grid_view.cube_size * grid_view.zoom_factor)}")
                    grid_view.center_grid(grid.rows, grid.cols)
                    redraw_screen()
                input_field.handle_input(event, screen, grid, grid_view)

        grid.redraw_dirty_rects(screen, int(grid_view.cube_size * grid_view.zoom_factor), grid_view.center_x, grid_view.center_y)

    pygame.quit()