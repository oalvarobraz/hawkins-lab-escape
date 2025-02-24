import heapq

def heuristica(no_atual, goal):
    return abs(no_atual[0] - goal[0]) + abs(no_atual[1] - goal[1])


class AStar:
    def __init__(self, graph, heuristic=heuristica, custo_terreno=None):
        self.graph = graph
        self.heuristic = heuristic
        self.custo_terreno = custo_terreno

    def get_vizinhos(self, node):
        neighbors = []
        for (neighbor, edge_cost) in self.graph.adj_list[node]:
            neighbors.append((neighbor, edge_cost))
        return neighbors

    def search(self, start, goal):
        """f(n) = g(n) + h(n), onde g(n) é o custo até o momento e h(n) é o custo estimado"""
        heap = []
        heapq.heappush(heap, (0 + self.heuristic(start, goal), 0, start, [start]))  # (f(n), no, caminho)
        visited = set()

        while heap:
            f_n, g_n, current_node, path = heapq.heappop(heap)

            if current_node == goal:
                return path, g_n

            if current_node in visited:
                continue
            visited.add(current_node)

            for (neighbor, edge_cost) in self.graph.adj_list[current_node]:
                if neighbor not in visited:
                    new_g_n = g_n + edge_cost
                    new_f_n = new_g_n + self.heuristic(neighbor, goal)
                    heapq.heappush(heap, (new_f_n, new_g_n, neighbor, path + [neighbor]))
        return None, float('inf')
