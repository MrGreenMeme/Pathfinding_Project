import pygame
import logging
class InputField:
    """
   Represents an input field in a Pygame application.

   Attributes:
       rect: The pygame.Rect object defining the input field's position and size.
       offset_x: The horizontal offset from the right edge of the window.
       font: The Pygame font object used to render the input field's text.
       inactive_color: The color of the input field when it is inactive.
       active_color: The color of the input field when it is active.
       redraw_screen: A callback function to redraw the entire screen.
       color: The current color of the input field, depending on its active state.
       text: The current text entered into the input field.
       active: A boolean indicating whether the input field is active.
   """
    def __init__(self, x: int, y: int, width: int, height: int, offset_x: int, font: pygame.font.Font, inactive_color, active_color, redraw_screen):
        """Initializes the InputField with position, size, font, colors, and a redraw callback.

        Args:
            x: The x-coordinate of the input field's top-left corner.
            y: The y-coordinate of the input field's top-left corner.
            width: The width of the input field.
            height: The height of the input field.
            offset_x: The horizontal offset from the right edge of the window.
            font: The Pygame font object used to render the input field's text.
            inactive_color: The color of the input field when it is inactive.
            active_color: The color of the input field when it is active.
            redraw_screen: A callback function to redraw the entire screen.
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.offset_x = offset_x
        self.font = font
        self.inactive_color = inactive_color
        self.active_color = active_color
        self.redraw_screen = redraw_screen
        self.color = inactive_color
        self.text = ''
        self.active = False

    def handle_click(self, event) -> None:
        """Handles mouse click events to toggle the input field's active state and color.

       Args:
           event: A Pygame event object containing information about the mouse click.
       """
        if self.rect.collidepoint(event.pos):
            self.active = not self.active
        self.color = self.active_color if self.active else self.inactive_color

    def handle_input(self, event, screen, grid, grid_view) -> None:
        """Handles keyboard input events to update the input field's text.

       Args:
           event: A Pygame event object containing information about the keyboard input.
           screen: The Pygame surface on which to draw the input field.
           grid: The grid object that may be resized based on the input.
           grid_view: The grid_view object that manages the display of the grid.

       Raises:
           ValueError: If the input format is incorrect when trying to resize the grid.
       """
        if self.active:
            if event.key == pygame.K_RETURN:
                logging.debug(f"Entered: {self.text}")
                try:
                    new_rows, new_cols = map(int, self.text.lower().split('x'))
                    grid.resize_grid(new_rows, new_cols)
                    grid_view.calculate_zoom_factor(grid.rows, grid.cols)
                    grid_view.center_grid(grid.rows, grid.cols)
                    self.redraw_screen()
                except Exception:
                    logging.info("Format should be rowsxcols like 10x10")
                self.text = ''
                self.draw(screen)
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
                self.draw(screen)
            else:
                self.text += event.unicode
                self.draw(screen)

    def draw(self, screen) -> None:
        """Draws the input field on the given screen surface.

        Args:
            screen: The Pygame surface on which to draw the input field.
        """
        pygame.draw.rect(screen, "white", self)
        pygame.draw.rect(screen, self.color, self.rect, 2)
        text_surface = self.font.render(self.text, True, self.color)
        screen.blit(text_surface, (self.rect.x + 5, self.rect.y + 5))
        pygame.display.update(self.rect)

    def shift(self, window_width: int) -> None:
        """Shifts the input field horizontally based on the window width.

        Args:
            window_width: The width of the window, used to position the input field.
        """
        self.rect.x = window_width - self.offset_x