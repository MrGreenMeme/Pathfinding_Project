# Example file showing a basic pygame "game loop"
import pygame


class Cube:
    def __init__(self, color, traversable=True):
        self.color = color
        self.traversable = traversable


class Grid:
    def __init__(self, rows, cols, cube_size):
        self.rows = rows
        self.cols = cols
        self.cube_size = cube_size
        self.grid = [[Cube("white", True) for i in range(cols)] for j in range(rows)]

    def draw_cube(self, screen, x, y, center_x, center_y):
        cube = self.grid[y][x]
        # inside cell
        pygame.draw.rect(screen, cube.color, (center_x + x * self.cube_size, center_y + y * self.cube_size, self.cube_size, self.cube_size))
        # outline of cell
        pygame.draw.rect(screen, "black", (center_x + x * self.cube_size, center_y + y * self.cube_size, self.cube_size, self.cube_size), 1)


# pygame setup
pygame.init()

# grid setup
rows, cols = (5, 5)
cube_size = 50
grid = Grid(rows, cols, cube_size)

# window setup
window_width, window_height = 1000, 1000
screen = pygame.display.set_mode((window_width, window_height), pygame.RESIZABLE)
pygame.display.set_caption("Pathfinding")

# center grid
def center_grid(window_width, window_height, grid_width, grid_height):
    new_center_x = (window_width - grid_width) // 2
    new_center_y = (window_height - grid_height) // 2
    return new_center_x, new_center_y

grid_width = cols * cube_size
grid_height = rows * cube_size
center_x, center_y = center_grid(window_width, window_height, grid_width, grid_height)

# Game loop
clock = pygame.time.Clock()
running = True

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.VIDEORESIZE:
            new_window_width, new_window_height = event.size
            print("x: " +  str(new_window_width) + " y: " + str(new_window_height))

            screen = pygame.display.set_mode((new_window_width, new_window_height), pygame.RESIZABLE)
            center_x, center_y = center_grid(new_window_width, new_window_height, grid_width, grid_height)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            x,y = event.pos
            print("x: " +  str(x) + " y: " + str(y))

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("white")

    for y in range(grid.rows):
        for x in range(grid.cols):
            grid.draw_cube(screen, x, y, center_x, center_y)

            # RENDER YOUR GAME HERE

    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(144)  # limits FPS to 144

pygame.quit()
