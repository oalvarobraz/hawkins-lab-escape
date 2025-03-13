from ursina import *
from mapa_utils import *

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

personagem_eleven = Entity(model='models_compressed/eleven.glb', scale=(1, 1, 1), position=(eleven[1], 0.09, -eleven[0]), rotation_y=180)
personagens_amigos = []
for i, amigo in enumerate(amigos):
    if i == 0:
        model = 'models_compressed/dustin.glb'
    elif i == 1:
        model = 'models_compressed/mike.glb'
    elif i == 2:
        model = 'models_compressed/lucas.glb'
    elif i == 3:
        model = 'models_compressed/will.glb'
    else:
        model = 'cube'

    personagem = Entity(
        model=model,
        scale=(0.8, 0.8, 0.8),
        position=(amigo[1], 0.09, -amigo[0]),
        rotation_y = 90 if i == 1 else 0
    )
    personagens_amigos.append(personagem)

texto_custo = Text(text="Custo do caminho: 0.00", position=(-0.8, 0.4), scale=1, background=True)

texto_ajuda = Text(
    text="[C] Trocar câmera | [0-4] Selecionar piso | [E] Editar mapa | [F5] Reset code | [+, -] Velocidade Eleven",
    position=(-0.8, -0.45),
    scale=0.7,
    background=True
)

caminho = None
caminho_total = []
custo_total = 0
botao_calcular = None
botao_editar = None
modo_edicao = False
tipo_piso_selecionado = 0
vel = 5

def calcular_e_mover():
    global caminho, custo_total, botao_calcular, caminho_total
    caminho, custo_total = calcular_heuristica_vizinho_mais_proximo(graph, amigos, eleven, saida)
    if caminho:
        caminho_total = caminho.copy()  # Armazena o caminho completo
        if len(caminho) > 0:
            caminho.pop(0)
    elif custo_total == float('inf'):
        destroy(texto_custo)
        texto_caminho = Text(text="Caminho não encontrado", position=(-0.1, 0.0), scale=1, background=True)
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

botao_calcular = Button(text="Calcular Caminho", color=color.blue, scale=(0.3, 0.1), position=(0.25, -0.43))
botao_calcular.on_click = calcular_e_mover

botao_editar = Button(text="Editar Mapa", color=color.orange, scale=(0.3, 0.1), position=(0.65, -0.43))
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
    global camera_mode, caminho, vel

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
    if held_keys['e'] and caminho is None:
        alternar_modo_edicao()
    if held_keys['+']:
        vel += 1
    if held_keys['-']:
        if vel < 3:
            vel = 3
        else :
            vel -= 1

    if caminho:
        pos_atual = (personagem_eleven.position.x, -personagem_eleven.position.z)
        pos = caminho[0]

        # Calcula a direção para o próximo ponto do caminho
        direcao_x = pos[1] - pos_atual[0]
        direcao_z = -(pos[0] - pos_atual[1])

        # Calcula o ângulo de rotação
        angulo = math.degrees(math.atan2(direcao_z, direcao_x))
        personagem_eleven.rotation_y = -angulo + 270

        # Move o personagem em direção ao próximo ponto
        velocidade = vel * time.dt
        personagem_eleven.position = (
            personagem_eleven.position.x + direcao_x * velocidade,
            personagem_eleven.position.y,
            personagem_eleven.position.z + direcao_z * velocidade
        )

        # Verifica se o personagem chegou ao próximo ponto
        if abs(personagem_eleven.position.x - pos[1]) < 0.1 and abs(personagem_eleven.position.z - (-pos[0])) < 0.1:
            caminho.pop(0)  # Remove o ponto atual do caminho

        # Atualiza o custo acumulado na tela
        custo_acumulado = 0
        for i in range(len(caminho_total) - len(caminho) - 1):
            custo_acumulado += graph.get_weight(caminho_total[i], caminho_total[i + 1])
        texto_custo.text = f"Custo do caminho: {custo_acumulado:.2f}"

app.run()