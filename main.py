from aStar import AStar
from graph import Graph
from mapa_utils import *

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

