from aStar import AStar
from graph import Graph
from itertools import permutations

def carregar_mapa_de_arquivo(caminho_arquivo):
    try:
        with open(caminho_arquivo, 'r') as f:
            linhas = f.readlines()
        return [[int(char) for char in linha.split()] for linha in linhas]
    except FileNotFoundError:
        print(f"Erro: Arquivo '{caminho_arquivo}' não encontrado.")
        return [[0 for _ in range(42)] for _ in range(42)]

def criar_grafo(mapa, custos):
    graph = Graph(weight=custos)
    for i in range(len(mapa)):
        for j in range(len(mapa[i])):
            node = (i, j)
            graph.add_node(node)
            for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                ni, nj = i + di, j + dj
                if 0 <= ni < len(mapa) and 0 <= nj < len(mapa[0]):
                    neighbor = (ni, nj)
                    graph.add_directed_edge(node, neighbor, custos[mapa[ni][nj]])
    return graph

def calcular_melhor_rota(graph, pontos, start, goal, search_algorithm=AStar):
    astar = search_algorithm(graph)
    melhor_custo = float('inf')
    melhor_caminho = []

    for ordem in permutations(pontos):
        custo_total = 0
        caminho_total = []

        atual = start
        for destino in ordem:
            caminho, custo = astar.search(atual, destino)
            if caminho is None:
                custo_total = float('inf')
                break

            custo_total += custo
            caminho_total.extend(caminho if not caminho_total else caminho[1:])
            atual = destino

        caminho_para_saida, custo_saida = astar.search(atual, goal)
        if caminho_para_saida is None:
            custo_total = float('inf')
        else:
            custo_total += custo_saida
            caminho_total.extend(caminho_para_saida if not caminho_total else caminho_para_saida[1:])

        if custo_total < melhor_custo:
            melhor_custo = custo_total
            melhor_caminho = caminho_total

    return melhor_caminho, melhor_custo

def calcular_heuristica_vizinho_mais_proximo(graph, pontos, start, goal, search_algorithm=AStar):
    astar = search_algorithm(graph)
    custo_total = 0
    caminho_total = []
    nao_visitados = set(pontos)
    atual = start

    while nao_visitados:
        proximo, menor_custo = None, float('inf')

        for destino in nao_visitados:
            _, custo = astar.search(atual, destino)
            if custo < menor_custo:
                menor_custo = custo
                proximo = destino

        if proximo is None:  # Caso algum destino não seja alcançável
            return None, float('inf')

        caminho, _ = astar.search(atual, proximo)
        caminho_total.extend(caminho if not caminho_total else caminho[1:])
        custo_total += menor_custo
        atual = proximo
        nao_visitados.remove(proximo)

    # Adicionar o caminho para a saída
    caminho_para_saida, custo_saida = astar.search(atual, goal)
    if caminho_para_saida is None:
        return None, float('inf')

    caminho_total.extend(caminho_para_saida if not caminho_total else caminho_para_saida[1:])
    custo_total += custo_saida

    return caminho_total, custo_total

