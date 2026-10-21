"""Route finding between Spanish cities: Greedy Best-First Search vs A* (straight-line distance heuristic)."""
import heapq

def read_pathfinding_file(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()

    graph = {}  # Inicializar graph
    distances = {}

    for line in lines:
        line = line.strip()


        if len(line.split()) == 3 and line.split()[2].isdigit(): # Almeria Granada 167

            city1, city2, distance = line.split()
            distance = int(distance)

            # Inicializar el diccionario si la ciudad no existe
            if city1 not in graph:
                graph[city1] = {}
            if city2 not in graph:
                graph[city2] = {}

            # Agregar las conexiones (bidireccionales)
            graph[city1][city2] = distance
            graph[city2][city1] = distance

        elif len(line.split()) == 2 and line.split()[1].isdigit(): # Almeria 571

            city, distance = line.split()
            distances[city] = int(distance)

        else: # any other string
            continue

    return graph, distances


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


def push_into_fringe(fringe, priority, node):
    heapq.heappush(fringe, (priority, node))
    return fringe

def pop_out_fringe(fringe):
    priority, node = heapq.heappop(fringe)
    return priority, node

def explore_nodes(node):
    return graph[node]

def calculate_h(node):
    return distances[node]


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


def GBFS (start, goal):

    # declare fringe as a priority queue
    fringe = []
    visited = set()
    solution = []

    # put start inside fringe
    fringe = push_into_fringe(fringe, calculate_h(start), start)

    # loop exploring all nodes in fringe
    while fringe:
        _, node = pop_out_fringe(fringe)
        solution.append(node)
        visited.add(node)

        # if goal reached, return
        if node == goal: break

        # get posible nodes to go
        nodes = explore_nodes(node)

        # calculate evaluation
        for node in nodes:
            if node not in visited:
                eval = calculate_h(node)

                # add nodes to the fringe
                fringe = push_into_fringe(fringe, eval, node)

    return solution


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


class Node:
    def __init__(self, name, h, g, parent=None):
        self.name = name
        self.h = h
        self.g = g
        self.parent = parent # Guardamos el padre
        self.priority = self.h + self.g

    def __lt__(self, other):
        return self.priority < other.priority


def A_star(start, goal):
    fringe = []
    visited = set()
    solution = []

    root = Node(start, calculate_h(start), 0)
    fringe = push_into_fringe(fringe, root.priority, root)

    while fringe:
        _, node_start = pop_out_fringe(fringe)
        if node_start.name in visited:
            continue  # ya expandido por un camino mejor
        visited.add(node_start.name)

        if node_start.name == goal:
            curr = node_start
            while curr:
                solution.append(curr.name)
                curr = curr.parent
            return solution[::-1] # Invertimos la lista para devolver Inicio -> Fin

        nodes_destiny = explore_nodes(node_start.name)

        for node_destiny in nodes_destiny:
            if node_destiny not in visited:
                g_new = node_start.g + graph[node_start.name][node_destiny]
                new_node = Node(node_destiny, calculate_h(node_destiny), g_new, parent=node_start)
                fringe = push_into_fringe(fringe, new_node.priority, new_node)

    return solution


if __name__ == "__main__":
    start = "Malaga"
    goal = "Valladolid"
    graph, distances = read_pathfinding_file("pathfinding.txt")

    print("Greedy Best-First Search (expanded nodes):", GBFS(start, goal))
    print("A* (optimal path):", A_star(start, goal))
