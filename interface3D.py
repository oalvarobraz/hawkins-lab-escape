from ursina import *
from aStar import AStar
from graph import Graph
from ucs import UniformCostSearch as Uni

def carregar_mapa_de_arquivo(caminho_arquivo):
    with open(caminho_arquivo, 'r') as f:
        linhas = f.readlines()
    mapa = [[int(char) for char in linha.split()] for linha in linhas]
    return mapa

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

def mover_personagem(personagem, caminho, custo_total, texto_custo, graph, caminho_total):
    if caminho:
        pos = caminho.pop(0)
        print(f"pos: {pos}")
        personagem.position = (pos[1], 0.5, -pos[0])

        custo_acumulado = 0
        for i in range(len(caminho_total) - len(caminho) - 1):
            custo_acumulado += graph.get_weight(caminho_total[i], caminho_total[i + 1])

        # Atualizar o custo acumulado na tela
        texto_custo.text = f"Custo do caminho: {custo_acumulado:.2f}"

        invoke(mover_personagem, personagem, caminho, custo_total, texto_custo, graph, caminho_total, delay=0.4)

# Configuração do Ursina
app = Ursina()

cores_piso = {
    0: color.rgb(191/255, 191/255, 191/255),  # Piso seco
    1: color.rgb(84/255, 141/255, 212/255),   # Piso molhado
    2: color.rgb(148/255, 54/255, 52/255),    # Fiação exposta
    3: color.rgb(152/255, 72/255, 6/255),     # Porta
    4: color.rgb(89/255, 89/255, 89/255)      # Parede
}

mapa = carregar_mapa_de_arquivo('mapa.txt')
if mapa is None:
    app.quit()

labirinto = Entity()
for i in range(len(mapa)):
    for j in range(len(mapa[i])):
        tipo_piso = mapa[i][j]
        cor = cores_piso.get(tipo_piso, color.gray)
        piso = Entity(model='cube', color=cor, scale=(1, 0.1, 1), position=(j, 0, -i), parent=labirinto)
        if tipo_piso == 4:
            parede = Entity(model='cube', color=color.black, scale=(1, 1, 1), position=(j, 0.5, -i), parent=labirinto)

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

graph = criar_grafo(mapa, custos)

personagem_eleven = Entity(model='cube', color=color.red, scale=(0.5, 1, 0.5), position=(eleven[1], 0.5, -eleven[0]))
personagens_amigos = [Entity(model='cube', color=color.green, scale=(0.5, 1, 0.5), position=(amigo[1], 0.5, -amigo[0])) for amigo in amigos]

texto_custo = Text(text="Custo do caminho: 0.00", position=(-0.8, 0.4), scale=2, background=True)

caminho = None
custo_total = 0
botao = None

# Função para calcular o caminho e iniciar o movimento
def calcular_e_mover():
    global caminho, custo_total, botao
    caminho, custo_total = calcular_melhor_rota(graph, amigos, eleven, saida)
    if caminho:
        mover_personagem(personagem_eleven, caminho.copy(), custo_total, texto_custo, graph, caminho)
    # Remove o botão da cena após o clique
    if botao:
        destroy(botao)
        botao = None

botao = Button(text="Calcular Caminho", color=color.blue, scale=(0.3, 0.1), position=(0, -0.3))
botao.on_click = calcular_e_mover

def update():
    alvo_x, alvo_z = personagem_eleven.x, personagem_eleven.z
    camera.position = lerp(camera.position, (alvo_x, 10, alvo_z - 15), 0.1)
    camera.rotation_x = 30

app.run()