from aStar import AStar
from itertools import permutations
from graph import Graph

# Função para exibir o mapa no console
def exibir_mapa(mapa, caminho):
    mapa_exibicao = [linha[:] for linha in mapa]  # Cria uma cópia do mapa
    for x, y in caminho:
        if 0 <= x < len(mapa_exibicao) and 0 <= y < len(mapa_exibicao[0]):  # Verifica os limites
            mapa_exibicao[x][y] = '*'  # Marca o caminho com '*'
        else:
            print(f"Coordenada fora dos limites: ({x}, {y})")

    for linha in mapa_exibicao:
        print(' '.join(str(c) for c in linha))


def carregar_mapa_de_arquivo(caminho_arquivo):
    with open(caminho_arquivo, 'r') as f:
        linhas = f.readlines()
    
    # Converte cada linha do arquivo em uma lista de inteiros
    mapa = [[int(char) for char in linha.split()] for linha in linhas]
    return mapa

def criar_grafo(mapa, custos):
    # Cria o grafo com base no mapa e nos custos
    graph = Graph(weight=custos)
    
    # Adiciona arestas ao grafo com base no mapa
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



mapa = carregar_mapa_de_arquivo('mapa.txt')

eleven = (6, 40)
amigos = [(5, 7), (17, 37), (20, 10), (30, 11)]
saida = (41, 40)

custos = {
    0: 1,  # Piso seco
    1: 3,  # Piso molhado
    2: 6,  # Fiação exposta
    3: 4,  # Porta
    4: float('inf')  # Parede
}

graph = criar_grafo(mapa, custos)

caminho, custo = calcular_melhor_rota(graph, amigos, eleven, saida)

print("Caminho encontrado:")
exibir_mapa(mapa, caminho)
print(f"Custo total: {custo}")

