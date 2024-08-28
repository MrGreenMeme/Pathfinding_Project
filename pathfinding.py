import pygame
import datetime
from grid import Grid, View
from algorithms import Algorithms
from ui import Toolbar, InputField, Dropdown, ToggleButton
from tkinter import filedialog
import logging
import tracemalloc
import os

def main():
    # pygame setup
    pygame.init()

    # logging setup
    logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s] %(asctime)s - %(message)s')

    # window setup
    window_width, window_height = 1000, 1000
    screen = pygame.display.set_mode((window_width, window_height), pygame.RESIZABLE)
    pygame.display.set_caption("Pathfinding")

    def redraw_screen(algorithm = None):
        screen.fill("white")
        toolbar.draw_toolbar(screen)
        input_field.draw(screen)
        dropdown.draw(screen)
        memory_tracing_toggle.draw(screen)
        run_ten_times_toggle.draw(screen)
        all_maps_toggle.draw(screen)
        for y in range(grid.rows):
            for x in range(grid.cols):
                grid.draw_cube(screen, x, y, int(view.cube_size * view.zoom_factor), view.center_x, view.center_y)

        if grid.current_map_file:
            view.draw_debug_text(screen, f"Current Map: {grid.current_map_file}", (10, view.window_height - 30))

        if algorithm:
            view.draw_debug_text(screen, f"Running: {algorithm}", (view.window_width - 170, view.window_height - 30))

        pygame.display.flip()

    # grid setup
    rows, cols = (15, 15)
    grid = Grid(rows, cols)
    cube_size = 45

    # algorithms
    algorithms = Algorithms(grid)

    # view setup
    debug_font = pygame.font.Font(None, 22)
    view = View(window_width, window_height, 1.0, 0.05, cube_size, debug_font)

    # font setup
    font_input_field = pygame.font.Font(None, 28)
    font_drop_down = pygame.font.Font(None, 24)
    memory_tracing_toggle_button = pygame.font.Font(None, 12)
    run_ten_times_toggle_button = pygame.font.Font(None, 18)

    # input field setup
    input_field = InputField(window_width - 270, 10, 100, 30, font_input_field, pygame.Color('grey75'), pygame.Color('grey0'), redraw_screen)

    # dropdown setup
    dropdown = Dropdown(window_width - 400, 10, 120, 25, font_drop_down, ["DFS", "BFS", "A*", "Dijkstra", "Greedy-BeFs", "Run all"])

    # toggle button setup
    memory_tracing_toggle = ToggleButton(window_width - 160, 10, 60, 30, 160, memory_tracing_toggle_button, "Trace-Memory")
    run_ten_times_toggle = ToggleButton(window_width - 90, 10, 30, 30, 90, run_ten_times_toggle_button, "10x")
    all_maps_toggle = ToggleButton(window_width - 50, 10, 40, 30, 50, memory_tracing_toggle_button, "All maps")

    # toolbar setup
    def load_image(file_path, size):
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
    view.center_grid(grid.rows, grid.cols)

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
    def run_algorithm(grid, algorithms, view, screen, algorithm):
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

                path = pathfinding_algorithms[algorithm](screen, int(view.cube_size * view.zoom_factor), view.center_x, view.center_y, memory_tracing_toggle.state)

                if memory_tracing_toggle.state:
                    snapshot = tracemalloc.take_snapshot()
                    top_stats = snapshot.statistics('filename')
                    algorithms.save_memory_statistics(top_stats[0], algorithm, grid.current_map_file)
                    tracemalloc.stop()

                if path:
                    for (x, y) in path:
                        grid.grid[y][x].color = "purple"
                        grid.dirty_rects.append(grid.draw_cube(screen, x, y, int(view.cube_size * view.zoom_factor), view.center_x, view.center_y))
                    pygame.display.flip()
                    grid.dirty_rects.clear()

    def run_all_algorithms(grid, algorithms, view, screen):
        algorithm_options = ["DFS", "BFS", "A*", "Dijkstra", "Greedy-BeFs"]
        for algorithm in algorithm_options:
            run_algorithm(grid, algorithms, view, screen, algorithm)
            pygame.time.wait(500)

    def run_all_maps(grid, algorithms, view, screen, selected_dropdown_option):
        if selected_dropdown_option is None:
            return None

        map_dir = "maps"
        map_files = [f for f in os.listdir(map_dir) if f.endswith('.txt')]
        sorted_map_files = sorted(map_files, key=lambda map_name: [int(part) for part in map_name.replace('.txt', '').split('_') if part.isdigit()])

        for map_file in sorted_map_files:
            grid.start_cube = None
            grid.goal_cube = None
            algorithms.visited_cubes.clear()

            map_path = os.path.join(map_dir, map_file).replace("\\", "/")
            grid.load_grid(map_path)
            view.calculate_zoom_factor(grid.rows, grid.cols)
            view.center_grid(grid.rows, grid.cols)
            redraw_screen()

            if selected_dropdown_option == "Run all":
                run_all_algorithms(grid, algorithms, view, screen)
            else:
                run_algorithm(grid, algorithms, view, screen, selected_dropdown_option)

    while running:
        clock.tick(60)
        # poll for events
        # pygame.QUIT event means the user clicked X to close your window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.VIDEORESIZE:
                new_window_width, new_window_height = event.size
                view.window_width, view.window_height = new_window_width, new_window_height
                logging.debug("New window_width: " +  str(new_window_width) + " new window_height: " + str(new_window_height))

                screen = pygame.display.set_mode((new_window_width, new_window_height), pygame.RESIZABLE)
                view.calculate_zoom_factor(grid.rows, grid.cols)
                view.center_grid(grid.rows, grid.cols)
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
                                run_all_maps(grid, algorithms, view, screen, dropdown.selected)
                            else:
                                if dropdown.selected in ["DFS", "BFS", "A*", "Dijkstra", "Greedy-BeFs"] and grid.start_cube and grid.goal_cube:
                                    run_algorithm(grid, algorithms, view, screen, dropdown.selected)
                                elif dropdown.selected == "Run all" and grid.start_cube and grid.goal_cube:
                                    run_all_algorithms(grid, algorithms, view, screen)
                        if toolbar.selected_tool == 5: # clear algo
                            algorithms.clear_path()
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
                                algorithms.visited_cubes.clear()
                                grid.load_grid(filename)
                                view.calculate_zoom_factor(grid.rows, grid.cols)
                                logging.debug(f"Grid imported. Calculated zoom factor: {view.zoom_factor}")
                                view.center_grid(grid.rows, grid.cols)
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
                            grid.handle_click(x, y, screen, int(view.cube_size * view.zoom_factor), view.center_x, view.center_y, toolbar.selected_tool)

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
                        view.center_x += shift_x
                        view.center_y += shift_y
                        move_grid_x = x
                        move_grid_y = y
                    else:
                        grid.handle_click(x, y, screen, int(view.cube_size * view.zoom_factor), view.center_x, view.center_y, toolbar.selected_tool)

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    view.zoom_factor += view.zoom_increment
                    logging.debug(f"Zoomed in. New zoom factor: {view.zoom_factor} + {int(view.cube_size * view.zoom_factor)}")
                    view.center_grid(grid.rows, grid.cols)
                    redraw_screen()
                elif event.key == pygame.K_DOWN:
                    view.zoom_factor = max(view.zoom_increment, view.zoom_factor - view.zoom_increment)
                    logging.debug(f"Zoomed out. New zoom factor: {view.zoom_factor} + {int(view.cube_size * view.zoom_factor)}")
                    view.center_grid(grid.rows, grid.cols)
                    redraw_screen()
                input_field.handle_input(event, screen, grid, view)

        # redraw only dirty rectangles
        for rect in grid.dirty_rects:
            pygame.draw.rect(screen, "white", rect)  # Clear the previous color
            # Redraw the cube in the dirty rect
            x = (rect.x - view.center_x) // int(view.cube_size * view.zoom_factor)
            y = (rect.y - view.center_y) // int(view.cube_size * view.zoom_factor)
            grid.draw_cube(screen, x, y, int(view.cube_size * view.zoom_factor), view.center_x, view.center_y)

        if grid.dirty_rects:
            pygame.display.flip()
            grid.dirty_rects.clear()

    pygame.quit()

if __name__ == '__main__':
    main()