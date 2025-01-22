from aStar import AStar
from itertools import permutations


# Função para calcular o melhor roteiro entre múltiplos destinos
def calcular_melhor_rota(mapa, pontos, eleven):
    astar = AStar(mapa)
    melhor_custo = float('inf')
    melhor_caminho = []
    start = eleven

    for ordem in permutations(pontos):
        custo_total = 0
        caminho_total = []

        for i in range(1, len(ordem)):
            goal = ordem[i]
            caminho, custo = astar.buscar(start, goal)
            if caminho is None:
                custo_total = float('inf')
                break
            custo_total += custo
            caminho_total.extend(caminho if not caminho_total else caminho[1:])
            start = goal

        if custo_total < melhor_custo:
            melhor_custo = custo_total
            melhor_caminho = caminho_total

    return melhor_caminho, melhor_custo

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
    simbolos_para_valores = {
        '.': 0,  # Piso seco
        '~': 1,  # Piso molhado
        '!': 2,  # Fiação exposta
        '=': 3,  # Porta
        '#': 4,  # Parede
        'E': 5,  # Eleven (posição inicial)
        'A': 6,  # Amigos (Denver, Mike, Lucas e Will)
        'S': 7   # Saída
    }
    
    with open(caminho_arquivo, 'r') as f:
        linhas = f.readlines()
    
    mapa = [[simbolos_para_valores[char] for char in linha.strip()] for linha in linhas]
    return mapa


def encontrar_posicoes(mapa, simbolo):
    posicoes = []
    for i, linha in enumerate(mapa):
        for j, char in enumerate(linha):
            if char == simbolo:
                posicoes.append((i, j))
    return posicoes


mapa = carregar_mapa_de_arquivo('mapa.txt')
amigos = encontrar_posicoes(mapa, 6)
eleven = encontrar_posicoes(mapa, 5)[0]
saida = encontrar_posicoes(mapa, 7)[0]
pontos = amigos + [saida]

print(pontos)





# # Exemplo de mapa (matriz 42x42 simplificada)
# mapa = [[0 for _ in range(42)] for _ in range(42)]

# # Definir áreas com diferentes terrenos
# # Definindo as pares
# for i in range(42):
#     mapa[i][0] = 4
#     mapa[i][41] = 4
#     mapa[0][i] = 4
#     mapa[41][i] = 4
# # Piso molhado
# mapa[2][6] = 1
# mapa[4][7] = 1
# mapa[2][8] = 1
# mapa[3][8] = 1
# mapa[4][8] = 1
# mapa[3][14] = 1
# mapa[4][14] = 1
# mapa[5][14] = 1
# mapa[10][10] = 1
# # Fiação exposta
# mapa[20][20] = 2
# # Porta
# mapa[30][30] = 3
# # Parede
# mapa[15][15] = 4

# # Posições iniciais e destinos
# start = (6, 40)  # Posição inicial de Eleven
# amigos = [(5, 7), (17, 37), (19, 10), (30, 11)] # Denver, Mike, Lucas e Will
# saida = (41, 40)

# # Rota completa
# pontos = [start] + amigos + [saida]
# caminho, custo = calcular_melhor_rota(mapa, pontos)

# print("Caminho encontrado:")
# exibir_mapa(mapa, caminho)
# print(f"Custo total: {custo}")
