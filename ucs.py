import heapq

class UniformCostSearch:
    def __init__(self, graph):
        self.graph = graph

    def search(self, start: int, goal: int):
        """Encontra o caminho de menor custo entre dois nós, considerando pesos nas arestas"""
        heap = []
        heapq.heappush(heap, (0, start, [start])) # (custo, no, caminho)

        visited = set() # conjunto de nós visitados

        while heap:
            cost, current_node, path = heapq.heappop(heap)

            if current_node == goal:
                return path, cost
            
            if current_node in visited:
                continue
            visited.add(current_node)

            for (neighbor, weight) in self.graph.adj_list[current_node]:
                if neighbor not in visited:
                    heapq.heappush(heap, ((cost + weight), neighbor, path + [neighbor]))

        return None, float('inf')
