import time
import numpy as np
from random import *
from copy import deepcopy
from collections import defaultdict

def printBoard(board):
    print("+"+"-"*23+"+")
    for i, row in enumerate(board):
        print(("|" + " {} {} {} |"*3).format(*[x if x != 0 else " " for x in row]))
        if i == 8:
            print("+"+"-"*23+"+")
        elif i % 3 == 2:
            print("|" + "-------+"*2 + "-------|")

def AC3(csp, queue=None, removals=defaultdict(set)):
    if queue is None:
        queue = [(Xt, X) for Xt in csp.adjList for X in csp.adjList[Xt]]
    
    
    
    while queue:

        (Xt, Xh) = queue.pop()
        if arc_reduce(csp, Xt, Xh, removals):
            if not csp.domains[Xt]:
                return False
            elif len(csp.domains[Xt]) > 1:
                continue
            for X in csp.adjList[Xt]:
                if X != Xt:
                    queue.append((X, Xt))
    return True

def makeArcQueue(csp, Xs):
    return [(Xt, Xh) for Xh in Xs for Xt in csp.adjList[Xh]]

def arc_reduce(csp, Xt, Xh, removals):
    revised = False
    
    for x in csp.domains[Xt].copy():
        for y in csp.domains[Xh]:
            if not csp.conflicts(*Xt, x, *Xh, y):
                break
        else:
            csp.domains[Xt].remove(x)
            removals[Xt].add(x)
            revised = True
    return revised

class CSP():
    def __init__(self, variables = [], adjList = {}, domains = {}):
        self.variables = variables
        self.adjList = adjList
        self.domains = domains

    def restore_domains(self, removals):
        for X in removals:
            self.domains[X] |= removals[X]

    def conflicts(self, i1, j1, x, i2, j2, y):
        k1 = i1 // 3 * 3 + j1 // 3
        k2 = i2 // 3 * 3 + j2 // 3
        return x == y and ( i1 == i2 or j1 == j2 or k1 == k2 )

def __addEdge__(i, j, adjList):
    k = i // 3 * 3 + j // 3

    for num in range(9):
        if num != i:
            adjList[(i, j)].add((num, j))
        if num != j:
            adjList[(i, j)].add((i, num))

        row = num//3 + k//3 * 3
        col = num%3 + k%3 * 3

        if row != i or col != j:
            adjList[(i, j)].add((row, col))

def buildCSP(board):
    adjList = defaultdict(set)
    
    for i in range(9):
        for j in range(9):
            __addEdge__(i, j, adjList)
    
    
    variables = []
    assigned = []
    domains = {}

    for i in range(9):
        for j in range(9):
            if board[i][j] == '.':
                domains[(i, j)] = set(range(9))
                variables.append((i, j))
            else:
                domains[(i, j)] = set([int(board[i][j]) - 1])
                assigned.append((i, j))

    return CSP(variables, adjList, domains), assigned

def generateSudoku(clues):
    board = [['.'] * 9 for i in range(9)]

    row = [set(range(9)) for i in range(9)]
    reg = [set(range(9)) for i in range(9)]
    col = [set(range(9)) for i in range(9)]

    for cnt in range(clues):
        i, j = randrange(9), randrange(9)

        while board[i][j] != '.':
            i, j = randrange(9), randrange(9)

        k = i // 3 * 3 + j // 3

        intersect = row[i] & col[j] & reg[k]
        
        if not intersect:
            break

        num = choice(list(intersect))
        board[i][j] = chr(ord('0') + num + 1)
        row[i].remove(num)
        col[j].remove(num)
        reg[k].remove(num)

    return board

def solveSudoku(board):
    csp, assigned = buildCSP(board)
    
    AC3(csp, makeArcQueue(csp, assigned))
    
    uncertain = []
    for i in range(9):
        for j in range(9):
            if len(csp.domains[(i, j)]) > 1:
                uncertain.append((i, j))
    
    backtrack(csp, uncertain)
    
    for i in range(9):
        for j in range(9):
            if board[i][j] == '.':
                if len(csp.domains[(i, j)]) != 1:
                    return None
                board[i][j] = str( csp.domains[(i, j)].pop() + 1 )
    
    return board

def backtrack(csp, uncertain):
    if not uncertain:
        return True

    X = uncertain.pop()
    removals = defaultdict(set)

    for x in csp.domains[X]:
        domainX = csp.domains[X]
        csp.domains[X] = set([x])

        if AC3(csp, makeArcQueue(csp, [X]), removals):
            retval = backtrack(csp, uncertain)
            if retval:
                return True
            
        csp.restore_domains(removals)
        csp.domains[X] = domainX

    uncertain.append(X)

    return False

def main():
    clues = int(input('Write number of clues: '))
    
    board = generateSudoku(clues)
    printBoard(board)
    
    
    start = time.time()
    solution = solveSudoku(board)
    end = time.time() - start
    input('Show result?')
    print('It took {0}s to solve'. format(end))

    if solution != None:
        printBoard(solution)
    else:
        print("Can't solve this sudoku")

    total_n = []
    fails = 0
    for i in range(10):
        start = time.time()
        board = generateSudoku(clues)
        if board == None:
            fails += 1
        else:
            solution = solveSudoku(board)
            total_n.append(time.time() - start)


    print('Average time for solve is {0}s'.format(np.average(total_n)))
    print('Number of created sudoku that cant be solved {0}'.format(fails))

if __name__ == "__main__": main()