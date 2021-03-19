from workspace import Workspace
from utility import dist_l1, dist_l2, dist_max, dist_names
from primitives.point import Point

from math import ceil
from random import random, choice

class Planner:
    pass

class PRM(Planner):
    def __init__(self, workspace: Workspace, delta: float = 0.01, k: int = 1, r: float = 0.0, distance_type: str = 'l2'):
        self.workspace = workspace
        self.delta = delta
        self.k = k
        self.r = r

        self.edges = []
        self.nodes = []

        self.dist = dist_names[distance_type]

    def make_path(self, a: Point, b: Point, d=None):
        if d == None:
            d = self.dist(a, b)

        N = ceil(d/self.delta)
        scales = [(n + 1) / N for n in range(N - 1)]

        return [Point(s * a.x + (1 - s) * b.x, s * a.y + (1 - s) * b.y) for s in scales]

    def construct(self, N: int):
        for _ in range(N):
            i = len(self.nodes)

            pt = Point(random() * self.workspace.dimensions[0], random() * self.workspace.dimensions[1])

            if not self.workspace.is_free(pt):
                continue

            i_pts = [{'i': j, 'pt': self.nodes[j], 'dist': self.dist(pt, self.nodes[j])} for j in range(i)]

            # Removing farther than r nodes.
            if self.r != 0:
                i_pts = [i_pt for i_pt in i_pts if i_pt['dist'] < self.r]

            # Reducing to k nodes at most.
            if self.k != 0:
                i_pts = sorted(i_pts, key=lambda i_pt: i_pt['dist'])
                i_pts = i_pts[:self.k]

            for i_pt in i_pts:
                path = self.make_path(pt, i_pt['pt'], i_pt['dist'])
                if all([self.workspace.is_free(p) for p in path]):
                    self.edges.append((i_pt['i'], i))
                    
            self.nodes.append(pt)

class RKMP(Planner):
    def __init__(self, workspace: Workspace, x0: tuple, robot, steps: int, grid_size: float, check_state):
        self.workspace = workspace
        self.robot = robot
        self.steps = steps
        self.grid_size = grid_size
        self.check_state = check_state # Must take a state and return if the state is a valid goal state.

        self.grid_width = ceil(float(workspace.dimensions[0]) / grid_size)
        self.grid_height = ceil(float(workspace.dimensions[1]) / grid_size)
        self.grid = [[[] for _ in range(self.grid_width)] for _ in range(self.grid_height)]

        self.add_state(x0)

        self.routes = {}

    def get_grid_indeces(self, x: float, y: float) -> tuple:
        i = max(0, min(int(x / self.grid_size), self.grid_width - 1))
        j = max(0, min(int(y / self.grid_size), self.grid_height - 1))

        return i, j

    def add_state(self, state: tuple):
        i, j = self.get_grid_indeces(state[0], state[1])
        self.grid[j][i].append(state)

    def sample_state(self) -> tuple:
        grid_cells = [self.grid[j][i] for i in range(self.grid_width) for j in range(self.grid_height) if len(self.grid[j][i]) > 0]
        cell = choice(grid_cells)
        return choice(cell)

    def solve(self, N: int) -> list:
        for n in range(int(N)):
            state = self.sample_state()
            a, alpha = self.robot.sample_control()

            route = self.robot.propagate(state, a, alpha, self.steps)

            if not all([self.workspace.is_free(Point(state[0], state[1])) for state in route]):
                continue

            route_complete = [self.check_state(state) for state in route]
            
            if any(route_complete):
                route = route[:route_complete.index(True) + 1]

                final_route = list(reversed(route))
                
                while state in self.routes:
                    state, route = self.routes[state]
                    final_route.extend(list(reversed(route)))
                
                final_route = reversed(final_route)
                return list(final_route)
        
            self.routes[route[-1]] = (state, route[:-1])
            self.add_state(route[-1])

        return []