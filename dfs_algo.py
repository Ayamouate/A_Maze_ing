# the cell is 0 or 1 so i can tell the
# config = function of parsing to dict
import random
from typing import Any, List


n, e, s, w = 1, 2, 4, 8
on, oe, os, ow = s, w, n, e


class Maze:
    def __init__(self, width: int, height: int,
                 entry: tuple, exit: tuple, seed: Any):
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

    def grid(self):
        return self.grid

    def find_unvisited_neighbors(self, x, y):
        neighbors = []

        if x > 0 and self.visited[y][x-1] == 0:  # left
            neighbors.append((x-1, y, w, ow))
        if x < self.width - 1 and self.visited[y][x+1] == 0:  # right
            neighbors.append((x+1, y, e, oe))
        if y > 0 and self.visited[y-1][x] == 0:  # up
            neighbors.append((x, y-1, n, on))
        if y < self.height - 1 and self.visited[y+1][x] == 0:  # down
            neighbors.append((x, y+1, s, os))
        return neighbors

    def dfs_algo(self):
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

    # apply_42_pattern()
    def add_loops(self) -> None:
        num_walls = (self.width * self.height) // 5

        for _ in range(num_walls):
            x = random.randint(0, self.width - 2)
            y = random.randint(0, self.height - 2)

            directions = [
                (0, -1, n, on),
                (1, 0, e, oe),
                (0, 1, s, os),
                (-1, 0, w, ow)
            ]
            dx, dy, direction, opposite = random.choice(directions)

            nx, ny = x + dx, y + dy
            if 0 <= nx < self.width and 0 <= ny < self.height:
                if self.can_remove_wall(x, y, nx, ny):
                    self.grid[y][x] &= ~direction
                    self.grid[ny][nx] &= ~opposite

    def choose_maze_algo(self, perfect: bool) -> List:
        self.dfs_algo()   # ALWAYS generate base maze

        if not perfect:
            self.add_loops()  # only if its False
        return self.grid

    def print_maze(self) -> None:
        height = len(self.grid)
        width = len(self.grid[0])

        for y in range(height):
            # top walls
            for x in range(width):
                print("+" if x == 0 else "", end="")
                print("---" if self.grid[y][x] & n else "   ", end="+")
            print()

            # side walls and cells
            for x in range(width):
                print("|" if self.grid[y][x] & w else " ", end="")

                if (x, y) == self.entry:
                    print(" S ", end="")
                elif (x, y) == self.exit:
                    print(" E ", end="")
                else:
                    print("   ", end="")

            print("|")  # right border

        # bottom line
        print("+" + "---+"*width)


maze = Maze(20, 15, (5, 1), (19, 14), seed=0)
maze.choose_maze_algo(perfect=False)  # build imperfect maze
maze.print_maze()                      # print it
