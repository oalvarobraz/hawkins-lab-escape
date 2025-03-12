from ursina import *
from aStar import AStar
from graph import Graph
from ucs import UniformCostSearch as Uni

# Função para carregar o mapa de um arquivo
def carregar_mapa_de_arquivo(caminho_arquivo):
    with open(caminho_arquivo, 'r') as f:
        linhas = f.readlines()
    mapa = [[int(char) for char in linha.split()] for linha in linhas]
    return mapa

# Função para criar o grafo
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

# Função para calcular a melhor rota
def calcular_melhor_rota(graph, pontos, start, goal, search_algorithm=AStar):
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

# Função para mover o personagem
def mover_personagem(personagem, caminho, custo_total, texto_custo):
    if caminho:
        pos = caminho.pop(0)
        personagem.position = (pos[1], 0.5, -pos[0])  # Ajuste nas coordenadas Z

        # Atualizar o custo acumulado
        custo_atual = custo_total - sum(graph.get_weight(caminho[i], caminho[i+1]) for i in range(len(caminho)-1))
        texto_custo.text = f"Custo do caminho: {custo_atual:.2f}"

        invoke(mover_personagem, personagem, caminho, custo_total, texto_custo, delay=0.4)


# Configuração do Ursina
app = Ursina()

# Cores para os tipos de piso
cores_piso = {
    0: color.rgb(191/255, 191/255, 191/255),  # Piso seco (cinza claro)
    1: color.rgb(84/255, 141/255, 212/255),   # Piso molhado (azul claro)
    2: color.rgb(148/255, 54/255, 52/255),    # Fiação exposta (vermelho escuro)
    3: color.rgb(152/255, 72/255, 6/255),     # Porta (marrom)
    4: color.rgb(89/255, 89/255, 89/255)      # Parede (cinza escuro)
}

# Carregar o mapa
mapa = carregar_mapa_de_arquivo('mapa.txt')
if mapa is None:
    app.quit()

# Criar o labirinto 3D
labirinto = Entity()
for i in range(len(mapa)):
    for j in range(len(mapa[i])):
        tipo_piso = mapa[i][j]
        cor = cores_piso.get(tipo_piso, color.gray)
        piso = Entity(model='cube', color=cor, scale=(1, 0.1, 1), position=(j, 0, -i), parent=labirinto)  # Ajuste nas coordenadas Z
        if tipo_piso == 4:  # Parede
            parede = Entity(model='cube', color=color.black, scale=(1, 1, 1), position=(j, 0.5, -i), parent=labirinto)  # Ajuste nas coordenadas Z

# Posições iniciais
eleven = (6, 40)
amigos = [(5, 7), (17, 37), (20, 10), (30, 11)]
saida = (41, 40)

# Custos dos pisos
custos = {
    0: 1,  # Piso seco
    1: 3,  # Piso molhado
    2: 6,  # Fiação exposta
    3: 4,  # Porta
    4: float('inf')  # Parede
}

# Criar o grafo e calcular o caminho
graph = criar_grafo(mapa, custos)
caminho, custo_total = calcular_melhor_rota(graph, amigos, eleven, saida)

# Criar personagens
personagem_eleven = Entity(model='cube', color=color.red, scale=(0.5, 1, 0.5), position=(eleven[1], 0.5, -eleven[0]))  # Ajuste nas coordenadas Z
personagens_amigos = [Entity(model='cube', color=color.green, scale=(0.5, 1, 0.5), position=(amigo[1], 0.5, -amigo[0])) for amigo in amigos]  # Ajuste nas coordenadas Z

texto_custo = Text(text="Custo do caminho: 0.00", position=(-0.8, 0.4), scale=2, background=True)

def update():
    alvo_x, alvo_z = personagem_eleven.x, personagem_eleven.z
    camera.position = lerp(camera.position, (alvo_x, 10, alvo_z - 15), 0.1)  # Suaviza o movimento
    camera.rotation_x = 30

# Mover personagens
if caminho:
    mover_personagem(personagem_eleven, caminho.copy(), custo_total, texto_custo)

# Iniciar o aplicativo
app.run()