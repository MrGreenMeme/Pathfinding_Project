class GridView:
    """
    A class managing the view settings for displaying a grid in a Pygame window.

    Attributes:
        window_width: The width of the Pygame window.
        window_height: The height of the Pygame window.
        zoom_factor: The current zoom factor applied to the grid.
        zoom_increment: The increment by which the zoom factor can be adjusted.
        cube_size: The size of each cube (cell) in the grid.
        center_x: The x-coordinate of the grid's center position on the screen.
        center_y: The y-coordinate of the grid's center position on the screen.
    """
    def __init__(self, window_width: int, window_height: int, zoom_factor: float, zoom_increment: float, cube_size: int):
        """
        Initializes the GridView with the given window dimensions, zoom settings, and cube size.

        Args:
            window_width: The width of the Pygame window.
            window_height: The height of the Pygame window.
            zoom_factor: The initial zoom factor applied to the grid.
            zoom_increment: The increment by which the zoom factor can be adjusted.
            cube_size: The size of each cube (cell) in the grid.
        """
        self.window_width = window_width
        self.window_height = window_height
        self.zoom_factor = zoom_factor
        self.zoom_increment = zoom_increment
        self.cube_size = cube_size
        self.center_x = 0
        self.center_y = 0

    def calculate_zoom_factor(self, grid_rows: int, grid_cols: int) -> None:
        """
        Calculates and sets the appropriate zoom factor based on the grid dimensions
        and the size of the Pygame window.

        Args:
            grid_rows: The number of rows in the grid.
            grid_cols: The number of columns in the grid.
        """
        required_zoom_x = self.window_width / (grid_cols * self.cube_size)
        required_zoom_y = self.window_height / (grid_rows * self.cube_size)
        self.zoom_factor = min(required_zoom_x, required_zoom_y)

    def center_grid(self, grid_rows: int, grid_cols: int) -> None:
        """
        Centers the grid within the Pygame window based on the grid dimensions and the current zoom factor.

        Args:
            grid_rows: The number of rows in the grid.
            grid_cols: The number of columns in the grid.
        """
        grid_width = grid_cols * int(self.cube_size * self.zoom_factor)
        grid_height = grid_rows * int(self.cube_size * self.zoom_factor)
        self.center_x = (self.window_width - grid_width) // 2
        self.center_y = (self.window_height - grid_height) // 2