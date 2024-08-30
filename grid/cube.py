class Cube:
    """
    A class representing a single cube (or cell) in a grid.

    Attributes:
        color: The color of the cube, specified as a string. Default is "white".
        traversable: A boolean indicating whether the cube can be traversed. Default is True.
    """
    def __init__(self, color: str = "white", traversable: bool = True):
        """
        Initializes a Cube with a specified color and a traversable boolean.

        Args:
            color: The color of the cube, specified as a string. Default is "white".
            traversable: A boolean indicating whether the cube is traversable. Default is True.
        """
        self.color = color
        self.traversable = traversable