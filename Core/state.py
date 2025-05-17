class State:
    def __init__(self, v, t, g, h):
        self.v = v
        self.t = t

        self.g = g
        self.h = h

        self.f = self.g + self.h
        self.parent = None

    def __eq__(self, other_state):
        return self.v == other_state.v and self.t == other_state.t

    def __hash__(self):
        return hash((self.v, self.t))

    def __lt__(self, other):
        return self.f < other.f

    def set_g(self, g):
        self.g = g
        self.f = self.g + self.h

    def set_h(self, h):
        self.h = h

    def set_parent(self, parent):
        self.parent = parent