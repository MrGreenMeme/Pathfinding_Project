import pygame
import logging
class InputField:
    def __init__(self, x, y, width, height, font, inactive_color, active_color, redraw_screen):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = inactive_color
        self.inactive_color = inactive_color
        self.active_color = active_color
        self.text = ''
        self.font = font
        self.active = False
        self.redraw_screen = redraw_screen

    def handle_click(self, event):
        if self.rect.collidepoint(event.pos):
            self.active = not self.active
        self.color = self.active_color if self.active else self.inactive_color

    def handle_input(self, event, screen, grid, view):
        if self.active:
            if event.key == pygame.K_RETURN:
                logging.debug(f"Entered: {self.text}")
                try:
                    new_rows, new_cols = map(int, self.text.lower().split('x'))
                    grid.resize_grid(new_rows, new_cols)
                    view.calculate_zoom_factor(grid.rows, grid.cols)
                    view.center_grid(grid.rows, grid.cols)
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

    def draw(self, screen):
        pygame.draw.rect(screen, "white", self)
        pygame.draw.rect(screen, self.color, self.rect, 2)
        text_surface = self.font.render(self.text, True, self.color)
        screen.blit(text_surface, (self.rect.x + 5, self.rect.y + 5))
        pygame.display.update(self.rect)

    def shift(self, window_width):
        self.rect.x = window_width - 270