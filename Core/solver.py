import networkx as nx
from memory_profiler import profile
from timeout_decorator import timeout

from Domain.cell import Cell
from Core.problem import PF4EA
from Core.state import State
from Core.utility import *
from bisect import insort

def heuristic(cell_a: Cell, cell_goal: Cell, graph: nx.DiGraph):
    try:
        h = nx.single_source_dijkstra(graph, cell_a, cell_goal, weight = "weight")[0]
    except nx.NetworkXNoPath:
        # ad es. se goal e' in un quadrato di ostacoli
        print ("Is not possible to calculate the heuristic")
        return
    return h

def compute_relaxed_path(cell_v: Cell, cell_goal: Cell, graph: nx.DiGraph):
    try:
        path = nx.dijkstra_path(graph, cell_v, cell_goal, weight = "weight")
        return path
    except nx.NetworkXNoPath:
        print("It is not possible to calculate the path.")
        return None

def compute_path_weight(graph, path):
    if not path:
        raise ValueError("The path can not be empty.")

    if len(path) < 2:
        return 0  # Un singolo nodo ha peso 0

    total_weight = 0

    # Itera attraverso coppie consecutive di nodi
    for i in range(len(path) - 1):
        current_node = path[i]
        next_node = path[i + 1]

        try:
            # Ottiene il peso dell'arco tra i nodi corrente e successivo
            edge_weight = graph[current_node][next_node]['weight']
            total_weight += edge_weight
        except KeyError:
            raise KeyError(f"Edge not found between nodes {current_node} and {next_node}")
    return total_weight

def count_wait_moves(path):
    counter = 0
    for i in range(len(path) - 1):
        if path[i] == path[i + 1]:
            counter += 1
    return counter

class Solver:
    #@timeout(300)
    @profile
    def reach_goal(self, pf4ea_instance: PF4EA, use_alternative_version):
        init = pf4ea_instance.init
        goal = pf4ea_instance.goal
        graph = pf4ea_instance.grid.graph
        agents = pf4ea_instance.agents
        max = pf4ea_instance.max

        open = []
        closed = set()
        count_open=0

        h = heuristic(init, goal, graph)

        if h is None:
            print("It was not possible to calculate the heuristic from Init.")
            return False, count_open, len(closed)
        init_state = State(init, 0, 0, h)

        # open.append(init_state)
        # alternativa a open.append(init_state) + open.sort()
        insort(open, init_state)
        count_open+=1
        while open:
            # open.sort()

            current = open.pop(0)
            closed.add(current)

            t = current.t
            v = current.v

            print(v.get_row(), v.get_col(), "at", t)

            if v == goal:
                solution = self.reconstruct_path(init_state, current)
                return solution, count_open, len(closed)

            if use_alternative_version:
                # strategia alternativa
                pi_r = compute_relaxed_path(v, goal, graph)
                if pi_r is not None:
                    if is_coll_free(pi_r, agents, t):
                        first_path = self.reconstruct_path(init_state, current)
                        second_path = pi_r[1:]
                        complete_path = first_path + second_path

                        if len(complete_path) <= max:
                            return complete_path, count_open, len(closed)

            if t < max:
                for node in graph.neighbors(v):
                    new_state = State(node, t + 1, float('inf'), heuristic(node, goal, graph))
                    if new_state not in closed:
                        is_traversable = True
                        for agent in agents:
                            try:
                                agent_cell = agent.get_path()[t]
                            except IndexError:
                                agent_cell = agent.end

                            try:
                                next_cell = agent.get_path()[t + 1]
                            # controllo che non vada out of bound, se cosi' fosse vuol dire che la prossima cella e' end
                            except IndexError:
                                next_cell = agent.end

                            if next_cell == node:
                                is_traversable = False

                            if next_cell == v and agent_cell == node:
                                is_traversable = False

                            if diagonal_exchange(v, node, agent_cell, next_cell):
                                is_traversable = False

                        if is_traversable:
                            if current.g + graph[v][node]["weight"] < new_state.g:
                                new_state.set_parent(current)
                                new_state.set_g(current.g + graph[v][node]["weight"])

                            if new_state not in open:
                                # open.append(new_state)
                                insort(open, new_state)
                                count_open+=1

        return False, count_open, len(closed)

    def reconstruct_path(self, init, current):
        if init == current:
            return [current.v]
        else:
            path = self.reconstruct_path(init, current.parent)
            path.append(current.v)
            return path