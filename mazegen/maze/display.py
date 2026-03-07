"""Maze Display Module.

Interactive terminal display for maze visualization using curses.
Wall encoding (bits): N=1, E=2, S=4, W=8
"""

import curses
from typing import List, Tuple

# Wall direction constants
N, E, S, W = 1, 2, 4, 8

# Layout constants
OFFSET_Y = 8
OFFSET_X = 2
CELL_H = 2
CELL_W = 4


class MazeDisplay:
    """Interactive curses-based maze display with path visualization."""

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
        self.path_set: set[Tuple[int, int]] = set(self.path)
        self.show_path = False
        self.color_index = 1
        self.width = len(grid[0]) if grid else 0
        self.height = len(grid)

    def _init_colors(self) -> None:
        """Initialize curses color pairs."""
        curses.start_color()
        curses.use_default_colors()
        # Color pairs 1-6: Wall colors (cycle through with 'c')
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_WHITE)
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_RED)
        curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_BLUE)
        curses.init_pair(4, curses.COLOR_CYAN, curses.COLOR_CYAN)
        curses.init_pair(5, curses.COLOR_YELLOW, curses.COLOR_YELLOW)
        curses.init_pair(6, curses.COLOR_MAGENTA, curses.COLOR_MAGENTA)
        # Color pair 7: Path (always green)
        curses.init_pair(7, curses.COLOR_GREEN, curses.COLOR_GREEN)
        # Color pair 8: Background (black)
        curses.init_pair(8, curses.COLOR_BLACK, curses.COLOR_BLACK)
        # Color pair 9: Entry (yellow on yellow)
        curses.init_pair(9, curses.COLOR_YELLOW, curses.COLOR_YELLOW)
        # Color pair 10: Exit (red on red)
        curses.init_pair(10, curses.COLOR_RED, curses.COLOR_RED)

    def render(self, stdscr: "curses.window") -> None:
        """Draw the entire maze using curses with cell-based rendering.

        Args:
            stdscr: Curses window object.
        """
        stdscr.clear()
        max_y, max_x = stdscr.getmaxyx()

        WALL = curses.color_pair(self.color_index)
        BG = curses.color_pair(8)
        PATH = curses.color_pair(7)

        # Calculate total maze size
        total_maze_h = CELL_H * (self.height + 1)
        total_maze_w = CELL_W * (self.width + 1)

        # Check terminal size
        required_height = OFFSET_Y + total_maze_h + 3
        required_width = OFFSET_X + total_maze_w + 2

        if max_y < required_height or max_x < required_width:
            self._safe_addstr(stdscr, 0, 0, "Terminal too small!")
            self._safe_addstr(stdscr, 1, 0,
                              f"Need: {required_width}x{required_height}")
            self._safe_addstr(stdscr, 2, 0, f"Have: {max_x}x{max_y}")
            stdscr.refresh()
            return

        # Draw each cell
        for row in range(self.height):
            for col in range(self.width):
                self._draw_cell(stdscr, col, row, WALL, BG, PATH)

        # Draw info below maze
        info_y = OFFSET_Y + total_maze_h + 1
        self._safe_addstr(stdscr, info_y, OFFSET_X,
                          "Controls: [p]ath  [c]olor  [q]uit")
        path_status = "ON" if self.show_path else "OFF"
        self._safe_addstr(stdscr, info_y + 1, OFFSET_X, f"Path: {path_status}")

        stdscr.refresh()

    def _draw_cell(self, stdscr: "curses.window", col: int, row: int,
                   WALL: int, BG: int, PATH: int) -> None:
        """Draw a single cell with its walls.

        Args:
            stdscr: Curses window.
            col: Column (x) in grid.
            row: Row (y) in grid.
            WALL: Wall color pair.
            BG: Background color pair.
            PATH: Path color pair.
        """
        walls = self.grid[row][col]
        is_path = self.show_path and (col, row) in self.path_set
        is_entry = (col, row) == self.entry
        is_exit = (col, row) == self.exit
        ENTRY = curses.color_pair(9)
        EXIT = curses.color_pair(10)

        # Calculate pixel position (top-left corner of cell)
        py = OFFSET_Y + row * CELL_H
        px = OFFSET_X + col * CELL_W

        # Draw North wall or path connection
        if walls & N:
            self._safe_addstr(stdscr, py, px + 2, "  ", WALL)
        else:
            # Check if path goes North
            north_path = is_path and (col, row - 1) in self.path_set
            if north_path:
                self._safe_addstr(stdscr, py, px + 2, "  ", PATH)
            else:
                self._safe_addstr(stdscr, py, px + 2, "  ", BG)

        # Draw South wall or path connection
        if walls & S:
            self._safe_addstr(stdscr, py + CELL_H, px + 2, "  ", WALL)
        else:
            south_path = is_path and (col, row + 1) in self.path_set
            if south_path:
                self._safe_addstr(stdscr, py + CELL_H, px + 2, "  ", PATH)
            else:
                self._safe_addstr(stdscr, py + CELL_H, px + 2, "  ", BG)

        # Draw West wall or path connection
        if walls & W:
            self._safe_addstr(stdscr, py + 1, px, "  ", WALL)
        else:
            west_path = is_path and (col - 1, row) in self.path_set
            if west_path:
                self._safe_addstr(stdscr, py + 1, px, "  ", PATH)
            else:
                self._safe_addstr(stdscr, py + 1, px, "  ", BG)

        # Draw East wall or path connection
        if walls & E:
            self._safe_addstr(stdscr, py + 1, px + CELL_W, "  ", WALL)
        else:
            east_path = is_path and (col + 1, row) in self.path_set
            if east_path:
                self._safe_addstr(stdscr, py + 1, px + CELL_W, "  ", PATH)
            else:
                self._safe_addstr(stdscr, py + 1, px + CELL_W, "  ", BG)

        # Draw 4 corners (always walls)
        self._safe_addstr(stdscr, py, px, "  ", WALL)
        self._safe_addstr(stdscr, py, px + CELL_W, "  ", WALL)
        self._safe_addstr(stdscr, py + CELL_H, px, "  ", WALL)
        self._safe_addstr(stdscr, py + CELL_H, px + CELL_W, "  ", WALL)

        # Draw cell content (center of cell)
        center_y = py + 1
        center_x = px + 2

        if is_entry:
            self._safe_addstr(stdscr, center_y, center_x, "  ", ENTRY)
        elif is_exit:
            self._safe_addstr(stdscr, center_y, center_x, "  ", EXIT)
        elif is_path:
            self._safe_addstr(stdscr, center_y, center_x, "  ", PATH)
        else:
            self._safe_addstr(stdscr, center_y, center_x, "  ", BG)

    def _safe_addstr(self, stdscr: "curses.window", y: int, x: int,
                     text: str, attr: int = 0) -> None:
        """Safely add string to curses window, ignoring boundary errors.

        Args:
            stdscr: Curses window object.
            y: Row position.
            x: Column position.
            text: Text to display.
            attr: Optional curses attribute.
        """
        try:
            stdscr.addstr(y, x, text, attr)
        except curses.error:
            pass

    def _cell_symbol(self, x: int, y: int) -> str:
        """Return the correct symbol for a cell.

        Args:
            x: Column index.
            y: Row index.

        Returns:
            E for entry, X for exit, * for path, space for empty.
        """
        if (x, y) == self.entry:
            return "E"
        if (x, y) == self.exit:
            return "X"
        if self.show_path and (x, y) in self.path_set:
            return "*"
        return " "

    def toggle_path(self) -> None:
        """Show/hide solution path."""
        self.show_path = not self.show_path

    def change_color(self) -> None:
        """Cycle through wall colors (1-6)."""
        self.color_index = (self.color_index % 6) + 1

    def set_path(self, path: List[Tuple[int, int]]) -> None:
        """Set the solution path.

        Args:
            path: List of (x, y) coordinates.
        """
        self.path = path
        self.path_set = set(path)

    def _main_loop(self, stdscr: "curses.window") -> None:
        """Main curses loop.

        Args:
            stdscr: Curses window object.
        """
        self._init_colors()
        curses.curs_set(0)
        stdscr.keypad(True)

        while True:
            self.render(stdscr)
            key = stdscr.getch()

            if key == ord('q'):
                break
            elif key == ord('p'):
                self.toggle_path()
            elif key == ord('c'):
                self.change_color()

    def run(self) -> None:
        """Start the interactive curses display (creates its own window)."""
        curses.wrapper(self._main_loop)

    def run_with_window(self, stdscr: "curses.window") -> None:
        """Run display with an existing curses window.

        Args:
            stdscr: Curses window object from wrapper.
        """
        self._init_colors()
        curses.curs_set(0)
        stdscr.keypad(True)

        while True:
            self.render(stdscr)
            key = stdscr.getch()

            if key == ord('q'):
                break
            elif key == ord('p'):
                self.toggle_path()
            elif key == ord('c'):
                self.change_color()
                self.change_color()
