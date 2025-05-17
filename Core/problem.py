from Domain.grid import Grid
from Domain.agent import Agent
from Domain.cell import Cell

class PF4EA:
    def __init__(self, grid = None, agents = None, init = None, goal = None, max = None):
        self.grid = grid
        self.agents = agents
        self.init = init
        self.goal = goal
        self.max = max

    def matrix_with_agents(self):
        matrix = self.grid.get_matrix().copy()
        val = 5
        for agent in self.agents:
            for j in range(len(agent.get_path())):
                cell = agent.get_path()[j]
                matrix[cell.get_row()][cell.get_col()] = val
            val += 1

        matrix[self.init.get_row()][self.init.get_col()] = 2
        matrix[self.goal.get_row()][self.goal.get_col()] = 3

        return matrix

    def matrix_at_time(self, t, path):
        matrix = self.grid.get_matrix().copy()

        val = 5
        for agent in self.agents:
            if t < len(agent.get_path()):
                matrix[agent.path[t].get_row()][agent.path[t].get_col()] = val
            else:
                matrix[agent.end.get_row()][agent.end.get_col()] = val
            val += 1

        if t < len(path):
            matrix[path[t].get_row()][path[t].get_col()] = 2
        else:
            return False
        return matrix

    def matrix_with_sol(self, sol):
        matrix = self.matrix_with_agents()
        for cell in sol:
            if cell != self.init and cell != self.goal:
                matrix[cell.get_row()][cell.get_col()] = 3
        return matrix

    def save_instance_to_file(self, filename):
        f = open(filename, 'w')

        matrix = self.grid.get_matrix()
        f.write("[")
        for i, row in enumerate(matrix):
            if i == len(matrix) - 1:
                f.write(" [" + " ".join(map(str, row)) + "]]")
            else:
                f.write(" [" + " ".join(map(str, row)) + "]\n")
        f.write("]\n")
        f.write(f"{self.init.get_row()} {self.init.get_col()}\n")
        f.write(f"{self.goal.get_row()} {self.goal.get_col()}\n")
        f.write(f"{self.max}\n")
        f.write(f"{len(self.agents)}\n")
        for agent in self.agents:
            f.write("[")
            for cell in agent.get_path():
                f.write(f"({cell.get_row()}, {cell.get_col()})")
            f.write("]\n")
        f.close()

    def read_instance_from_file(self, filename):
        f = open(filename, "r")
        lines = f.readlines()
        grid = []
        i = 0
        while lines[i].strip().startswith("["):
            row = list(map(int, lines[i].strip().replace("[", "").replace("]", "").split()))
            grid.append(row)
            i += 1
        self.grid = Grid.grid_from_matrix(grid)

        init_row, init_col = map(int, lines[i].split())
        self.init = Cell(init_row, init_col)

        goal_row, goal_col = map(int, lines[i + 1].split())
        self.goal = Cell(goal_row, goal_col)
        self.max = int(lines[i + 2].strip())

        num_agents = int(lines[i + 3].strip())
        self.agents = []
        for j in range(num_agents):
            path_str = lines[i + 4 + j].strip().replace("[", "").replace("]", "")
            path = [Cell(int(coord.strip("()").split(",")[0]),
                         int(coord.strip("()").split(",")[1]))
                    for coord in path_str.split(")(")]
            new_agent = Agent.agent_from_path(path)
            self.agents.append(new_agent)
        f.close()