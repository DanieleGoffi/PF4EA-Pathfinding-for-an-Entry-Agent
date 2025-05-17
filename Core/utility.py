def inits_collide(cell, agents, shift_t=0):
    for a in agents:
        if shift_t == 0:
            if a.start == cell:
                return True
        elif shift_t < len(a.get_path()):
            if a.get_path()[shift_t] == cell:
                return True
        elif shift_t >= len(a.get_path()):
            if a.end == cell:
                return True
    return False

def violate_constraints (cell, t, prev_cell, agents):
    if same_cell_at_t(cell, t, agents):
        return True

    if check_swap(cell, t, prev_cell, agents):
        return True

    if check_diagonal_exchange(cell, t, prev_cell, agents):
        return True

    return False

def same_cell_at_t(cell, t, agents):
    for a in agents:
        path = a.get_path()
        if t < len(path):
            cell_a = path[t]
            if cell_a == cell:
                return True
        else:
            if a.end == cell:
                return True
    return False

def check_swap(cell, t, prev_cell, agents):
    for a in agents:
        path = a.get_path()
        if t < len(path):
            prev = path[t - 1]
            c = path[t]

            if prev == cell and c == prev_cell:
                return True
    return False

def check_diagonal_exchange(cell, t, prev_cell, agents):
    for a in agents:
        path = a.get_path()
        if t < len(path):
            prev = path[t - 1]
            c = path[t]
            if diagonal_exchange(prev_cell, cell, c, prev):
                return True
    return False

def diagonal_exchange(c1, c2, g1, g2):
    if c1.is_diagonal_to(c2) and g1.is_diagonal_to(g2):
        if  (c1.get_row() == g1.get_row() - 1 and c1.get_col() == g1.get_col()) and (c2.get_row() == g2.get_row() + 1 and c2.get_col() == g2.get_col()):
            return True
        if  (c1.get_row() == g1.get_row() + 1 and c1.get_col() == g1.get_col()) and (c2.get_row() == g2.get_row() - 1 and c2.get_col() == g2.get_col()):
            return True
        if  (c1.get_row() == g1.get_row()  and c1.get_col() == g1.get_col() - 1) and (c2.get_row() == g2.get_row()  and c2.get_col() == g2.get_col() + 1):
            return True
        if  (c1.get_row() == g1.get_row()  and c1.get_col() == g1.get_col() + 1) and (c2.get_row() == g2.get_row()  and c2.get_col() == g2.get_col() - 1):
            return True
    return False

def is_coll_free(path_to_check, agents, shift_t=0):
    if inits_collide(path_to_check[0], agents, shift_t):
        return False

    for i in range(1, len(path_to_check)):
        prev_cell = path_to_check[i - 1]
        cell = path_to_check[i]

        if violate_constraints(cell, i+shift_t, prev_cell, agents):
            return False

    return True