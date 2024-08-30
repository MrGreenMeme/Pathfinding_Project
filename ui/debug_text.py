import pygame.font

class DebugText:
    """
   A class to display debug text on a Pygame screen.

   Attributes:
       font: A Pygame font object used to render the text.
       text_color: The color of the text.
   """
    def __init__(self, font: pygame.font.Font, text_color):
        """Initializes the DebugText with a font and text color.

       Args:
           font: A Pygame font object used to render the text.
           text_color: The color of the text.
       """
        self.font = font
        self.text_color = text_color

    def draw(self, screen, debug_text: str, position: tuple) -> None:
        """Renders and displays the debug text on the screen.

        Args:
            screen: The Pygame surface on which to draw the debug text.
            debug_text: The string of text to display on the screen.
            position: A tuple representing the (x, y) position on the screen where the text will be drawn.
        """
        text_surface = self.font.render(debug_text, True, self.text_color)
        screen.blit(text_surface, position)