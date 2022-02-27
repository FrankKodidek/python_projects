#!/usr/bin/python

from collections import deque
from heapq import heappop, heappush
from dataclasses import dataclass
from random import shuffle
import sys, re, os, time, array

from subprocess import call
from time import sleep

step = True

@dataclass
class Cord:

    x: int
    y: int

    def right(self):
        return Cord(self.x+1, self.y)
    def up(self):
        return Cord(self.x, self.y-1)
    def left(self):
        return Cord(self.x-1, self.y)
    def down(self):
        return Cord(self.x, self.y+1)

    def __eq__(self, o):
        return (self.x == o.x) and (self.y == o.y)

class fcolors:
    open_color = '\033[93m+\033[0m'
    path_color = '\033[1m\033[92mo\033[0m'
    start_color = '\033[94m\033[91mS\033[0m'
    end_color = '\033[1m\033[91mE\033[0m'

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_neighbours(maze, cord):
    ret = []
    for neighbour in (("U", cord.up()), ("L", cord.left()), ("D", cord.down()), ("R", cord.right())):
        direction, cord = neighbour
        if maze[cord.y][cord.x] not in ('+', 'X'):
            ret.append(neighbour)

    return ret

def print_maze(maze, cord, char):
    sleep(0.05)
    clear()
    yi = 0
    maze[cord.y][cord.x] = char
    for y in maze:
        xi = 0
        for x in y:
            if Cord(xi, yi) == cord:
                print(char, end='')
            else:
                print(x, end='')
            xi += 1

        yi += 1            
        print()

    return maze

def print_path(maze, start, path):
    cord = start
    for c in list(path):
        if c == 'R':
            cord = cord.right()
        elif c == 'D':
            cord = cord.down()
        elif c == 'L':
            cord = cord.left()
        elif c == 'U':
            cord = cord.up()

        maze = print_maze(maze, cord, fcolors.path_color)

def RS(maze, start, end):
    visited = list()
    stack = deque([("S", start)])
    expanded = 0

    while stack:
        path, cord = stack.popleft()
        if cord == end:
            if path != 'S':
                path = path[:len(path) - 1]
                path = path[1:]

            return path, expanded + 1
        if cord in visited:
            continue

        visited.append(cord)
        for direction, neighbour in get_neighbours(maze, cord):
            stack.append((path + direction, neighbour))
        
        if start != cord:
            maze = print_maze(maze, cord, fcolors.open_color)
        
        expanded += 1
        shuffle(stack)
        if step:
            input()
    
    return [], expanded

def DFS(maze, start, end):
    visited = list()
    stack = deque([("S", start)])
    expanded = 0

    while stack:
        path, cord = stack.pop()
        
        if cord == end:
            if path != 'S':
                path = path[:len(path) - 1]
                path = path[1:]
                
            return path, expanded
        if cord in visited:
            continue

        visited.append(cord)
        for direction, neighbour in get_neighbours(maze, cord):
            stack.append((path + direction, neighbour))
        
        if start != cord:
            maze = print_maze(maze, cord, fcolors.open_color)
        
        expanded += 1
        if step:
            input()
    
    return [], expanded

def BFS(maze, start, end):
    visited = list()
    stack = deque([("S", start)])
    expanded = 0

    while stack:
        path, cord = stack.popleft()
        if cord == end:
            if path != 'S':
                path = path[:len(path) - 1]
                path = path[1:]

            return path, expanded + 1
        if cord in visited:
            continue

        visited.append(cord)
        for direction, neighbour in get_neighbours(maze, cord):
            stack.append((path + direction, neighbour))
        
        if start != cord:
            maze = print_maze(maze, cord, fcolors.open_color)
        
        expanded += 1
        if step:
            input()
    
    return [], expanded

def heuristic(cord, end):
    ### Manhattan distance ### 
    return abs(cord.x - end.x) + abs(cord.y - end.y)

def GS(maze, start, end):
    opened = []
    heappush(opened, (heuristic(start, end), "S", start))
    visited = list()
    expanded = 0

    while opened:
        _, path, cord = heappop(opened)

        if cord == end:
            if path != 'S':
                path = path[:len(path) - 1]
                path = path[1:]

            return path, expanded
        if cord in visited:
            continue
        visited.append(cord)
        for direction, neighbour in get_neighbours(maze, cord):
            heappush(opened, (heuristic(neighbour, end),
                                path + direction, neighbour))
        
        if start != cord:
            maze = print_maze(maze, cord, fcolors.open_color)
        
        expanded += 1
        if step:
            input()
    return [], expanded

def AStar(maze, start, end):
    opened = []
    heappush(opened, (0 + heuristic(start, end), 0, "S", start))
    visited = list()
    expanded = 0

    while opened:
        _, cost, path, cord = heappop(opened)

        if cord == end:
            if path != 'S':
                path = path[:len(path) - 1]
                path = path[1:]

            return path, expanded
        if cord in visited:
            continue
        visited.append(cord)
        for direction, neighbour in get_neighbours(maze, cord):
            heappush(opened, (cost + heuristic(neighbour, end), cost + 1,
                                path + direction, neighbour))
        
        if start != cord:
            maze = print_maze(maze, cord, fcolors.open_color)
        
        expanded += 1
        if step:
            input()
    return [], expanded

def setup_maze(maze):
    start = maze[len(maze)-2].strip()
    end = maze[len(maze)-1].strip()

    maze = maze[:len(maze)-2]
    maze = [[x for x in y] for y in maze]

    start = (re.search(r"[0-9]+, [0-9]+", start)).group(0)
    start = [int(x) for x in start.split(', ')]
    start = Cord(start[0], start[1])
    
    end = (re.search(r"[0-9]+, [0-9]+", end)).group(0)
    end = [int(x) for x in end.split(', ')]
    end = Cord(end[0], end[1])

    maze = print_maze(maze, start, fcolors.start_color)
    maze = print_maze(maze, end, fcolors.end_color)

    return maze, start, end

def file_management():
    while True:
        clear()
        mazefile = "dataset/" + input("Enter number of test file from dataset/<dd>.txt for preview: ") + ".txt"
        file_ok = False

        try:
            with open(mazefile, 'r') as f:
                maze = f.readlines()
            
            file_ok = True
        except IOError:
            print("Couldn't open/find file dataset/" + mazefile)
        
        if file_ok:
            
            # [print(x.strip()) for x in maze]
            maze = [x.strip() for x in maze]
            _, start, end = setup_maze(maze)
            print(f"start: {(start.x, start.y)}\nend: {(end.x, end.y)}")

            if 'y' == input("Do you want this maze? (y/n): "):
                return maze
        
        if 'y' == input("Do you want to leave instead? (y/n): "):
            exit(0)

def choose_alg(maze, start, end):
    while True:
        maze = print_maze(maze, start, fcolors.start_color)
        maze = print_maze(maze, end, fcolors.end_color)

        print("1) RS\n2) DFS\n3) BFS\n4) GS\n5) A*")

        pick = int(input("Select desired algorithm: "))
        if pick < 1 or pick > 5:
            print("Wrong number")
            if 'y' == input("Do you want to leave? (y/n): "):
                exit(0)
            continue

        global step
        step = (input("Set by step? (y/n): ") == 'y')    
        
        if pick == 1:
            return RS(maze, start, end)
        elif pick == 2:
            return DFS(maze, start, end)
        elif pick == 3:
            return BFS(maze, start, end)
        elif pick == 4:
            return GS(maze, start, end)
        elif pick == 5:
            return AStar(maze, start, end)
            
def main():
    maze, start, end = setup_maze(file_management())    

    path, expanded = choose_alg(maze, start, end)

    input("Draw path...")

    print_path(maze, start, path)

    print(f"---------------------------------------\n{fcolors.start_color} Start\n{fcolors.end_color} End\n{fcolors.open_color} Opened node\n{fcolors.path_color} Path\nX Wall\nspace Fresh node\n---------------------------------------\nNodes expanded: {expanded}\nPath length: {len(path) + 1}")

if __name__ == "__main__": main()
