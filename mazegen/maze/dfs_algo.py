import random
from typing import Any


n, e, s, w = 1, 2, 4, 8
on, oe, os, ow = s, w, n, e


class Maze:
    def __init__(self, width: int, height: int,
                 entry: tuple[int, int], exit: tuple[int, int], seed: Any):
        self.grid = []  # store the cells
        self.width = width
        self.height = height
        self.entry = entry  # tuple (0, 0)
        self.exit = exit  # tuple (19, 14)
        self.seed = seed
        self.visited = [[0 for _ in range(self.width)]
                        for _ in range(self.height)]
        random.seed(self.seed)
        for _ in range(height):
            row = []
            for _ in range(width):
                row.append(15)
            self.grid.append(row)
        ex, ey = self.entry
        self.visited[ey][ex] = 1
        if self.width >= 10 and self.height >= 10:
            self.make_42_patern()

    def find_unvisited_neighbors(self, x: int,
                                 y: int) -> list[tuple[int, int, int, int]]:
        neighbors: list[tuple[int, int, int, int]] = []

        if x > 0 and self.visited[y][x-1] == 0:  # left
            neighbors.append((x-1, y, w, ow))
        if x < self.width - 1 and self.visited[y][x+1] == 0:  # right
            neighbors.append((x+1, y, e, oe))
        if y > 0 and self.visited[y-1][x] == 0:  # up
            neighbors.append((x, y-1, n, on))
        if y < self.height - 1 and self.visited[y+1][x] == 0:  # down
            neighbors.append((x, y+1, s, os))
        return neighbors

    def make_42_patern(self) -> None:
        w_42 = int((self.width - 7) / 2)
        h_42 = int((self.height - 5) / 2)
        lst = [
            (0, 0), (0, 1), (0, 2), (1, 2), (2, 2), (2, 3),
            (2, 4), (4, 0), (5, 0), (6, 0), (6, 1), (6, 2),
            (5, 2), (4, 2), (4, 3), (4, 4), (5, 4), (6, 4)]

        for t in lst:
            dx, dy = t
            self.visited[dy + h_42][dx + w_42] = 2

    def dfs_algo(self) -> None:
        stack = [self.entry]  # to store cells and pop if cell is 0 or visited
        while stack:
            x, y = stack[-1]
            neighbors = self.find_unvisited_neighbors(x, y)
            if neighbors:
                nx, ny, direction, opposite = random.choice(neighbors)
                self.grid[y][x] = self.grid[y][x] & ~direction
                self.grid[ny][nx] = self.grid[ny][nx] & ~opposite
                self.visited[ny][nx] = 1
                stack.append((nx, ny))
            else:
                stack.pop()

    def remove_walls(self) -> None:  # save borders from removing +
        num_walls = ((self.width * self.height) // 5) - 4
        for _ in range(num_walls):
            x = random.randint(0, self.width - 1)  # choosing random x, y
            y = random.randint(0, self.height - 1)
            ofsetx, ofsety, direction, opposite = random.choice([
                                (0, -1, n, on), (1, 0, e, oe),
                                (0, 1, s, os), (-1, 0, w, ow)])
            nx, ny = x + ofsetx, y + ofsety  # checking if the neighbor exist
            # if a neighb.. exist then its a wall is not a border
            if 0 <= nx < self.width and 0 <= ny < self.height:
                if self.visited[y][x] != 2 and self.visited[ny][nx] != 2:
                    if self.grid[y][x] & direction:
                        self.grid[y][x] = self.grid[y][x] & ~direction
                        self.grid[ny][nx] = self.grid[ny][nx] & ~opposite

    def choose_maze_algo(self, perfect: bool) -> list[list[int]]:
        try:
            # checking if the entry and exit are outside 42
            ex, ey = self.entry
            xx, xy = self.exit
            if self.visited[ey][ex] == 2 or self.visited[xy][xx] == 2:
                raise ValueError("Entry and exit coordinates must be"
                                 " outside the 42 pattern!")
            self.dfs_algo()
            if not perfect:
                self.remove_walls()
            return self.grid
        except ValueError as e:
            print(f"Error: {e}")
            return self.grid

    def get_42_pattern_cells(self) -> set[tuple[int, int]]:
        """Return set of (x, y) coordinates that are part of the 42 pattern."""
        cells: set[tuple[int, int]] = set()
        for y in range(self.height):
            for x in range(self.width):
                if self.visited[y][x] == 2:
                    cells.add((x, y))
        return cells
