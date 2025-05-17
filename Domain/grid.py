import numpy as np
from memory_profiler import profile
from timeout_decorator import timeout

from Domain.obstacle import *
from Domain.cell import *
import networkx as nx

class Grid:
    # @timeout(300)
    @profile
    def __init__(self, rows, cols, percent_avail_cells = None, agg_factor = None):
        self.rows = rows
        self.cols = cols
        self.percent_avail_cells = percent_avail_cells
        self.agg_factor = agg_factor

        if percent_avail_cells is not None:
            self.matrix = self.create_matrix()
            self.generate_obstacles()
            self.graph = self.create_graph()

    # logica utile per il caricamento di istanza da file
    @classmethod
    def grid_from_matrix(cls, matrix):
        grid = Grid(len(matrix), len(matrix[0]))
        grid.matrix = np.array(matrix)
        grid.graph = grid.create_graph()
        return grid

    def create_matrix(self):
        grid = []
        for i in range(self.rows):
            row = [0] * self.cols
            grid.append(row)
        return np.array(grid)

    def generate_obstacles(self):
        tot_cells = self.rows * self.cols
        num_avail_cells = int(tot_cells * self.percent_avail_cells)
        num_obstacle_cells = tot_cells - num_avail_cells
        open_cells = self.get_traversables()

        while open_cells and num_obstacle_cells > 0:
            start_cell = np.random.choice(open_cells)
            obstacle = self.generate_single_obstacle(start_cell, num_obstacle_cells)

            num_obstacle_cells -= obstacle.get_size()
            computed_closed_cells = obstacle.compute_closed_cells(self.matrix)

            for c in computed_closed_cells:
                self.matrix[c.row][c.col] = 2

            open_cells = self.get_traversables()
        self.matrix[self.matrix == 2] = 0

    def generate_single_obstacle(self, starting_cell, num_obstacle_cells):
        new_obstacle = Obstacle()
        new_obstacle.add_cell(starting_cell)

        self.matrix[starting_cell.row][starting_cell.col] = 1
        dim = 1

        while new_obstacle.get_size() < self.agg_factor:
            closed_cells = set(new_obstacle.compute_closed_cells(self.matrix)) & set(self.get_traversables())
            closed_cells = list(closed_cells)

            if len(closed_cells) == 0 or (num_obstacle_cells-dim) == 0:
                return new_obstacle

            extracted_cell = np.random.choice(closed_cells)

            new_obstacle.add_cell(extracted_cell)
            self.matrix[extracted_cell.row][extracted_cell.col] = 1
            dim +=1
        return new_obstacle

    def get_matrix(self):
        return self.matrix

    def get_traversables(self):
        a = []
        for i in range(self.rows):
            for j in range(self.cols):
                if self.matrix[i][j] == 0:
                    a.append(Cell(i, j))
        return a

    def create_graph(self):
        graph = nx.DiGraph(directed=True)

        a = self.get_traversables()

        for i in range(len(a)):
            for j in range(len(a)):
                if a[i].is_cardinal_to( a[j]):
                    graph.add_edge(a[i], a[j], weight = 1)
                if a[i].is_diagonal_to(a[j]):
                    graph.add_edge(a[i], a[j], weight = np.sqrt(2))
                if a[i] == a[j]:
                    graph.add_edge(a[i], a[j], weight = 1)
        return graph