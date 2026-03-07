import random
from typing import List, Tuple, Optional
from mazegen.maze import dfs_algo as DFSMaze


"""Maze Generator Module.

Generates maze structure using DFS algorithm.
Wall encoding (bits):
    Bit 0 (LSB): North (1 = closed, 0 = open)
    Bit 1: East
    Bit 2: South
    Bit 3: West
"""


# Direction constants
N, E, S, W = 1, 2, 4, 8
# Opposite directions
ON, OE, OS, OW = S, W, N, E


class MazeGenerator:
    """Generates maze structure using DFS algorithm."""

    def __init__(self, width: int, height: int,
                 entry: Tuple[int, int], exit_pos: Tuple[int, int],
                 seed: Optional[int] = None) -> None:
        """Initialize the maze generator."""
        self.width = width
        self.height = height
        self.entry = entry
        self.exit = exit_pos
        self.seed = seed

        # Initialize grid with all walls closed (15 = 0b1111)
        self.grid: List[List[int]] = [
            [15 for _ in range(width)] for _ in range(height)
        ]

        # Track visited cells
        self.visited: List[List[bool]] = [
            [False for _ in range(width)] for _ in range(height)
        ]

        # Set random seed
        if seed is not None:
            random.seed(seed)

    def _get_unvisited_neighbors(self, x: int,
                                 y: int) -> List[Tuple[int, int, int, int]]:
        """Get list of unvisited neighboring cells.

        Args:
            x: Current cell x coordinate.
            y: Current cell y coordinate.

        Returns:
            List of (nx, ny, direction, opposite) tuples.
        """
        neighbors = []

        # West (left)
        if x > 0 and not self.visited[y][x - 1]:
            neighbors.append((x - 1, y, W, OW))
        # East (right)
        if x < self.width - 1 and not self.visited[y][x + 1]:
            neighbors.append((x + 1, y, E, OE))
        # North (up)
        if y > 0 and not self.visited[y - 1][x]:
            neighbors.append((x, y - 1, N, ON))
        # South (down)
        if y < self.height - 1 and not self.visited[y + 1][x]:
            neighbors.append((x, y + 1, S, OS))

        return neighbors

    def generate_dfs(self) -> List[List[int]]:
        """Generate maze using Depth-First Search algorithm.

        Returns:
            2D grid with wall configurations.
        """
        # Start from entry point
        maze = DFSMaze.Maze(
            self.width,
            self.height,
            self.entry,
            self.exit,
            self.seed
        )

        maze.dfs_algo()
        return list(maze.grid)
