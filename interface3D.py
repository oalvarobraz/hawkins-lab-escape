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

        if proximo is None:
            return None, float('inf')

        caminho, _ = astar.search(atual, proximo)
        caminho_total.extend(caminho if not caminho_total else caminho[1:])
        custo_total += menor_custo
        atual = proximo
        nao_visitados.remove(proximo)

    caminho_para_saida, custo_saida = astar.search(atual, goal)
    if caminho_para_saida is None:
        return None, float('inf')

    caminho_total.extend(caminho_para_saida if not caminho_total else caminho_para_saida[1:])
    custo_total += custo_saida

    return caminho_total, custo_total

def mover_personagem(personagem, caminho, custo_total, texto_custo, graph, caminho_total):
    if caminho:
        pos = caminho.pop(0)
        personagem.position = (pos[1], 0.5, -pos[0])

        custo_acumulado = 0
        for i in range(len(caminho_total) - len(caminho) - 1):
            custo_acumulado += graph.get_weight(caminho_total[i], caminho_total[i + 1])

        # Atualizar o custo acumulado na tela
        texto_custo.text = f"Custo do caminho: {custo_acumulado:.2f}"

        invoke(mover_personagem, personagem, caminho, custo_total, texto_custo, graph, caminho_total, delay=0.4)

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
piso_entities = []

for i in range(len(mapa)):
    linha_entities = []
    for j in range(len(mapa[i])):
        tipo_piso = mapa[i][j]
        cor = cores_piso.get(tipo_piso, color.gray)
        piso = Entity(model='cube', color=cor, scale=(1, 0.1, 1), position=(j, 0, -i), parent=labirinto, collider='box')
        if tipo_piso == 4:
            parede = Entity(model='cube', color=color.black, scale=(1, 1, 1), position=(j, 0.5, -i), parent=labirinto)
        linha_entities.append(piso)
    piso_entities.append(linha_entities)

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

texto_custo = Text(text="Custo do caminho: 0.00", position=(-0.8, 0.4), scale=1, background=True)

caminho = None
custo_total = 0
botao_calcular = None
botao_editar = None
modo_edicao = False
tipo_piso_selecionado = 0

def calcular_e_mover():
    global caminho, custo_total, botao_calcular
    caminho, custo_total = calcular_melhor_rota(graph, amigos, eleven, saida)
    if caminho:
        mover_personagem(personagem_eleven, caminho.copy(), custo_total, texto_custo, graph, caminho)
    # Remove o botão da cena após o clique
    if botao_calcular:
        destroy(botao_calcular)
        botao_calcular = None
        destroy(botao_editar)

def alternar_modo_edicao():
    global modo_edicao, botao_editar
    modo_edicao = not modo_edicao
    if modo_edicao:
        botao_editar.text = "Sair do Modo Edição"
        camera.position = (len(mapa[0]) // 2, 150, -len(mapa) // 2)  # Centraliza a câmera
        camera.rotation_x = 90  # Visão de cima
    else:
        botao_editar.text = "Editar Mapa"
        camera.rotation_x = 30

def editar_mapa():
    global graph
    if modo_edicao and mouse.left:
        if mouse.hovered_entity in [piso for linha in piso_entities for piso in linha]:
            i = int(-mouse.hovered_entity.z)
            j = int(mouse.hovered_entity.x)

            mapa[i][j] = tipo_piso_selecionado
            mouse.hovered_entity.color = cores_piso.get(tipo_piso_selecionado, color.gray)

            for child in labirinto.children:
                if child.position == (j, 0.5, -i) and isinstance(child, Entity):
                    destroy(child)

            if tipo_piso_selecionado == 4:
                parede = Entity(model='cube', color=color.black, scale=(1, 1, 1), position=(j, 0.5, -i), parent=labirinto)
            
            graph = criar_grafo(mapa, custos)
            

def mudar_tipo_piso():
    global tipo_piso_selecionado
    if held_keys['0']:
        tipo_piso_selecionado = 0  # Piso seco
    elif held_keys['1']:
        tipo_piso_selecionado = 1  # Piso molhado
    elif held_keys['2']:
        tipo_piso_selecionado = 2  # Fiação exposta
    elif held_keys['3']:
        tipo_piso_selecionado = 3  # Porta
    elif held_keys['4']:
        tipo_piso_selecionado = 4  # Parede

botao_calcular = Button(text="Calcular Caminho", color=color.blue, scale=(0.3, 0.1), position=(0, -0.3))
botao_calcular.on_click = calcular_e_mover

botao_editar = Button(text="Editar Mapa", color=color.orange, scale=(0.3, 0.1), position=(0, -0.45))
botao_editar.on_click = alternar_modo_edicao

CAMERA_MODES = {
    'FIXA': 'fixa',
    'TERCEIRA_PESSOA': 'terceira_pessoa'
}

camera_mode = CAMERA_MODES['TERCEIRA_PESSOA']

def alternar_camera():
    global camera_mode
    if camera_mode == CAMERA_MODES['FIXA']:
        camera_mode = CAMERA_MODES['TERCEIRA_PESSOA']
    else:
        camera_mode = CAMERA_MODES['FIXA']

def update():
    global camera_mode

    if modo_edicao:
        editar_mapa()
        mudar_tipo_piso()
    else:
        if camera_mode == CAMERA_MODES['FIXA']:
            camera.position = (len(mapa[0]) // 2, 150, -len(mapa) // 2)
            camera.rotation_x = 90
        elif camera_mode == CAMERA_MODES['TERCEIRA_PESSOA']:
            alvo_x, alvo_z = personagem_eleven.x, personagem_eleven.z
            camera.position = lerp(camera.position, (alvo_x, 10, alvo_z - 15), 0.1)
            camera.rotation_x = 30

    if held_keys['c']:
        alternar_camera()
        held_keys['c'] = False

app.run()