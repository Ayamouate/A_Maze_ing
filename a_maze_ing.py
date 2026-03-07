import sys
import os
import curses

from mazegen.maze.config_parse import load_config, MazeConfig
from mazegen.maze.dfs_algo import Maze
from mazegen.maze.serializer import MazeInfo, find_shortest_path
from mazegen.maze.display import MazeDisplay


"""A-Maze-ing - Main entry point for maze generation.

Usage:
    python3 a_maze_ing.py              # uses config.txt by default
    python3 a_maze_ing.py config.txt   # specify config file
"""


# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def generate_maze(config: MazeConfig, stdscr: "curses.window") -> None:
    """Generate maze based on configuration.

    Args:
        config: Validated maze configuration.
        stdscr: Curses window object.
    """
    print(f"Generating maze {config.width}x{config.height}...")
    print(f"Entry: {config.entry}, Exit: {config.exit}")
    print(f"Algorithm: {config.algo}, Perfect: {config.perfect}")

    # Create maze generator
    maze = Maze(
        width=config.width,
        height=config.height,
        entry=config.entry,
        exit=config.exit,
        seed=config.seed
    )

    # Generate maze
    perfect = config.perfect
    grid = maze.choose_maze_algo(perfect=perfect)

    if grid is None:
        print("Error: Failed to generate maze")
        sys.exit(1)

    # Find shortest path (returns direction string like "EESSWW")
    path = find_shortest_path(grid, config.entry, config.exit)

    if not path:
        print("Warning: No path found from entry to exit!")
        path = ""

    # Convert path string to coordinates for display
    path_coords = []
    if path:
        x, y = config.entry
        path_coords.append((x, y))
        for direction in path:
            if direction == 'N':
                y -= 1
            elif direction == 'S':
                y += 1
            elif direction == 'E':
                x += 1
            elif direction == 'W':
                x -= 1
            path_coords.append((x, y))

    # Write output file
    serializer = MazeInfo(grid, config.output_file)
    serializer.print_to_file(
        entry=config.entry,
        exit_pos=config.exit,
        path=path
    )

    print(f"Maze written to: {config.output_file}")
    print(f"Shortest path length: {len(path)}")

    # Launch interactive curses display with passed window
    display = MazeDisplay(grid, config.entry, config.exit, path_coords)
    display.run_with_window(stdscr)


def curses_main(stdscr: "curses.window") -> None:
    """Main curses wrapper function.

    Args:
        stdscr: Curses window object.
    """
    # Get config file path
    if len(sys.argv) > 1:
        config_file = sys.argv[1]
    else:
        config_file = "config.txt"

    # Check if config file exists
    if not os.path.exists(config_file):
        raise FileNotFoundError(f"Config file not found: {config_file}")

    # Load and validate configuration
    config = load_config(config_file)

    # Generate maze with curses window
    generate_maze(config, stdscr)


def main() -> None:
    """Main entry point."""
    # Get config file path for pre-curses validation
    if len(sys.argv) > 1:
        config_file = sys.argv[1]
    else:
        config_file = "config.txt"

    # Check if config file exists before starting curses
    if not os.path.exists(config_file):
        print(f"Error: Config file not found: {config_file}")
        sys.exit(1)

    try:
        # Validate config before entering curses mode
        config = load_config(config_file)
        print(f"Loaded config from: {config_file}")
        print(f"Generating maze {config.width}x{config.height}...")
        print(f"Entry: {config.entry}, Exit: {config.exit}")
        print(f"Algorithm: {config.algo}, Perfect: {config.perfect}")

        # Start curses mode
        curses.wrapper(curses_main)

    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
