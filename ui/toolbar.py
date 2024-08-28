import pygame

class Toolbar:
    def __init__(self, tools, tool_size, tool_spacing):
        self.toolbar_rect = pygame.Rect(0, 0, (tool_size + tool_spacing) * len(tools), tool_size)
        self.tools = tools
        self.tool_size = tool_size
        self.tool_spacing = tool_spacing
        self.selected_tool = 0
        self.tool_rects = []

    def draw_toolbar(self, screen):
        for i, tool in enumerate(self.tools):
            x = i * (self.tool_size + self.tool_spacing)
            tool_rect = pygame.Rect(x, 0, self.tool_size, self.tool_size)
            self.tool_rects.append(tool_rect)
            if isinstance(tool[1], pygame.Surface):
                screen.blit(tool[1], (x, 0))
            else:
                pygame.draw.rect(screen, tool[1], tool_rect)
            if i == self.selected_tool:
                pygame.draw.rect(screen, "black", tool_rect, 3)
        pygame.display.update(self.toolbar_rect)

    def handle_click(self, x, y):
        for i, tool_rect in enumerate(self.tool_rects):
            if tool_rect.collidepoint(x, y):
                if self.selected_tool == i:
                    self.selected_tool = None
                else:
                    self.selected_tool = i
                return True
        return False