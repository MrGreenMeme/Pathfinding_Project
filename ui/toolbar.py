import pygame

class Toolbar:
    """
    Represents a toolbar in a Pygame application.

    Attributes:
        tools: A list of tools where each tool is represented as a tuple.
            The first element is the tool's name, and the second element is
            either a pygame.Surface object or a color.
        tool_size: The size of each tool (assumed to be square).
        tool_spacing: The spacing between each tool on the toolbar.
        selected_tool: The index of the currently selected tool, or None if no tool is selected.
        toolbar_rect:  The pygame.Rect object defining the toolbar's position and size.
        tool_rects: A list of pygame.Rect objects representing the individual tool areas.
    """
    def __init__(self, tools, tool_size: int, tool_spacing: int):
        """Initializes the Toolbar with a list of tools, size of each tool, and the spacing between them.

       Args:
           tools: A list of tuples where each tuple contains the tool's name and a pygame.Surface
               or a color.
           tool_size: The size of each tool.
           tool_spacing: The spacing between each tool.
       """
        self.toolbar_rect = pygame.Rect(0, 0, (tool_size + tool_spacing) * len(tools), tool_size)
        self.tools = tools
        self.tool_size = tool_size
        self.tool_spacing = tool_spacing
        self.selected_tool = 0
        self.tool_rects = []

    def draw_toolbar(self, screen) -> None:
        """Draws the toolbar on the given screen surface.

        Args:
            screen: The Pygame surface on which to draw the toolbar.
        """
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

    def handle_click(self, x: int, y: int) -> bool:
        """Handles mouse click events to select or deselect a tool based on the click location.

       Args:
           x: The x-coordinate of the mouse click.
           y: The y-coordinate of the mouse click.

       Returns:
           bool: True if a tool was clicked (whether selected or deselected), False otherwise.
       """
        for i, tool_rect in enumerate(self.tool_rects):
            if tool_rect.collidepoint(x, y):
                if self.selected_tool == i:
                    self.selected_tool = None
                else:
                    self.selected_tool = i
                return True
        return False