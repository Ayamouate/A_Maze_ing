from typing import Any, List
from collections import deque


"""Output file module for maze serialization."""


N, E, S, W = 1, 2, 4, 8


class MazeInfo:
    """
    Converts the maze grid to hexadecimal representation and
    writes the complete maze data to a file.
    """

    def __init__(self, grid: List[List[Any]], file_name: str) -> None:
        """Initialize the maze info handler.
        Args:
            grid: 2D list of Cell objects representing the maze.
            file_name: Path to the output file.
        """
        self.grid = grid
        self.file_name = file_name

    def convert_to_hex(self, nbr: int) -> str:
        """Convert an integer to hexadecimal string."""
        if nbr == 0:
            return "0"
        result = ""
        base = "0123456789ABCDEF"
        while nbr > 0:
            result = base[nbr % 16] + result
            nbr //= 16
        return result

    def to_hex(self) -> str:
        """Convert the entire maze grid to hexadecimal format.

        Returns:
            Multi-line string with each cell's wall configuration
            as a hexadecimal character.
        """
        result = ""
        for row in self.grid:
            line = ""
            for cell in row:
                line += self.convert_to_hex(cell)
            line += "\n"
            result += line
        return result

    def print_to_file(self, entry: tuple[int, int],
                      exit_pos: tuple[int, int],
                      path: str) -> None:
        """Write maze data to the output file.
        Args:
            entry: Entry point coordinates as (x, y) tuple.
            exit_pos: Exit point coordinates as (x, y) tuple.
            path: Solution path string (directional characters).
        """
        hex_str = self.to_hex()

        with open(self.file_name, "w") as file:
            file.write(hex_str)
            file.write("\n")
            file.write(f"{entry[0]},{entry[1]}\n")
            file.write(f"{exit_pos[0]},{exit_pos[1]}\n")
            file.write(path + "\n")


def find_shortest_path(grid: List[List[int]], entry: tuple[int, int],
                       exit_pos: tuple[int, int]) -> str:
    """Find shortest path from entry to exit using BFS."""
    height = len(grid)
    width = len(grid[0]) if grid else 0

    queue = deque([(entry[0], entry[1], "")])
    visited = {entry}

    # Direction mappings: (dx, dy, wall_bit, letter)
    directions = [
        (0, -1, N, 'N'),  # North: y-1
        (1, 0, E, 'E'),   # East: x+1
        (0, 1, S, 'S'),   # South: y+1
        (-1, 0, W, 'W'),  # West: x-1
    ]

    while queue:
        x, y, path = queue.popleft()

        if (x, y) == exit_pos:
            return path

        cell = grid[y][x]

        for dx, dy, wall_bit, letter in directions:
            nx, ny = x + dx, y + dy

            # Check bounds
            if not (0 <= nx < width and 0 <= ny < height):
                continue

            # Check if wall is open (bit is 0)
            if cell & wall_bit:
                continue  # Wall is closed

            if (nx, ny) not in visited:
                visited.add((nx, ny))
                queue.append((nx, ny, path + letter))

    return ""  # No path found
