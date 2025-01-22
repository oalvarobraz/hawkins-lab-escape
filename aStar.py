import heapq
from itertools import permutations

class AStar:
    def __init__(self, mapa):
        self.mapa = mapa
        self.custos = {
            0: 1,  # Piso seco
            1: 3,  # Piso molhado
            2: 6,  # Fiação exposta
            3: 4,  # Porta
            4: float('inf')  # Parede
        }

    def heuristica(self, no_atual, goal):
        return abs(no_atual[0] - goal[0]) + abs(no_atual[1] - goal[1])

    def custo_terreno(self, pos):
        return self.custos.get(self.mapa[pos[0]][pos[1]], float('inf'))

    def get_vizinhos(self, no):
        movimentos = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        vizinhos = []
        for dx, dy in movimentos:
            x, y = no[0] + dx, no[1] + dy
            if 0 <= x < len(self.mapa) and 0 <= y < len(self.mapa[0]) and self.mapa[x][y] != 4:
                vizinhos.append((x, y))
        return vizinhos

    def buscar(self, start, goal):
        open_list = []
        heapq.heappush(open_list, (0 + self.heuristica(start, goal), start))

        g_scores = {start: 0}
        pais = {start: None}
        closed_list = set()

        while open_list:
            _, atual = heapq.heappop(open_list)

            if atual in closed_list:
                continue

            if atual == goal:
                return self.reconstruir_caminho(pais, goal), g_scores[atual]

            closed_list.add(atual)

            for vizinho in self.get_vizinhos(atual):
                if vizinho in closed_list:
                    continue

                g_novo = g_scores[atual] + self.custo_terreno(vizinho)

                if vizinho not in g_scores or g_novo < g_scores[vizinho]:
                    g_scores[vizinho] = g_novo
                    f = g_novo + self.heuristica(vizinho, goal)
                    heapq.heappush(open_list, (f, vizinho))
                    pais[vizinho] = atual

        return None, float('inf')

    def reconstruir_caminho(self, pais, goal):
        caminho = []
        atual = goal
        while atual:
            caminho.append(atual)
            atual = pais[atual]
        return caminho[::-1]

def calcular_melhor_rota(mapa, pontos, start, goal):
    astar = AStar(mapa)
    melhor_custo = float('inf')
    melhor_caminho = []

    for ordem in permutations(pontos):
        custo_total = 0
        caminho_total = []

        atual = start
        for destino in ordem:
            caminho, custo = astar.buscar(atual, destino)
            if caminho is None:
                custo_total = float('inf')
                break

            custo_total += custo
            caminho_total.extend(caminho if not caminho_total else caminho[1:])
            atual = destino

        caminho_para_saida, custo_saida = astar.buscar(atual, goal)
        if caminho_para_saida is None:
            custo_total = float('inf')
        else:
            custo_total += custo_saida
            caminho_total.extend(caminho_para_saida if not caminho_total else caminho_para_saida[1:])

        if custo_total < melhor_custo:
            melhor_custo = custo_total
            melhor_caminho = caminho_total

    return melhor_caminho, melhor_custo

def calcular_heuristica_vizinho_mais_proximo(mapa, pontos, start, goal):
    astar = AStar(mapa)
    custo_total = 0
    caminho_total = []
    nao_visitados = set(pontos)
    atual = start

    while nao_visitados:
        proximo, menor_custo = None, float('inf')

        for destino in nao_visitados:
            _, custo = astar.buscar(atual, destino)
            if custo < menor_custo:
                menor_custo = custo
                proximo = destino

        if proximo is None:  # Caso algum destino não seja alcançável
            return None, float('inf')

        caminho, _ = astar.buscar(atual, proximo)
        caminho_total.extend(caminho if not caminho_total else caminho[1:])
        custo_total += menor_custo
        atual = proximo
        nao_visitados.remove(proximo)

    # Adicionar o caminho para a saída
    caminho_para_saida, custo_saida = astar.buscar(atual, goal)
    if caminho_para_saida is None:
        return None, float('inf')

    caminho_total.extend(caminho_para_saida if not caminho_total else caminho_para_saida[1:])
    custo_total += custo_saida

    return caminho_total, custo_total
