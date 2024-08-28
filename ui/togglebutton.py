import pygame

class ToggleButton:
    def __init__(self, x, y, width, height, offset, font, text):
        self.offset = offset
        self.rect = pygame.Rect(x, y, width, height)
        self.font = font
        self.text = text
        self.state = False
        self.color_on = pygame.Color('green')
        self.color_off = pygame.Color('grey')

    def draw(self, screen):
        color = self.color_on if self.state else self.color_off
        pygame.draw.rect(screen, color, self.rect)
        text = self.font.render(self.text, True, "white")
        screen.blit(text, (self.rect.x + 3, self.rect.y + 10))
        pygame.display.update(self.rect)
    def handle_click(self):
        self.state = not self.state

    def shift(self, window_width):
        self.rect.x = window_width - self.offset