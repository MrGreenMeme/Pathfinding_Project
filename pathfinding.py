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
        self.grid = [[Cube("green", True) for i in range(cols)] for j in range(rows)]

    def draw_cube(self, screen, x, y):
        cube = self.grid[y][x]
        # inside cell
        pygame.draw.rect(screen, cube.color, (x * self.cube_size, y * self.cube_size, self.cube_size, self.cube_size))
        # outline of cell
        pygame.draw.rect(screen, "black", (x * self.cube_size, y * self.cube_size, self.cube_size, self.cube_size), 1)


# pygame setup
pygame.init()
rows, cols = (5, 5)
cube_size = 50
grid = Grid(rows, cols, cube_size)
screen = pygame.display.set_mode((1000, 1000))
clock = pygame.time.Clock()
running = True

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("white")

    for y in range(grid.rows):
        for x in range(grid.cols):
            grid.draw_cube(screen, x, y)

            # RENDER YOUR GAME HERE

    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(144)  # limits FPS to 144

pygame.quit()
