"""Maze Display Module.

Interactive terminal display for maze visualization using curses.
Wall encoding (bits): N=1, E=2, S=4, W=8
"""

import curses
import random
import time
from typing import List, Tuple, Optional
from mazegen.dfs_algo import Maze
from mazegen.serializer import find_shortest_path, MazeInfo


# Wall direction constants
N, E, S, W = 1, 2, 4, 8

# Cell dimensions
CELL_H = 2
CELL_W = 4


class MazeDisplay:
    """Interactive curses-based maze display with path visualization."""

    def __init__(self, grid: List[List[int]], entry: Tuple[int, int],
                 exit_pos: Tuple[int, int],
                 path: List[Tuple[int, int]] | None = None,
                 seed: Optional[int] = None,
                 perfect: bool = False,
                 output_file: Optional[str] = None,
                 pattern_42: Optional[set[Tuple[int, int]]] = None,
                 algo: str = "DFS") -> None:
        """Initialize maze display.

        Args:
            grid: 2D grid with wall configurations.
            entry: Entry coordinates (x, y).
            exit_pos: Exit coordinates (x, y).
            path: Optional list of (x, y) coordinates for solution path.
            seed: Random seed for regeneration.
            perfect: Whether maze is perfect (no loops).
            output_file: Output file path for maze data.
            pattern_42: Set of (x, y) coordinates for 42 pattern cells.
            algo: Maze generation algorithm (DFS or PRIM).
        """
        self.grid = grid
        self.entry = entry
        self.exit = exit_pos
        self.path: List[Tuple[int, int]] = path if path else []
        self.path_set: set[Tuple[int, int]] = set(self.path)
        self.show_path = False
        self.color_index = 5  # Start with white (color pair 5)
        self.width = len(grid[0]) if grid else 0
        self.height = len(grid)
        self.seed = seed
        self.original_seed = seed  # Track if seed was fixed from config
        self.perfect = perfect
        self.output_file = output_file
        self.pattern_42: set[Tuple[int, int]] = (
            pattern_42 if pattern_42 else set()
        )
        self.algo = algo

    def _init_colors(self) -> None:
        """Initialize curses color pairs."""
        curses.start_color()
        curses.use_default_colors()

        curses.init_pair(1, curses.COLOR_MAGENTA, curses.COLOR_MAGENTA)
        curses.init_pair(2, curses.COLOR_BLUE, curses.COLOR_BLUE)
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_YELLOW)
        curses.init_pair(4, curses.COLOR_CYAN, curses.COLOR_CYAN)
        curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_WHITE)

        curses.init_pair(11, curses.COLOR_YELLOW, curses.COLOR_YELLOW)
        curses.init_pair(12, curses.COLOR_CYAN, curses.COLOR_CYAN)
        curses.init_pair(13, curses.COLOR_MAGENTA, curses.COLOR_MAGENTA)
        curses.init_pair(14, curses.COLOR_BLUE, curses.COLOR_BLUE)
        curses.init_pair(15, curses.COLOR_BLUE, curses.COLOR_BLUE)

        curses.init_pair(20, curses.COLOR_BLACK, curses.COLOR_BLACK)
        curses.init_pair(21, curses.COLOR_RED, curses.COLOR_RED)
        curses.init_pair(22, curses.COLOR_GREEN, curses.COLOR_GREEN)
        # Color pair 23: 42 pattern cells (white text on black = gray look)
        curses.init_pair(23, curses.COLOR_WHITE, curses.COLOR_BLACK)
        # Color pair 24: Title bar (white text on black background)
        curses.init_pair(24, curses.COLOR_GREEN, curses.COLOR_BLACK)

    def _get_path_color_index(self) -> int:
        """Get the path color index (opposite of current wall color)."""
        # Wall index 1-5 maps to path index 11-15
        return self.color_index + 10

    def draw_title(self, stdscr: "curses.window", width: int) -> None:
        """Draw the application title bar.
        Args:
            stdscr: Curses window object.
            width: Terminal width.
        """
        title = "# MazeGen — By aymouate and ykoia #"

        decoration = [
            "╔══════════════════════════════════════════════════════╗",
            "║                                                      ║",
            "║   ███╗   ███╗ █████╗ ███████╗███████╗ ██████╗        ║",
            "║   ████╗ ████║██╔══██╗╚══███╔╝██╔════╝██╔════╝        ║",
            "║   ██╔████╔██║███████║  ███╔╝ █████╗  ██║  ███╗       ║",
            "║   ██║╚██╔╝██║██╔══██║ ███╔╝  ██╔══╝  ██║   ██║       ║",
            "║   ██║ ╚═╝ ██║██║  ██║███████╗███████╗╚██████╔╝       ║",
            "║   ╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝╚══════╝ ╚═════╝        ║",
            "║                                                      ║",
            "║        Procedural Maze Generator and Solver          ║",
            "║                                                      ║",
            "╚══════════════════════════════════════════════════════╝",
        ]
        title_color = curses.color_pair(24)
        # Center the title
        title_x = max(0, (width - len(title)) // 2)
        self._safe_addstr(stdscr, 0, title_x, title, title_color)
        start_row = 1
        for i, line in enumerate(decoration):
            deco_x = max(0, (width - len(line)) // 2)
            self._safe_addstr(stdscr, start_row + i, deco_x, line, title_color)

    def render(
        self,
        stdscr: "curses.window",
        clear_screen: bool = True,
    ) -> None:
        """Draw the entire maze using curses with cell-based rendering.

        Args:
            stdscr: Curses window object.
        """
        if clear_screen:
            stdscr.clear()
        max_y, max_x = stdscr.getmaxyx()

        WALL = curses.color_pair(self.color_index)
        BG = curses.color_pair(20)
        PATH = curses.color_pair(self._get_path_color_index())

        # Calculate total maze size
        total_maze_h = CELL_H * (self.height + 1)
        total_maze_w = CELL_W * (self.width + 1)

        # Title height (decoration box is 12 lines + 1 for title)
        title_height = 13

        # Menu height (6 lines for box + 2 for path status)
        menu_height = 8

        # Calculate centered offsets
        total_content_h = title_height + total_maze_h + menu_height
        total_content_w = max(total_maze_w, 62)  # 62 is menu width

        # Center vertically and horizontally
        vert_center = (max_y - total_content_h) // 2 + title_height
        offset_y = max(title_height, vert_center)
        offset_x = max(0, (max_x - total_content_w) // 2)

        # Check terminal size
        required_height = total_content_h + 3
        required_width = total_content_w + 2

        if max_y < required_height or max_x < required_width:
            self._safe_addstr(stdscr, 0, 0, "Terminal too small!")
            self._safe_addstr(stdscr, 1, 0,
                              f"Need: {required_width}x{required_height}")
            self._safe_addstr(stdscr, 2, 0, f"Have: {max_x}x{max_y}")
            stdscr.refresh()
            return

        # Draw title bar
        self.draw_title(stdscr, max_x)

        # Draw each cell with centered offsets
        for row in range(self.height):
            for col in range(self.width):
                self._draw_cell(stdscr, col, row, WALL, BG, PATH,
                                offset_x, offset_y)

        # Draw info below maze (centered)
        info_y = offset_y + total_maze_h + 1
        menu_width = 62
        menu_x = max(0, (max_x - menu_width) // 2)

        self._safe_addstr(
            stdscr, info_y, menu_x,
            "╭──────────────────────────────────────────────────────────╮")
        self._safe_addstr(
            stdscr, info_y + 1, menu_x,
            "│                    ☘ Maze controls ☘                     │")
        self._safe_addstr(
            stdscr, info_y + 2, menu_x,
            "├─────────────────────────────┬────────────────────────────┤")
        self._safe_addstr(
            stdscr, info_y + 3, menu_x,
            "│  [p] Toggle path            │  [r] Regenerate maze       │")
        self._safe_addstr(
            stdscr, info_y + 4, menu_x,
            "│  [c] Change colors          │  [space] Skip animation    │")
        self._safe_addstr(
            stdscr, info_y + 5, menu_x,
            "│  [q] Quit                   │                            │")
        self._safe_addstr(
            stdscr, info_y + 6, menu_x,
            "╰─────────────────────────────┴────────────────────────────╯")
        path_status = "ON" if self.show_path else "OFF"
        self._safe_addstr(stdscr, info_y + 8, menu_x, f"Path: {path_status}")

        stdscr.refresh()

    def _draw_cell(self, stdscr: "curses.window", col: int, row: int,
                   WALL: int, BG: int, PATH: int,
                   offset_x: int, offset_y: int) -> None:
        """Draw a single cell with its walls.

        Args:
            stdscr: Curses window.
            col: Column (x) in grid.
            row: Row (y) in grid.
            WALL: Wall color pair.
            BG: Background color pair.
            PATH: Path color pair.
            offset_x: Horizontal offset for centering.
            offset_y: Vertical offset for centering.
        """
        walls = self.grid[row][col]
        is_path = self.show_path and (col, row) in self.path_set
        is_entry = (col, row) == self.entry
        is_exit = (col, row) == self.exit
        is_42 = (col, row) in self.pattern_42
        ENTRY = curses.color_pair(21)
        EXIT = curses.color_pair(22)
        PATTERN_42 = curses.color_pair(23)

        # Calculate pixel position (top-left corner of cell)
        py = offset_y + row * CELL_H
        px = offset_x + col * CELL_W

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
        elif is_42:
            self._safe_addstr(stdscr, center_y, center_x, "██",
                              PATTERN_42 | curses.A_DIM)
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

    def toggle_path(self) -> None:
        """Show/hide solution path."""
        self.show_path = not self.show_path

    def change_color(self) -> None:
        """Cycle through wall colors (1-5)."""
        self.color_index = (self.color_index % 5) + 1

    def _update_path_from_grid(self) -> str:
        """Recompute shortest path and update cached coordinates."""
        path_str = find_shortest_path(self.grid, self.entry, self.exit) or ""

        path_coords: List[Tuple[int, int]] = []
        if path_str:
            x, y = self.entry
            path_coords.append((x, y))
            for direction in path_str:
                if direction == 'N':
                    y -= 1
                elif direction == 'S':
                    y += 1
                elif direction == 'E':
                    x += 1
                elif direction == 'W':
                    x -= 1
                path_coords.append((x, y))

        self.path = path_coords
        self.path_set = set(path_coords)
        return path_str

    def _animate_path_reveal(
        self,
        stdscr: "curses.window",
        full_path: List[Tuple[int, int]],
    ) -> None:
        """Reveal the final path progressively, one cell per frame."""
        if not self.show_path or not full_path:
            return

        self.path = full_path
        self.path_set = set()

        frame_dt = 1 / 60
        last = time.monotonic()

        for coord in full_path:
            self.path_set.add(coord)
            self.render(stdscr, clear_screen=False)

            now = time.monotonic()
            wait = frame_dt - (now - last)
            if wait > 0:
                time.sleep(wait)
            last = time.monotonic()

    def regenerate(self, stdscr: Optional["curses.window"] = None) -> None:
        """Regenerate the maze with a new random seed."""

        if self.original_seed is not None:
            return
        new_seed = random.randint(0, 1000000)

        # Create new maze
        maze = Maze(
            width=self.width,
            height=self.height,
            entry=self.entry,
            exit=self.exit,
            seed=new_seed,
            algo=self.algo
        )

        # Generate maze
        new_grid = maze.choose_maze_algo(perfect=self.perfect)

        if new_grid is not None:
            broken_walls = maze.get_broken_walls()
            self.seed = new_seed
            self.pattern_42 = maze.get_42_pattern_cells()

            if stdscr is not None and broken_walls:
                self.animate_generation(stdscr, broken_walls,
                                        final_grid=new_grid)
            else:
                self.grid = new_grid

            path_str = self._update_path_from_grid()

            if stdscr is not None and self.path:
                self._animate_path_reveal(stdscr, self.path)

            # Update output file if specified
            if self.output_file:
                serializer = MazeInfo(self.grid, self.output_file)
                serializer.print_to_file(
                    entry=self.entry,
                    exit_pos=self.exit,
                    path=path_str if path_str else ""
                )

    def run_with_window(
        self,
        stdscr: "curses.window",
        startup_broken_walls: Optional[List[Tuple[int, int, int, int]]] = None,
    ) -> None:
        """Run display with an existing curses window.
        Args:
            stdscr: Curses window object from wrapper.
            startup_broken_walls: Optional wall-break steps for initial
                generation animation.
        """
        self._init_colors()
        curses.curs_set(0)
        curses.raw()
        stdscr.keypad(True)

        if startup_broken_walls:
            self.animate_generation(stdscr, startup_broken_walls,
                                    final_grid=self.grid)

        # Recompute path after animation (animate_generation clears path_set)
        self._update_path_from_grid()

        while True:
            self.render(stdscr)
            key = stdscr.getch()
            if key == 3:
                continue
            if key == ord('q') or key == ord('Q'):
                break
            elif key == ord('p') or key == ord('P'):
                self.toggle_path()
                if self.show_path and self.path:
                    self._animate_path_reveal(stdscr, self.path)
            elif key == ord('c') or key == ord('C'):
                self.change_color()
            elif key == ord('r') or key == ord('R'):
                self.regenerate(stdscr)

    def animate_generation(
        self,
        stdscr: "curses.window",
        broken_walls: List[Tuple[int, int, int, int]],
        final_grid: Optional[List[List[int]]] = None,
    ) -> None:
        """Animate wall carving with reduced frame flicker.
        Args:
            stdscr: Curses window object.
            broken_walls: Ordered list of (x, y, nx, ny) wall-break steps.
            final_grid: The completed maze grid to restore after animation
                (handles early skip via space key). If None, the partially
                animated grid is kept as-is.
        """
        self.grid = [
            [N | E | S | W for _ in range(self.width)]
            for _ in range(self.height)
        ]
        self.path = []
        self.path_set = set()

        frame_dt = 1 / 60
        last = time.monotonic()

        stdscr.nodelay(True)
        try:
            for x, y, nx, ny in broken_walls:
                key = stdscr.getch()
                if key == ord(' '):
                    break

                if nx == x + 1:
                    self.grid[y][x] &= ~E
                    self.grid[ny][nx] &= ~W
                elif nx == x - 1:
                    self.grid[y][x] &= ~W
                    self.grid[ny][nx] &= ~E
                elif ny == y + 1:
                    self.grid[y][x] &= ~S
                    self.grid[ny][nx] &= ~N
                elif ny == y - 1:
                    self.grid[y][x] &= ~N
                    self.grid[ny][nx] &= ~S

                self.render(stdscr, clear_screen=False)

                now = time.monotonic()
                wait = frame_dt - (now - last)
                if wait > 0:
                    time.sleep(wait)
                last = time.monotonic()
        finally:
            stdscr.nodelay(False)
            # Always restore the final correct grid so the path is valid
            if final_grid is not None:
                self.grid = final_grid
        self.render(stdscr)
