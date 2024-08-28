class View:
    def __init__(self, window_width, window_height, zoom_factor, zoom_increment, cube_size, debug_font):
        self.window_width = window_width
        self.window_height = window_height
        self.zoom_factor = zoom_factor
        self.zoom_increment = zoom_increment
        self.cube_size = cube_size
        self.debug_font = debug_font
        self.center_x = 0
        self.center_y = 0

    def calculate_zoom_factor(self, grid_rows, grid_cols):
        required_zoom_x = self.window_width / (grid_cols * self.cube_size)
        required_zoom_y = self.window_height / (grid_rows * self.cube_size)
        self.zoom_factor = min(required_zoom_x, required_zoom_y)

    def center_grid(self, grid_rows, grid_cols):
        grid_width = grid_cols * int(self.cube_size * self.zoom_factor)
        grid_height = grid_rows * int(self.cube_size * self.zoom_factor)
        self.center_x = (self.window_width - grid_width) // 2
        self.center_y = (self.window_height - grid_height) // 2

    def draw_debug_text(self, screen, debug_text, position):
        text_surface = self.debug_font.render(debug_text, True, "black")
        screen.blit(text_surface, position)