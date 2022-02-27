#!/usr/bin/env python

import math, time, os
import numpy as np
from mayavi import mlab
from random import randint

def DrawSphere(point, r=0.7, opacity=1, color=(0,0,0)):
    u, v = np.mgrid[0:2*np.pi:12j, 0:np.pi:12j]

    x = np.cos(u)*np.sin(v)
    y = np.sin(u)*np.sin(v)
    z = np.cos(v)

    x = r*x + point[0]
    y = r*y + point[1]
    z = r*z + point[2]

    mlab.mesh(x, y, z, color=color, opacity=opacity, resolution=70)

def DataVis(points):
    x, y, z = np.array(points).T
    # print(x)
    mlab.points3d(x, y, z, color=(1,1,0), resolution=90, scale_factor=1)

class Aesa:
    def __init__(self, candidates, distance):
        self.candidates = candidates
        self.distance = distance
        
        self.precomputed = [[distance(x, y) for y in candidates] for x in candidates]

    def nearest(self, target, def_dist=0, kNN=1):
        best = []

        if def_dist == 0:
            def_dist = math.inf
            best = [[-1, def_dist]] * kNN

        size = len(self.candidates)
        
        alive = list(range(size))
        
        lower_bounds = [0] * size
            
        
        while alive:

            pivot = min(alive, key=lambda i: lower_bounds[i])
            pivot_dist = self.distance(target, self.candidates[pivot])

            if def_dist == math.inf:
                if pivot_dist < best[kNN - 1][1]:
                    alive.remove(pivot)
                    best[kNN - 1] = [pivot, pivot_dist]
                    best.sort(key=lambda x: x[1])
                
            else:
                if pivot_dist < def_dist:
                    alive.remove(pivot)
                    best.append([pivot, pivot_dist])

            old_alive = alive
            alive = []
            
            for i in old_alive:    
                lower_bound = abs(pivot_dist - self.precomputed[pivot][i])
                lower_bounds[i] = max(lower_bounds[i], lower_bound)
                
                if def_dist == math.inf:
                    if lower_bounds[i] < best[kNN - 1][1]:
                        alive.append(i)
                else:
                    if lower_bounds[i] < def_dist:
                        alive.append(i)
            
        if not best:
            return []
        
        return [[self.candidates[index], dist] for index, dist in best]

dimensions = 3
limit_int = 100
def random_point():
    return [randint(0, limit_int) for i in range(dimensions)]

count = 0
def euclidean_distance(x, y):
    global count
    count += 1

    s = 0
    for i in range(len(x)):
        d = x[i] - y[i]
        s += d*d
    return math.sqrt(s)

def manhattan_distance(x, y):
    global count
    count += 1
    return np.abs(np.array(x) - np.array(y)).sum()

def hamming_distance(x, y):
    global count
    count += 1

    return np.linalg.norm(np.array(x) - np.array(y))

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def choose_alg():
    while True:
        print('Vyber funkce na vypocet vzdalenosti mezi body')
        print('1)Euklidovska metrika\n2)Manhattanska metrika\n3)Hammingova vzdalenost')

        pick = int(input("Napis cislo <1,3>: "))
        if pick < 1 or pick > 3:
            print("Spatne cislo")
        
        if pick == 1:
            return euclidean_distance
        elif pick == 2:
            return manhattan_distance
        elif pick == 3:
            return hamming_distance

def choose_method():
    while True:
        print('Vyber mezi vstupu')
        print('1)kNN\n2)rozsah')

        kNN = 1
        dist = 0

        pick = int(input("Napis cislo <1,2>: "))
        num = int(input("Napis mnozstvi/velikost: "))
        

        if pick == 1:
            return num, dist
        elif pick == 2:
            return kNN, num

    tmp = (input('kNN dotaz? (y/n): ') == 'y')

    kNN = 1
    if tmp:
        kNN = int(input('Velikost k: '))

        while kNN < 1:
            print('Spatne cislo')

            kNN = int(input('Velikost k: '))
    
    tmp = (input('rozsahovy dotaz? (y/n): ') == 'y')

    roz = 0
    if tmp:
        roz = int(input('vzdalenost rozsahu: '))

        while roz < 1:
            print('Spatne cislo')

            roz = int(input('vzdalenost rozsahu: '))

def handle_input():
    global dimensions
    global limit_int

    dimensions = int(input('Dimenze bodu (vizualizace je pouze pro 3d): '))
    while dimensions < 1:    
        print('Spatne cislo')

        dimensions = int(input('Dimenze bodu (vizualizace je pouze pro 3d): '))

    if dimensions == 3:
        fig = mlab.figure()

    limit_int = int(input('Maximalni velikost gen. cisla: '))
    while limit_int < 1:
        print('Spatne cislo')

        limit_int = int(input('Maximalni velikost gen. cisla: '))

    num_points = int(input('Pocet generovanych bodu: '))
    while num_points < 1:
        print('Spatne cislo')

        num_points = int(input('Pocet generovanych bodu: '))

    points = [random_point() for n in range(num_points)]
    if dimensions == 3:
        DataVis(points)
    
    alg = choose_alg()
    kNN, dist = choose_method()


    ntest = int(input('Pocet testovacich bodu pro zjisteni prumeru volani d(,): '))

    return points, kNN, dist, ntest, alg

def main():
    global count
    global dimensions

    do_again = True
    while do_again:
        clear()
        do_again = False

        points, kNN, dist, ntest, alg = handle_input()
        
        t0 = time.time()
        aesa = Aesa(points, alg)
        t1 = time.time()

        total_n = t1-t0
        print('{0} pocet zavolani d(,) při předpočítáváním {1}s'.format(count, total_n))

        count = 0

        target_point = random_point()

        t0 = time.time()
        result = aesa.nearest(target_point, kNN=kNN, def_dist=dist)
        t1 = time.time()

        total_n = t1-t0
        

        result.append([target_point, 0])

        if dimensions == 3:
            DrawSphere(target_point, color=(1,0,0), r=0.9)

            max_dist = 0
            for index, value in enumerate(result):
                point, val = value
                next_index = index+1

                if max_dist < val:
                    max_dist = val
                
                DrawSphere(point, color=(0,1,0))
            
            if dist > 0:
                DrawSphere(target_point, opacity=0.1, color=(1,1,1), r=dist)
            
            if kNN > 1:
                DrawSphere(target_point, opacity=0.1, color=(1,1,1), r=max_dist)

        
        print('{0} pocet zavolani d(,) pri hledani za cas {1}s'.format(count, total_n))
        count = 0
        
        total_n = []
        for i in range(ntest):
            t0 = time.time()
            result = aesa.nearest(random_point(), kNN=kNN, def_dist=dist)
            t1 = time.time()

            total_n.append(t1-t0)

        
        print('{0} prumerni pocet volani d(,) pri hledni za prumerny cas {1}s'.format(count / ntest, np.average(total_n)))
        count = 0

        print()
        if input('Ano pustit program znovu | Ne chci odejit? (y/n): ') == 'y':
            do_again = True
            if dimensions == 3:
                mlab.close()

            continue

        exit(0)
        
    

if __name__ == "__main__": main()