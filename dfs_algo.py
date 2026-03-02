# the cell is 0 or 1 so i can tell the 

# config = function of parsing to dict
import random


n, e, s, w = 1, 2, 4, 8
on, oe, os, ow = s, w, n, e


class Grid:
    def __init__(self, width: int, height: int,
                 entry: tuple, exit: tuple):
        self.grid = []  # store the cells
        self.width = width
        self.height = height
        self.entry = entry  # tuple (0, 0)
        self.exit = exit  # tuple (19, 14)
        self.visited = [[0 for _ in range(self.width)]
                        for _ in range(self.height)]

        for _ in range(height):
            row = []
            for _ in range(width):
                row.append(15)
            self.grid.append(row)
        ex, ey = self.entry
        self.visited[ey][ex] = 1

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

    def dfs_algo(self) -> list:
        stack = [self.entry]  # to store cells and pop if cell is 0 or visited

        while stack:
            x, y = stack[-1]
            neighbors = self.find_unvisited_neighbors(x, y)
            if neighbors:
                nx, ny, direction, opposit = random.choice(neighbors)
                self.grid[y][x] = self.grid[y][x] & ~direction
                self.grid[ny][nx] = self.grid[ny][nx] & ~opposit
                self.visited[ny][nx] = 1
                stack.append((nx, ny))
            else:
                stack.pop()
        return self.grid

    def print_maze(self, grid):
        height = len(grid)
        width = len(grid[0])

        for y in range(height):
            # Top walls
            for x in range(width):
                print("+" if x == 0 else "", end="")
                print("---" if grid[y][x] & 1 else "   ", end="+")
            print()

            # Side walls
            for x in range(width):
                print("|" if grid[y][x] & 8 else " ", end="   ")
            print("|")  # right border

        # Bottom line
        print("+" + "---+"*width)

    def choose_maze_algo(self, perfect: bool) -> None:
        if perfect:
            self.dfs_algo()
        else:
            pass
