"""Output file module for maze serialization."""

from typing import Any, List

try:
    from mazegen import dfs_algo
except ImportError:
    import dfs_algo  # type: ignore


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


def main():
    maze = dfs_algo.Maze(20, 15, (5, 1), (19, 14), seed=0)
    grid = maze.choose_maze_algo(perfect=False)

    serializer = MazeInfo(grid, "output.txt")
    serializer.print_to_file(
        entry=maze.entry,
        exit_pos=maze.exit,
        path="NESW"  # placeholder for now
    )
    print("Maze written to output.txt")


if __name__ == "__main__":
    main()
