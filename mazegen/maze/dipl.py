import curses
from curses import window
import curses.panel
from curses.panel import panel
import random
from typing import Dict, List, Any, Tuple, Optional
import mazegen.maze.dfs_algo as recursive_backtraking
import mazegen.maze


class MazeDisplay:
    """
    Handles the TUI (Terminal User Interface)
    for maze visualization using curses.

    This class manages window creation,
    color pairs, terminal resizing,
    and user input mapping for the maze generation and pathfinding animations.
    """
    colors: List[int] = [
        curses.COLOR_RED,
        curses.COLOR_GREEN,
        curses.COLOR_MAGENTA,
        curses.COLOR_BLUE,
        curses.COLOR_CYAN,
    ]

    def __init__(self, config_data: Dict[str, Any],
                 maze_open: List[List[Dict[str, Any]]]):
        """
        Initializes the display with configuration and the generated maze.
        """
        self.config_data = config_data
        self.maze_open = maze_open
        self.maze_close = self.maz_close()

    def init_curses(self, stdscr: window) -> None:
        """
        Sets up the initial curses state, including colors
        and cursor visibility.
        """
        curses.curs_set(0)
        stdscr.keypad(True)
        curses.start_color()
        curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
        curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_RED, curses.COLOR_RED)
        curses.init_pair(6, curses.COLOR_CYAN, curses.COLOR_WHITE)
        curses.init_pair(7, curses.COLOR_YELLOW, curses.COLOR_YELLOW)
        curses.init_pair(8, curses.COLOR_BLACK, curses.COLOR_BLACK)

    def calcul_maze(self, maze_h: int, maze_w: int) -> Tuple[int, int]:
        """
        Calculates the top-left corner (x, y) to center the maze on screen.
        """
        width: int = self.config_data["WIDTH"]
        height: int = self.config_data["HEIGHT"]
        total_width = width * 4 + 1
        total_height = height * 2 + 1
        x_start = (maze_w // 2) - (total_width // 2)
        y_start = (maze_h // 2) - (total_height // 2)
        return x_start, y_start

    def maz_close(self) -> List[List[Dict[str, bool]]]:
        """
        Creates a 'closed' version of the maze where all walls are present.
        """
        width: int = self.config_data["WIDTH"]
        height: int = self.config_data["HEIGHT"]
        maze = [[{"N": True, "E": True, "S": True, "W": True}
                 for _ in range(width)] for _ in range(height)]
        return maze

    def maze_from_open(self) -> List[List[Dict[str, bool]]]:
        """
        Synchronizes the closed maze state with the current open maze state.
        """
        width: int = self.config_data["WIDTH"]
        height: int = self.config_data["HEIGHT"]
        maze = [[{"N": self.maze_open[y][x]["N"],
                  "E": self.maze_open[y][x]["E"],
                  "S": self.maze_open[y][x]["S"],
                  "W": self.maze_open[y][x]["W"]}
                 for x in range(width)] for y in range(height)]
        return maze

    def display_maze(self, maze_win: window,
                     maze_h: int, maze_w: int) -> None:
        """
        Draws the actual maze structure (walls and paths) onto the maze window.
        """
        maze_close = self.maze_close
        width: int = self.config_data["WIDTH"]
        height: int = self.config_data["HEIGHT"]
        x_start, y_start = self.calcul_maze(maze_h, maze_w)
        for ny in range(height):
            top_line = ""
            for nx in range(width):
                top_line += "█"
                top_line += "███" if maze_close[ny][nx]["N"] else "   "
            top_line += "█"
            maze_win.addstr(y_start + ny * 2, x_start,
                            top_line, curses.color_pair(6))

            left_right_line = ""
            for nx in range(width):
                left_right_line += "█" if maze_close[ny][nx]["W"] else " "
                left_right_line += "   "
            left_right_line += "█"
            maze_win.addstr(y_start + 1 + ny * 2, x_start,
                            left_right_line, curses.color_pair(6))

        bottom_line = ""
        for nx in range(width):
            bottom_line += "█"
            bottom_line += "███" if maze_close[-1][nx]["S"] else "   "
        bottom_line += "█"
        maze_win.addstr(y_start + height * 2, x_start,
                        bottom_line, curses.color_pair(6))
        if width >= 7 and height >= 5:
            self.color_42(maze_win, maze_h, maze_w)
        self.color_start_exit(maze_win, maze_h, maze_w)

    def color_start_exit(self, maze_win: window, maze_h:
                         int, maze_w: int) -> None:
        """
        Highlights the entry and exit points of the maze.
        """
        x_start, y_start = self.calcul_maze(maze_h, maze_w)
        entry_x, entry_y = self.config_data["ENTRY"]
        exit_x, exit_y = self.config_data["EXIT"]

        maze_win.addstr(y_start + entry_y * 2 + 1, x_start + entry_x * 4 + 1,
                        "   ", curses.color_pair(4))
        maze_win.addstr(y_start + exit_y * 2 + 1, x_start + exit_x * 4 + 1,
                        "   ", curses.color_pair(5))

    def color_42(self, maze_win: window,
                 maze_h: int, maze_w: int) -> None:
        """
        Special decorative coloring for central points in the maze.
        """
        x_start, y_start = self.calcul_maze(maze_h, maze_w)
        width = self.config_data["WIDTH"]
        height = self.config_data["HEIGHT"]
        mx, my = (width // 2), (height // 2)

        points = [
            (mx-1, my), (mx-1, my+1), (mx-2, my), (mx-3, my),
            (mx-3, my-1), (mx-3, my-2), (mx-1, my+2),
            (mx+1, my), (mx+2, my), (mx+3, my),
            (mx+3, my-1), (mx+3, my-2),
            (mx+2, my-2), (mx+1, my-2),
            (mx+1, my+1), (mx+1, my+2),
            (mx+2, my+2), (mx+3, my+2)
        ]
        for cx, cy in points:
            screen_x = x_start + cx * 4 + 1
            screen_y = y_start + cy * 2 + 1
            maze_win.addstr(screen_y, screen_x, "   ", curses.color_pair(8))

    def calculate_sizes(self, stdscr: window
                        ) -> Tuple[int, int, int, int, int, int]:
        """
        Calculates window dimensions based on the current terminal size.
        """
        h, w = stdscr.getmaxyx()
        title_h = 3
        bottom_h = 12
        maze_h = h - title_h - bottom_h
        maze_w = w
        info_w = maze_w
        return h, w, title_h, maze_h, maze_w, info_w

    def create_windows(self, title_h: int, maze_h: int,
                       maze_w: int, info_w: int) -> Tuple[
            window, window, window,
            panel, panel, panel]:
        """
        Initializes the curses windows and their corresponding panels.
        """
        title_win = curses.newwin(title_h, maze_w, 0, 0)
        title_panel = curses.panel.new_panel(title_win)
        title_panel.top()
        maze_win = curses.newwin(maze_h, maze_w, title_h, 0)
        maze_panel = curses.panel.new_panel(maze_win)
        maze_panel.top()
        info_win = curses.newwin(12, info_w, title_h + maze_h, 0)
        info_panel = curses.panel.new_panel(info_win)
        info_panel.top()

        return (title_win, maze_win, info_win,
                title_panel, maze_panel, info_panel)

    def draw_title(self, win: window, w: int) -> None:
        """
        Draws the application title bar.
        """
        win.border()
        win.bkgd(curses.color_pair(1))
        win.addstr(1, (w // 2) - 11, ":( Ɋozbr (×_×) Ma3dnos ):")
        win.addstr(2, (w // 2) - 11, "⏶⏶⏶⏶⏶⏶⏶⏶⏶⏶⏶z⏶⏶⏶⏶⏶⏶⏶⏶⏶⏶⏶⏶⏶")

    def draw_maze(self, win: window,
                  maze_h: int, maze_w: int) -> None:
        """
        Sets the maze window background and triggers structure drawing.
        """
        win.border()
        win.bkgd(curses.color_pair(2))
        self.display_maze(win, maze_h, maze_w)

    def draw_info(self, win: window, w: int) -> None:
        """
        Draws the legend and control instructions at the bottom.
        """
        x = (w // 2) - 33
        win.border()
        win.bkgd(curses.color_pair(1))
        win.addstr(
            2, x, "╭─────────────────────────────────"
            "────────────────────────────────╮")
        win.addstr(
            3, x, "│                   ☘ Maze controls"
            " Explained ☘                   │")
        win.addstr(
            4, x, "├────────────────────────────────┬─"
            "───────────────────────────────┤")
        win.addstr(
            5, x, "│  1: Press 's' to start         │"
            "  2: Press 'SPACE' to skip anim │")
        win.addstr(
            6, x, "│  3: Press 'p' to show path     │"
            "  4: Press 'r' to random maze   │")
        win.addstr(
            7, x, "│  5: Press 'c' to change colors │"
            "  6: Press 'k' to show/hide path│")
        win.addstr(
            8, x, "╰────────────────────────────────"
            "┴────────────────────────────────╯")
        win.addstr(
            10, x, "                         Press "
            "'q' to quit                ")

    def input_key(self, maze_win: window) -> Optional[str]:
        """
        Captures keyboard input and maps it to specific string actions.
        """
        key = maze_win.getch()
        if key in (ord('q'), ord('Q')):
            return "quit"
        elif key in (ord('s'), ord('S')):
            return "start"
        elif key in (ord('p'), ord('P')):
            return "path"
        elif key in (ord('c'), ord('C')):
            return "change_color"
        elif key in (ord('r'), ord('R')):
            return "random_maze"
        elif key in (ord('k'), ord('K')):
            return "show_path"
        return None

    def window_output(self, stdscr: window) -> None:
        """
        Main rendering loop. Handles window management, animation triggers,
        and logic.
        """
        self.init_curses(stdscr)

        path_shown = False
        maze_started = False
        maze_shown = False

        from typing import Optional

        prev_size: Optional[Tuple[int, int]] = None

        title_win: Optional[window] = None
        maze_win: Optional[window] = None
        info_win: Optional[window] = None

        title_panel: Optional[panel] = None
        maze_panel: Optional[panel] = None
        info_panel: Optional[panel] = None

        while True:
            try:
                _, _, title_h, maze_h, maze_w, info_w = self.calculate_sizes(
                    stdscr)

                if prev_size != stdscr.getmaxyx():
                    (
                        title_win,
                        maze_win,
                        info_win,
                        title_panel,
                        maze_panel,
                        info_panel,
                    ) = self.create_windows(title_h, maze_h, maze_w, info_w)

                    self.draw_title(title_win, maze_w)
                    self.draw_info(info_win, info_w)
                    self.draw_maze(maze_win, maze_h, maze_w)

                    prev_size = stdscr.getmaxyx()

                if maze_win is None:
                    continue

                if maze_shown:
                    mazegen.animation.draw_opend_maze(
                        maze_win,
                        self.maze_open,
                        self.maze_close,
                        self.config_data,
                    )

                if path_shown:
                    mazegen.animation.redraw_path(
                        self.config_data, maze_win,
                        maze_h, maze_w, self.maze_open
                    )

                curses.panel.update_panels()
                curses.doupdate()
                curses.flushinp()
                action = self.input_key(maze_win)
                if action == "quit":
                    break
                elif action == "start":
                    if not maze_started and not maze_shown:
                        maze_started = True
                        maze_shown = True
                        mazegen.animation.startInstructions(
                            maze_win,
                            self.maze_open,
                            self.maze_close,
                            self.config_data,
                        )

                elif action == "path":
                    if maze_started and not path_shown:
                        path_shown = True
                        mazegen.animation.show_path(
                            self.config_data, maze_win,
                            maze_h, maze_w, self.maze_open
                        )
                elif action == "show_path":
                    if maze_started and path_shown:
                        path_shown = False
                    elif maze_started and not path_shown:
                        mazegen.animation.redraw_path(
                            self.config_data, maze_win,
                            maze_h, maze_w, self.maze_open
                        )
                        path_shown = True

                elif action == "change_color":
                    if maze_started:
                        colors = self.colors.copy()
                        random.shuffle(colors)
                        self.maze_color = colors[0]
                        self.path_color = colors[1]
                        self.n42_color = colors[2]

                        curses.init_pair(6, self.maze_color,
                                         curses.COLOR_WHITE)
                        curses.init_pair(7, self.path_color, self.path_color)
                        curses.init_pair(8, self.n42_color, self.n42_color)
                        maze_win.clear()
                        self.draw_maze(maze_win, maze_h, maze_w)
                        curses.panel.update_panels()
                        curses.doupdate()
                elif action == "random_maze":
                    if maze_started:

                        self.maze_open, steps = (
                            recursive_backtraking.generate_maze_with_steps(
                                self.config_data
                            )
                        )
                        self.config_data["ANIMATION_STEPS"] = steps
                        self.maze_close = self.maze_from_open()
                        mazegen.animation.reset_path_cache()
                        mazegen.out_put.write_maze_hex(self.maze_open,
                                                       self.config_data)
                        mazegen.out_put.write_path(
                            self.config_data, self.maze_open)
                        stdscr.clear()
                        maze_win.clear()

                        self.draw_maze(maze_win, maze_h, maze_w)
                        if path_shown:
                            mazegen.animation.show_path(
                                self.config_data,
                                maze_win,
                                maze_h,
                                maze_w,
                                self.maze_open,
                            )
                        curses.panel.update_panels()
                        curses.doupdate()

            except curses.error:
                h_error, w_error = stdscr.getmaxyx()
                error_win = curses.newwin(h_error, w_error, 0, 0)
                error_panel = curses.panel.new_panel(error_win)
                error_panel.top()
                error_win.border()
                error_win.bkgd(curses.color_pair(1))
                error_win.addstr(
                    h_error // 2, (w_error // 2) -
                    10, f"Window too small: {h_error}x{w_error}"
                )
                curses.panel.update_panels()
                curses.doupdate()
                action = self.input_key(error_win)
                if action == "quit":
                    exit()

                continue

    def display(self) -> None:
        """
        Launches the curses wrapper to safely start the application.
        """
        curses.wrapper(self.window_output)
