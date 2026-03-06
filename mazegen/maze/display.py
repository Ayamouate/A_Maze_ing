import sys
from typing import List, Tuple


"""Maze Display Module.

Interactive terminal display for maze visualization.
Wall encoding (bits): N=1, E=2, S=4, W=8
"""


# Wall direction constants
N, E, S, W = 1, 2, 4, 8

# ANSI color codes
COLORS = [
    "",           # default/white
    "\033[31m",   # red
    "\033[32m",   # green
    "\033[34m",   # blue
    "\033[33m",   # yellow
    "\033[35m",   # magenta
]
RESET = "\033[0m"


class MazeDisplay:
    """Interactive terminal maze display with path visualization."""

    def __init__(self, grid: List[List[int]], entry: Tuple[int, int],
                 exit_pos: Tuple[int, int],
                 path: List[Tuple[int, int]] | None = None) -> None:
        """Initialize maze display.
        Args:
            grid: 2D grid with wall configurations.
            entry: Entry coordinates (x, y).
            exit_pos: Exit coordinates (x, y).
            path: Optional list of (x, y) coordinates for solution path.
        """
        self.grid = grid
        self.entry = entry
        self.exit = exit_pos
        self.path: List[Tuple[int, int]] = path if path else []
        self.show_path = False
        self.color_index = 0
        self.width = len(grid[0]) if grid else 0
        self.height = len(grid)

    def render(self) -> None:
        """Draw the entire maze to terminal."""
        # Clear screen
        print("\033[2J\033[H", end="")
        color = COLORS[self.color_index]

        for y in range(self.height):
            self._draw_top_walls(y, color)
            self._draw_cells(y, color)

        # Draw bottom border
        self._draw_bottom_border(color)
        print(RESET)

    def _draw_top_walls(self, y: int, color: str) -> None:
        """Draw horizontal walls for a row.
        Args:
            y: Row index.
            color: ANSI color code.
        """
        line = ""
        for x in range(self.width):
            line += color + "+"
            if self.grid[y][x] & N:
                line += "---"
            else:
                line += "   "
        line += color + "+" + RESET
        print(line)

    def _draw_cells(self, y: int, color: str) -> None:
        """Draw vertical walls and cell content.
        Args:
            y: Row index.
            color: ANSI color code.
        """
        line = ""
        for x in range(self.width):
            # West wall
            if self.grid[y][x] & W:
                line += color + "|" + RESET
            else:
                line += " "
            # Cell content
            line += " " + self._cell_symbol(x, y) + " "

        # East wall of last cell
        if self.grid[y][self.width - 1] & E:
            line += color + "|" + RESET
        else:
            line += " "
        print(line)

    def _draw_bottom_border(self, color: str) -> None:
        """Draw bottom border of maze.
        Args:
            color: ANSI color code.
        """
        line = ""
        for x in range(self.width):
            line += color + "+"
            if self.grid[self.height - 1][x] & S:
                line += "---"
            else:
                line += "   "
        line += color + "+" + RESET
        print(line)

    def _cell_symbol(self, x: int, y: int) -> str:
        """Return the correct symbol for a cell.
        Args:
            x: Column index.
            y: Row index.

        Returns:
            E for entry, X for exit, '.' for path, space for empty.
        """
        if (x, y) == self.entry:
            return "E"
        if (x, y) == self.exit:
            return "X"
        if self.show_path and (x, y) in self.path:
            return "*"
        return " "

    def toggle_path(self) -> None:
        """Show/hide solution path."""
        self.show_path = not self.show_path

    def change_color(self) -> None:
        """Cycle through wall colors."""
        self.color_index = (self.color_index + 1) % len(COLORS)

    def set_path(self, path: List[Tuple[int, int]]) -> None:
        """Set the solution path.

        Args:
            path: List of (x, y) coordinates.
        """
        self.path = path

    def run(self) -> None:
        """Main interactive loop."""
        # Set terminal to raw mode for single key input
        try:
            import termios
            import tty
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
        except (ImportError, termios.error):
            # Fallback for non-Unix systems
            self._run_simple()
            return

        try:
            while True:
                self.render()
                print("\nControls: [p]ath [c]olor [q]uit")

                # Read single key
                tty.setraw(fd)
                key = sys.stdin.read(1)
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

                if key == "q":
                    break
                elif key == "p":
                    self.toggle_path()
                elif key == "c":
                    self.change_color()
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            print("\033[2J\033[H", end="")  # Clear screen on exit

    def _run_simple(self) -> None:
        """Simple input loop for systems without termios."""
        while True:
            self.render()
            print("\nControls: [p]ath [c]olor [q]uit")
            key = input("Enter command: ").strip().lower()

            if key == "q":
                break
            elif key == "p":
                self.toggle_path()
            elif key == "c":
                self.change_color()
