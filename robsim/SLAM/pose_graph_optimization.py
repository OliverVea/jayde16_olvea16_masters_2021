# Graph is a series of Nodes connected with Edges.
# Node is a pose of the robot at some time. 
# Edge is a connection between two nodes. Two types of Edge exists:
#   - Continuity-based Edge: an Edge that connects a Node to the previous Node in the Graph
#   - Observation-based Edge: an Edge that connects a Node to other Nodes based on shared measured inputs, e.g., same feature detected.

# The goal of the optimization process is to find the state, x, (a collection of every node in the graph) that minimizes the error term:
# x* = argmin(sum_ij(e_ij * omega_ij * e_ij))
# Where omega_ij is the information matrix, which relates a transformation to the certainty in every dimension.

# x = [x0, y0, t0, x1, y1, t1, x2, y2, t2, x3, ...]

# When optimizing the Graph, the position of every node is shifted according to the total error of the graph.
# An error term between Node i and j is defined as:
# e_ij = z_ij^(-1) * T_ij
# z_ij is the transformation from Node i to j according to an edge.
# T_ij is the transformation from Node i to j according to the coordinates in the graph.
# e_ij will return as a transformation matrix and will have to be transformed to, e.g., state form.

from coordinate import Coordinate


class Node(Coordinate):
    pass

class Edge:
    pass

class Graph:
    pass