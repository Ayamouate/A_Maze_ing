"""Maze Renderer Module.

Displays maze in ASCII format.
"""

from typing import List, Tuple

# Direction constants
N, E, S, W = 1, 2, 4, 8


class MazeRenderer:
    """Displays maze in ASCII format."""

    def __init__(self, grid: List[List[int]],
                 entry: Tuple[int, int], exit_pos: Tuple[int, int]) -> None:
        """Initialize the maze renderer.

        Args:
            grid: 2D list of wall configurations (0-15).
            entry: Entry point coordinates (x, y).
            exit_pos: Exit point coordinates (x, y).
        """
        self.grid = grid
        self.entry = entry
        self.exit = exit_pos
        self.height = len(grid)
        self.width = len(grid[0]) if grid else 0
        self.path: List[Tuple[int, int]] = []
        self.show_path = False

    