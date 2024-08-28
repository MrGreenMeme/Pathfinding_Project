import pygame

class Dropdown:
    def __init__(self, x, y, width, height, font, options):
        self.rect = pygame.Rect(x, y, width, height)
        self.option_rect = pygame.Rect(0, 0, 0, 0)
        self.font = font
        self.options = options
        self.selected = None
        self.open = False

    def handle_click(self, event):
        if self.rect.collidepoint(event.pos):
            self.open = not self.open
        elif self.open:
            for i, option in enumerate(self.options):
                option_rect = pygame.Rect(self.rect.x, self.rect.y + (i + 1) * self.rect.height, self.rect.width, self.rect.height)
                if option_rect.collidepoint(event.pos):
                    self.selected = option
                    self.open = False

    def draw(self, screen):
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

    def shift(self, window_width):
        self.rect.x = window_width - 400