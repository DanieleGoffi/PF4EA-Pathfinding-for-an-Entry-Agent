import time
import random
import numpy as np
from memory_profiler import profile
from numba.np.linalg import dot_2
from timeout_decorator import timeout

from Domain.cell import *
from Core.utility import *

class Agent:
    # @timeout(100)
    @profile
    def __init__(self, grid, length, others):
        self.path = []
        self.length = length

        if grid is not None:
            self.start = self.compute_starting_cell(grid, others)
            self.end = None
            self.compute_path(grid, others)
        else:
            self.start = None
            self.end = None

    # logica utile per il caricamento di istanza da file
    @classmethod
    def agent_from_path(cls, path):
        agent = Agent(None, 0, [])
        agent.path = path
        agent.length = len(path)
        agent.start = path[0]
        agent.end = path[-1]
        return agent

    def get_path(self):
        return self.path

    def compute_starting_cell(self, grid, others):
        candidates=grid.get_traversables().copy()
        candidate = random.choice(candidates)

        while inits_collide(candidate, others) :
            candidates.remove(candidate)
            candidate = random.choice(candidates)

        self.path.append(candidate)
        return candidate

    def compute_path (self, grid, others):
        matrix = grid.get_matrix()

        for i in range(1, self.length):
            prev_cell = self.path[i - 1]
            neighbors = prev_cell.get_all_neighbors(matrix)
            candidates = neighbors
            candidates.append(prev_cell)
            random.shuffle(candidates)
            cell = candidates.pop()

            while cell and (cell.is_obstacle(matrix) or violate_constraints(cell, i, prev_cell, others)):
                cell = candidates.pop()

            if not candidates:
                break

            self.path.append(cell)
        self.end = self.path[-1]

    def print_path(self):
        for cell in self.path:
            print(f"({cell.get_row()}, {cell.get_col()})", end=" ")
        print()