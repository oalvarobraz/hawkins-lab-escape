class Graph:
    def __init__(self, adj_list=None, weight=None) -> None:
        if adj_list is None:
            adj_list = {}
        self.adj_list = adj_list  # lista de adjacência
        self.weight = weight  # peso da aresta

    def add_directed_edge(self, u, v, weight: float = 1.0):
        """
        Adiciona uma aresta direcionada de u para v com um peso (padrão = 1.0).
        """
        if u not in self.adj_list:
            self.adj_list[u] = []
        self.adj_list[u].append((v, weight))  # Armazena o vizinho e o peso

    def add_undirected_edge(self, u, v, weight: float = 1.0):
        """
        Adiciona uma aresta não direcionada entre u e v com um peso (padrão = 1.0).
        """
        self.add_directed_edge(u, v, weight)
        self.add_directed_edge(v, u, weight)

    def degree_out(self, u) -> int:
        return len(self.adj_list.get(u, []))

    def degree_in(self, u) -> int:
        count = 0
        for neighbors in self.adj_list.values():
            for (neighbor, _) in neighbors:
                if neighbor == u:
                    count += 1
        return count

    def is_neighbor(self, u, v) -> bool:
        for (neighbor, _) in self.adj_list.get(u, []):
            if neighbor == v:
                return True
        return False

    def get_weight(self, u, v) -> float:
        for (neighbor, weight) in self.adj_list.get(u, []):
            if neighbor == v:
                return weight
        return None

    def to_adj_matrix(self):
        nodes = list(self.adj_list.keys())
        node_index = {node: i for i, node in enumerate(nodes)}
        adj_matrix = [[0 for _ in range(len(nodes))] for _ in range(len(nodes))]
        for i, node in enumerate(nodes):
            for (neighbor, weight) in self.adj_list[node]:
                j = node_index[neighbor]
                adj_matrix[i][j] = weight
        return adj_matrix

    def remove_directed_edge(self, u, v):
        if u in self.adj_list:
            self.adj_list[u] = [(neighbor, weight) for (neighbor, weight) in self.adj_list[u] if neighbor != v]

    def remove_undirected_edge(self, u, v):
        self.remove_directed_edge(u, v)
        self.remove_directed_edge(v, u)

    def add_node(self, u):
        if u not in self.adj_list:
            self.adj_list[u] = []

    def remove_node(self, u):
        # Remove todas as arestas que entram ou saem de u
        for node in self.adj_list:
            self.adj_list[node] = [(neighbor, weight) for (neighbor, weight) in self.adj_list[node] if neighbor != u]
        # Remove o nó u da lista de adjacência
        if u in self.adj_list:
            del self.adj_list[u]

    def get_neighbors(self, u):
        return self.adj_list.get(u, [])