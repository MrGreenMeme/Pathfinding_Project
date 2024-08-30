import pygame

class Dropdown:
    """
    Represents a dropdown menu in a Pygame application.

    Attributes:
        rect: The pygame.Rect object defining the dropdowns position and size.
        offset_x: The horizontal offset from the right edge of the window.
        font: The Pygame font object used to render the dropdown options.
        options: A list of strings representing the dropdown menu options.
        option_rect: The pygame.Rect object defining the area where the dropdown options are displayed.
        selected: The currently selected option from the dropdown, or None if no option is selected.
        open: A boolean indicating whether the dropdown menu is currently open.
    """
    def __init__(self, x: int, y: int, width: int, height: int, offset_x: int, font: pygame.font.Font, options: list):
        """Initializes the Dropdown with position, size, font, options, and offset.

        Args:
            x: The x-coordinate of the dropdowns top-left corner.
            y: The y-coordinate of the dropdowns top-left corner.
            width: The width of the dropdown.
            height: The height of the dropdown.
            offset_x: The horizontal offset from the right edge of the window.
            font: The Pygame font object used to render the dropdown options.
            options: A list of strings representing the dropdown menu options.
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.offset_x = offset_x
        self.font = font
        self.options = options
        self.option_rect = pygame.Rect(0, 0, 0, 0)
        self.selected = None
        self.open = False

    def handle_click(self, event) -> None:
        """Handles mouse click events to open/close the dropdown and select options.

       Args:
           event: A Pygame event object containing information about the mouse click.
       """
        if self.rect.collidepoint(event.pos):
            self.open = not self.open
        elif self.open:
            for i, option in enumerate(self.options):
                option_rect = pygame.Rect(self.rect.x, self.rect.y + (i + 1) * self.rect.height, self.rect.width, self.rect.height)
                if option_rect.collidepoint(event.pos):
                    self.selected = option
                    self.open = False

    def draw(self, screen) -> None:
        """Draws the dropdown menu on the given screen surface.

        Args:
            screen: The Pygame surface on which to draw the dropdown.
        """
        pygame.draw.rect(screen, "white", self.rect) # clear previous color
        pygame.draw.rect(screen, "grey" if self.open else "black", self.rect)
        text = self.font.render(self.selected if self.selected else "Select Algo", True, "white")
        screen.blit(text, (self.rect.x + 5, self.rect.y + 5))

        if self.open:
            for i, option in enumerate(self.options):
                option_rect = pygame.Rect(self.rect.x, self.rect.y + (i + 1) * self.rect.height, self.rect.width, self.rect.height)
                pygame.draw.rect(screen, "black", option_rect)
                option_text = self.font.render(option, True, "white")
                screen.blit(option_text, (option_rect.x + 5, option_rect.y + 5))
            self.option_rect = pygame.Rect(self.rect.x, self.rect.y + self.rect.height, self.rect.width, self.rect.height * len(self.options))
            pygame.display.flip()
        else:
            pygame.draw.rect(screen, "white", self.option_rect)
            self.option_rect = pygame.Rect(0, 0, 0, 0)
            pygame.display.flip()

    def shift(self, window_width: int) -> None:
        """Shifts the dropdown menu horizontally based on the window width.

        Args:
            window_width: The width of the window, used to position the dropdown.
        """
        self.rect.x = window_width - self.offset_x