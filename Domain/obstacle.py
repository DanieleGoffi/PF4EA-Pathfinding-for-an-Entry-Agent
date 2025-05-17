class Obstacle:
    def __init__(self):
        self.cell_list = []

    def add_cell(self, cell):
        self.cell_list.append(cell)
    
    def get_cell_list(self):
        return self.cell_list

    def compute_closed_cells(self, matrix):
        closed_cells = []
        for cell in self.cell_list:
            for cardinal_neighbor in cell.get_cardinal_neighbors(matrix):
                closed_cells.append(cardinal_neighbor)

        closed_cells = set(closed_cells) - set(self.cell_list)
        return list(closed_cells)

    def get_size(self):
        return len(self.cell_list)