class Cell:
    def __init__(self, row, col):
        self.row = row
        self.col = col

    def __eq__(self, other_cell):
        return self.row == other_cell.row and self.col == other_cell.col
    
    def __hash__(self):
        return hash((self.row, self.col))

    def get_row(self):
        return self.row

    def get_col(self):
        return self.col
    
    def is_top_row(self):
        return self.row == 0

    def is_bottom_row(self, matrix):
        return self.row == len(matrix) - 1

    def is_left_column(self):
        return self.col == 0

    def is_right_column(self, matrix):
        return self.col == (len(matrix[1]) - 1)
    
    def is_top_left_corner(self):
        return self.is_top_row() and self.is_left_column()

    def is_top_right_corner(self, matrix):
        return self.is_top_row() and self.is_right_column(matrix)
    
    def is_bottom_left_corner(self, matrix):
        return self.is_bottom_row(matrix) and self.is_left_column()
    
    def is_bottom_right_corner(self, matrix):
        return self.is_bottom_row(matrix) and self.is_right_column(matrix)

    def is_corner(self, matrix):
        return self.is_top_left_corner() or self.is_top_right_corner(matrix) or self.is_bottom_left_corner(matrix) or self.is_bottom_right_corner(matrix)

    def get_cardinal_neighbors(self, matrix):
        neighbors = []
        if not self.is_top_row():
            neighbors.append(Cell(self.row - 1, self.col))
        if not self.is_bottom_row(matrix):
            neighbors.append(Cell(self.row + 1, self.col))
        if not self.is_left_column():
            neighbors.append(Cell(self.row, self.col - 1))
        if not self.is_right_column(matrix):
            neighbors.append(Cell(self.row, self.col + 1))
        return neighbors

    def cardinal_direction(self, cell2):
        if self.row == cell2.row and self.col == cell2.col - 1:
            return "N"
        if self.row == cell2.row and self.col == cell2.col + 1:
            return "S"
        if self.row == cell2.row - 1 and self.col == cell2.col:
            return "W"
        if self.row == cell2.row + 1 and self.col == cell2.col:
            return "E"
        
    def is_cardinal_to(self, cell2):
        if self.cardinal_direction(cell2) is None:
            return False
        else:
            return True
        
    def diagonal_direction(self, cell2):
        if self.row == cell2.row + 1 and self.col == cell2.col + 1:
            return "SE"
        if self.row == cell2.row + 1 and self.col == cell2.col - 1:
            return "SW"
        if self.row == cell2.row - 1 and self.col == cell2.col + 1:
            return "NE"
        if self.row == cell2.row - 1 and self.col == cell2.col - 1:
            return "NW"
        
    def is_diagonal_to(self, cell2):
        if self.diagonal_direction(cell2) is None:
            return False
        else:
            return True

    def get_diagonal_neighbors(self, matrix):
        neighbors = []
        if not self.is_top_row() and not self.is_left_column():
            neighbors.append(Cell(self.row - 1, self.col - 1))
        if not self.is_top_row() and not self.is_right_column(matrix):
            neighbors.append(Cell(self.row - 1, self.col + 1))
        if not self.is_bottom_row(matrix) and not self.is_left_column():
            neighbors.append(Cell(self.row + 1, self.col - 1))
        if not self.is_bottom_row(matrix) and not self.is_right_column(matrix):
            neighbors.append(Cell(self.row + 1, self.col + 1))
        return neighbors

    def get_all_neighbors(self, matrix):
        neighbors = self.get_cardinal_neighbors(matrix)
        neighbors.extend(self.get_diagonal_neighbors(matrix))
        return neighbors

    def is_obstacle(self, matrix):
        return matrix[self.row][self.col] == 1