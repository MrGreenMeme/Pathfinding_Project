import pygame

class ToggleButton:
    """
    Represents a toggle button in a Pygame application.

    Attributes:
        rect:  The pygame.Rect object defining the button's position and size.
        offset_x: The horizontal offset from the right edge of the window.
        font: The Pygame font object used to render the button's text.
        text: The text displayed on the button.
        state: A boolean indicating whether the button is on (True) or off (False).
        color_on: The color of the button when it is in the 'on' state.
        color_off: The color of the button when it is in the 'off' state.
    """
    def __init__(self, x: int, y: int, width: int, height: int, offset_x: int, font: pygame.font.Font, text: str):
        """Initializes the ToggleButton with position, size, font, text, and state.

         Args:
             x: The x-coordinate of the button's top-left corner.
             y: The y-coordinate of the button's top-left corner.
             width: The width of the button.
             height: The height of the button.
             offset_x: The horizontal offset from the right edge of the window.
             font: The Pygame font object used to render the button's text.
             text: The text displayed on the button.
         """
        self.rect = pygame.Rect(x, y, width, height)
        self.offset_x = offset_x
        self.font = font
        self.text = text
        self.state = False
        self.color_on = pygame.Color('green')
        self.color_off = pygame.Color('grey')

    def draw(self, screen) -> None:
        """Draws the toggle button on the given screen surface.

        Args:
            screen: The Pygame surface on which to draw the button.
        """
        color = self.color_on if self.state else self.color_off
        pygame.draw.rect(screen, color, self.rect)
        text = self.font.render(self.text, True, "white")
        screen.blit(text, (self.rect.x + 3, self.rect.y + 10))
        pygame.display.update(self.rect)
    def handle_click(self) -> None:
        """Toggles the button state when it is clicked."""
        self.state = not self.state

    def shift(self, window_width: int) -> None:
        """Shifts the button horizontally based on the window width.

        Args:
            window_width: The width of the current window.
        """
        self.rect.x = window_width - self.offset_x