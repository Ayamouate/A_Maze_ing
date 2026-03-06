import sys
import os

from config_parse import load_config, MazeConfig
from mazegen.dfs_algo import Maze
from mazegen.serializer import MazeInfo, find_shortest_path
from mazegen.maze.display import MazeDisplay


"""A-Maze-ing - Main entry point for maze generation.

Usage:
    python3 a_maze_ing.py              # uses config.txt by default
    python3 a_maze_ing.py config.txt   # specify config file
"""


# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def generate_maze(config: MazeConfig) -> None:
    """Generate maze based on configuration.

    Args:
        config: Validated maze configuration.
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

    # Print ASCII maze with path
    print("\nMaze preview (path shown with *):")
    maze.print_maze(path_coords)

    # Launch interactive display
    print("\nLaunching interactive display...")
    print("Controls: [p]ath toggle, [c]olor change, [q]uit")
    display = MazeDisplay(grid, config.entry, config.exit, path_coords)
    display.run()


def main() -> None:
    """Main entry point."""
    # Get config file path
    if len(sys.argv) > 1:
        config_file = sys.argv[1]
    else:
        config_file = "config.txt"

    # Check if config file exists
    if not os.path.exists(config_file):
        print(f"Error: Config file not found: {config_file}")
        sys.exit(1)

    try:
        # Load and validate configuration
        config = load_config(config_file)
        print(f"Loaded config from: {config_file}")

        # Generate maze
        generate_maze(config)

    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
