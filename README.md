# A-Maze-Ing

*This project has been created as part of the 42 curriculum by aymouate, and ykoia.*

---

## Description

**A-Maze-Ing** is a maze generation and visualization tool built in Python. The project generates random mazes using **DFS** or **PRIM**, finds the shortest path using **Breadth-First Search (BFS)**, and provides an interactive terminal-based display using the **curses** library.

### Key Features

- **Maze Generation**: Creates random mazes with configurable dimensions
- **42 Pattern**: Embeds a "42" pattern in mazes ≥10x10 (school tribute)
- **Path Finding**: BFS algorithm to find the shortest path from entry to exit
- **Interactive Display**: Terminal-based visualization with color cycling
- **Generation Animation**: Shows maze carving animation at startup and on regeneration
- **Skip Animation**: Press `space` during carving animation to jump to final maze
- **Perfect/Imperfect Mazes**: Option to generate perfect mazes (single solution) or imperfect mazes (multiple paths)
- **Hex Output**: Serializes maze data to a file in hexadecimal format

---

## Instructions

### Prerequisites

- Python 3.10 or higher
- Terminal with curses support (Linux/macOS)

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd main_Maze

# Install dependencies
make install
```

This installs:
- `pydantic` - Configuration validation
- `flake8` - Linting
- `mypy` - Type checking

### Running the Maze Generator

```bash
# Run with default config (config.txt)
make run

# Or specify a custom config file
python3 a_maze_ing.py my_config.txt
```

### Interactive Controls

Once the maze is displayed:
| Key | Action |
|-----|--------|
| `p` | Toggle path visibility ON/OFF (animated reveal when turning ON) |
| `c` | Cycle through wall colors (Magenta → Blue → Yellow → Cyan → White) |
| `r` | Regenerate maze with new random seed |
| `space` | Skip current generation animation |
| `q` | Quit |

### Other Commands

```bash
make lint        # Run flake8 and mypy type checking
make lint-strict # Strict mypy checking
make clean       # Remove cache/build files (incl. dist and mazegen.egg-info)
make debug       # Run with Python debugger
```

---

## Configuration File Format

The configuration file uses a simple `KEY=VALUE` format. Create a `config.txt` file at the project root:

```plaintext
WIDTH=25
HEiGHT=20
ENTRY=3,1
EXIT=15,17
OUTPUT_FILE=maze.txt
PERFECT=True
```

### Required Parameters

| Parameter | Type | Range | Description |
|-----------|------|-------|-------------|
| `WIDTH` | int | 3-99 | Maze width in cells |
| `HEIGHT` | int | 3-99 | Maze height in cells |
| `ENTRY` | x,y | Within bounds | Entry point coordinates |
| `EXIT` | x,y | Within bounds | Exit point coordinates |
| `OUTPUT_FILE` | string | - | Output file path for maze data |
| `PERFECT` | bool | True/False | Perfect maze (single path) or imperfect (multiple paths) |

### Optional Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `SEED` | int | Random | Random seed for reproducible mazes |
| `ALGO` | string | DFS | Maze generation algorithm |

### Validation Rules

- Entry and exit must be within maze bounds
- Entry and exit cannot be the same position
- Entry and exit cannot overlap with the "42" pattern area (mazes ≥10x10)

### Runtime Notes

- Startup generation animation runs inside curses before controls are active
- Press `space` during startup/regeneration animation to skip to final maze
- For mazes smaller than `10x10`, the app prints `Error: maze too small for 42 pattern!` after quitting the UI

---

## Maze Generation Algorithm

### Algorithm Choice: Depth-First Search (DFS)

We chose the **DFS (Depth-First Search)** algorithm for maze generation.

### How It Works

1. **Initialization**: Start with a grid where all cells have 4 walls (value 15 = 1111 in binary)
2. **Wall Encoding**: Each wall is a bit: N=1, E=2, S=4, W=8
3. **DFS Traversal**:
   - Start at entry point, mark as visited
   - Push current cell to stack
   - Find unvisited neighbors
   - Randomly choose one, remove wall between current and neighbor
   - Repeat until stack is empty
4. **Imperfect Maze**: Optionally remove ~20% of walls to create multiple paths

### Why DFS?

| Advantage | Description |
|-----------|-------------|
| **Simplicity** | Easy to implement and understand |
| **Long Corridors** | Creates winding paths with fewer dead ends |
| **Memory Efficient** | Only requires a stack (O(n) space) |
| **Perfect Mazes** | Guarantees exactly one path between any two points |
| **42 Pattern Support** | Easy to integrate blocked cells for the 42 pattern |

### Algorithm Complexity

- **Time**: O(width × height) - visits each cell once
- **Space**: O(width × height) - stack can hold all cells in worst case

---

## Output File Format

The generated `maze.txt` contains:

```
<hex grid>

<entry_x>,<entry_y>
<exit_x>,<exit_y>
<path>
```

### Hex Grid Encoding

Each cell is represented by a single hex character (0-F) encoding its walls:
- Bit 0 (1): North wall
- Bit 1 (2): East wall
- Bit 2 (4): South wall
- Bit 3 (8): West wall

Example: `B` = 11 = 1011 binary = North + East + West walls (open to South)

### Path Format

Direction string from entry to exit: `N` (North), `E` (East), `S` (South), `W` (West)

Example: `EESSWWSSEEEE` means "go East, East, South, South, West, West, South, South, East, East, East, East"

---

## Reusable Code Components

### 1. Maze Generation (`mazegen/dfs_algo.py`)

```python
from mazegen.dfs_algo import Maze

maze = Maze(width=20, height=15, entry=(0,0), exit=(19,14), seed=42)
grid = maze.choose_maze_algo(perfect=True)
```

**Reusable for**: Any project needing procedural maze generation

### 2. Path Finding (`mazegen/serializer.py`)

```python
from mazegen.serializer import find_shortest_path

path = find_shortest_path(grid, entry=(0,0), exit_pos=(19,14))
# Returns: "EESSWWSSEE..."
```

**Reusable for**: Any grid-based pathfinding with wall encoding

### 3. Configuration Parsing (`mazegen/config_parse.py`)

```python
from mazegen.config_parse import load_config

config = load_config("config.txt")
print(config.width, config.height, config.entry)
```

**Reusable for**: Any project needing KEY=VALUE config file parsing with validation

### 4. Interactive Display (`mazegen/display.py`)

```python
from mazegen.display import MazeDisplay

display = MazeDisplay(grid, entry, exit_pos, path_coords)
display.run_with_window(stdscr)
```

**Reusable for**: Any curses-based grid visualization

---

## Advanced Features

### 1. 42 Pattern Integration

For mazes ≥10x10, a "42" pattern is embedded in the center:
- Pattern cells are blocked during generation
- Creates a visual "42" in the final maze
- Entry/exit cannot overlap with pattern

### 2. Color Cycling

5 wall colors available: Magenta → Blue → Yellow → Cyan → White

Path colors automatically contrast with walls.

### 3. Maze Regeneration

Press `r` to generate a new maze with a random seed while keeping dimensions.
Regeneration includes wall-carving animation and animated path reveal.

### 4. Perfect vs Imperfect Mazes

- **Perfect (PERFECT=True)**: Single solution, no loops
- **Imperfect (PERFECT=False)**: Removes ~20% of internal walls, creating multiple paths

---

## Project Structure

```
main_Maze/
├── a_maze_ing.py          # Main entry point
├── config.txt             # Default configuration
├── maze.txt               # Generated output
├── Makefile               # Build commands
├── pyproject.toml         # Python project config
├── README.md              # This file
└── mazegen/
    ├── __init__.py
    ├── config_parse.py      # Configuration parsing & validation
    ├── dfs_algo.py          # DFS/PRIM maze generation
    ├── display.py           # Curses-based visualization + animation
    └── serializer.py        # Output + BFS pathfinding
```

---

## Team & Tools

### Team Member

| Member | Role |
|--------|------|
| **aymouate** | display, config, parsing, documentation |
| **ykoia** | Algorithmes, animation, documentation |

### Tools Used

| Tool | Purpose |
|------|---------|
| **Python 3.13** | Core language |
| **Pydantic** | Config validation |
| **curses** | Terminal UI |
| **flake8** | Code linting |
| **mypy** | Type checking |
| **Make** | Build automation |
| **Git** | Version control |
| **Notion** | Task management & project planning |

---

### Documentation & References

- [Maze Generation Algorithms - Wikipedia](https://en.wikipedia.org/wiki/Maze_generation_algorithm)
- [Depth-First Search - GeeksforGeeks](https://www.geeksforgeeks.org/depth-first-search-or-dfs-for-a-graph/)
- [Python curses Documentation](https://docs.python.org/3/library/curses.html)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [BFS Pathfinding Tutorial](https://www.redblobgames.com/pathfinding/a-star/introduction.html)

### AI Usage

AI were used to assist development. Here's how AI was used and for which parts:

| Task | AI Contribution |
|------|-----------------|
| **Code structure** | Suggested modular file organization | Project architecture |
| **Bug fixing** | Identified issues in wall drawing and path continuity |
| **Type hints** | Suggested proper type annotations for mypy |
| **Documentation** | Helped structure README sections |
