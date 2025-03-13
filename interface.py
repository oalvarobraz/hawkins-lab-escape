import pygame
import sys
from itertools import permutations
from aStar import *
from graph import Graph

# Cores
WHITE = (191, 191, 191)
BLACK = (89, 89, 89)
GRAY = (200, 200, 200)
BLUE = (84, 141, 212)
GREEN = (0, 255, 0)
RED = (148, 54, 52)
YELLOW = (255, 255, 0)
ORANGE = (152, 72, 6)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)

# Tipos de terreno e suas cores
TERRENOS = {
    0: (WHITE, "Piso seco"),
    1: (BLUE, "Piso molhado"),
    2: (RED, "Fiação exposta"),
    3: (ORANGE, "Porta"),
    4: (BLACK, "Parede"),
}

LARGURA_TELA = 840
ALTURA_TELA = 940
TAMANHO_CELULA = 20
LINHAS, COLUNAS = 42, 42

def desenhar_botao(tela, texto, posicao, tamanho, cor_base, cor_texto):
    fonte = pygame.font.Font(None, 36)
    pygame.draw.rect(tela, cor_base, (*posicao, *tamanho))
    texto_renderizado = fonte.render(texto, True, cor_texto)
    texto_x = posicao[0] + (tamanho[0] - texto_renderizado.get_width()) // 2
    texto_y = posicao[1] + (tamanho[1] - texto_renderizado.get_height()) // 2
    tela.blit(texto_renderizado, (texto_x, texto_y))

def verificar_clique_botao(posicao_mouse, posicao_botao, tamanho_botao):
    x, y = posicao_mouse
    bx, by = posicao_botao
    bw, bh = tamanho_botao
    return bx <= x <= bx + bw and by <= y <= by + bh

def carregar_mapa_de_arquivo(caminho_arquivo):
    try:
        with open(caminho_arquivo, 'r') as f:
            linhas = f.readlines()
        return [[int(char) for char in linha.split()] for linha in linhas]
    except FileNotFoundError:
        print(f"Erro: Arquivo '{caminho_arquivo}' não encontrado.")
        return [[0 for _ in range(COLUNAS)] for _ in range(LINHAS)]

def criar_grafo(mapa, custos):
    graph = Graph(weight=custos)
    for i in range(LINHAS):
        for j in range(COLUNAS):
            node = (i, j)
            graph.add_node(node)
            for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                ni, nj = i + di, j + dj
                if 0 <= ni < LINHAS and 0 <= nj < COLUNAS:
                    neighbor = (ni, nj)
                    graph.add_directed_edge(node, neighbor, custos[mapa[ni][nj]])
    return graph

def desenhar_mapa(tela, mapa, start, amigos, saida):
    for i in range(LINHAS):
        for j in range(COLUNAS):
            cor, _ = TERRENOS[mapa[i][j]]
            pygame.draw.rect(tela, cor, (j * TAMANHO_CELULA, i * TAMANHO_CELULA, TAMANHO_CELULA, TAMANHO_CELULA))
            pygame.draw.rect(tela, GRAY, (j * TAMANHO_CELULA, i * TAMANHO_CELULA, TAMANHO_CELULA, TAMANHO_CELULA), 1)

    if start:
        pygame.draw.rect(tela, GREEN, (start[1] * TAMANHO_CELULA, start[0] * TAMANHO_CELULA, TAMANHO_CELULA, TAMANHO_CELULA))
    for amigo in amigos:
        pygame.draw.rect(tela, CYAN, (amigo[1] * TAMANHO_CELULA, amigo[0] * TAMANHO_CELULA, TAMANHO_CELULA, TAMANHO_CELULA))
    if saida:
        pygame.draw.rect(tela, ORANGE, (saida[1] * TAMANHO_CELULA, saida[0] * TAMANHO_CELULA, TAMANHO_CELULA, TAMANHO_CELULA))

def animar_caminho(tela, mapa, caminho, start, amigos, saida, delay=100, custos={0: 1, 1: 3, 2: 6, 3: 4, 4: float('inf')}):
    custo_acumulado = 0
    fonte = pygame.font.Font(None, 36)

    for passo in caminho:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        desenhar_mapa(tela, mapa, start, amigos, saida)
        pygame.draw.rect(tela, YELLOW, (passo[1] * TAMANHO_CELULA, passo[0] * TAMANHO_CELULA, TAMANHO_CELULA, TAMANHO_CELULA))
        
        if passo != start:
            custo_passo = custos[mapa[passo[0]][passo[1]]]
            custo_acumulado += custo_passo
        pygame.draw.rect(tela, GRAY, (10, 850, 400, 40))
        texto_custo = fonte.render(f"Custo acumulado: {custo_acumulado}", True, BLACK)
        tela.blit(texto_custo, (10, 850))
        
        pygame.display.flip()
        pygame.time.delay(delay)

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

def mostrar_opcoes_iniciais():
    pygame.init()
    largura, altura = 720, 445
    tela = pygame.display.set_mode((largura, altura))
    pygame.display.set_caption("Fuga do Laboratório - Menu Inicial")

    try:
        background = pygame.image.load("imgs/background_principal.jpeg")
        background = pygame.transform.scale(background, (largura, altura))
    except pygame.error:
        print("Erro ao carregar a imagem de fundo. Certifique-se de que 'background.jpg' está no diretório do projeto.")
        background = None

    rodando = True
    while rodando:
        # Desenhar o fundo
        if background:
            tela.blit(background, (0, 0))
        else:
            tela.fill(GRAY)

        # Desenhar botões
        desenhar_botao(tela, "Criar Mapa", (50, altura - 60), (200, 50), BLUE, WHITE)
        desenhar_botao(tela, "Carregar Mapa", (largura - 250, altura - 60), (200, 50), ORANGE, WHITE)

        pygame.display.flip()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif evento.type == pygame.MOUSEBUTTONDOWN:
                pos_mouse = pygame.mouse.get_pos()

                if verificar_clique_botao(pos_mouse, (50, altura - 60), (200, 50)):
                    return [[0 for _ in range(42)] for _ in range(42)], False

                elif verificar_clique_botao(pos_mouse, (largura - 250, altura - 60), (200, 50)):
                    try:
                        mapa = carregar_mapa_de_arquivo("mapa.txt")
                        return mapa, True
                    except FileNotFoundError:
                        print("Erro: Arquivo 'mapa.txt' não encontrado.")
                        return [[0 for _ in range(42)] for _ in range(42)], False

def mostrar_custo(tela, custo_total, largura):
    fonte = pygame.font.Font(None, 36)
    texto_custo = fonte.render(f"Custo total do caminho: {custo_total}", True, BLACK)
    tela.blit(texto_custo, (largura - texto_custo.get_width() - 10, 850))

def criar_interface():
    mapa, mapa_carregado = mostrar_opcoes_iniciais()
    caminho = None
    largura, altura = 840, 940
    linhas, colunas = 42, 42
    tamanho_celula = 840 // colunas

    tela = pygame.display.set_mode((largura, altura))
    pygame.display.set_caption("Fuga do Laboratório - A*")

    start = (6, 40)
    amigos = [(5, 7), (17, 37), (20, 10), (30, 11)]
    saida = (41, 40)

    rodando = True
    tipo_atual = 0
    escolha = None
    graph = criar_grafo(mapa, {0: 1, 1: 3, 2: 6, 3: 4, 4: float('inf')})
    
    while rodando:
        tela.fill(GRAY)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif evento.type == pygame.MOUSEBUTTONDOWN:
                x, y = evento.pos
                if verificar_clique_botao(evento.pos, (largura-180, 890), (100, 40)):
                    mapa = [[0 for _ in range(colunas)] for _ in range(linhas)]
                    graph = criar_grafo(mapa, {0: 1, 1: 3, 2: 6, 3: 4, 4: float('inf')})
                    caminho, custo_total = None, None
                    escolha = None

                elif verificar_clique_botao(evento.pos, (30, 890), (150, 40)):
                    criar_interface()
                    escolha = None
                
                elif verificar_clique_botao(evento.pos, (170, 890), (200, 40)):
                    mapa = carregar_mapa_de_arquivo("mapa.txt")
                    graph = criar_grafo(mapa, {0: 1, 1: 3, 2: 6, 3: 4, 4: float('inf')})
                    caminho, custo_total = None, None
                    escolha = None
                
                elif verificar_clique_botao(evento.pos, (400, 890), (220, 40)):
                    background = pygame.image.load("imgs/image6.webp")
                    background = pygame.transform.scale(background, (largura, altura))
                    tela.blit(background, (0, 0))

                    desenhar_botao(tela, "Permutações", ((largura-300)//2, (altura-250)//2), (300, 50), WHITE, BLACK)
                    desenhar_botao(tela, "Heurística", ((largura-300)//2, (altura-100)//2), (300, 50), WHITE, BLACK)
                    desenhar_botao(tela, "Voltar", ((largura-300)//2, (altura+50)//2), (300, 50), WHITE, BLACK)
                    pygame.display.flip()

                    escolha = None
                    while escolha is None:
                        for evento_prompt in pygame.event.get():
                            if evento_prompt.type == pygame.QUIT:
                                pygame.quit()
                                sys.exit()
                            elif evento_prompt.type == pygame.MOUSEBUTTONDOWN:
                                x, y = evento_prompt.pos
                                if verificar_clique_botao(evento_prompt.pos, ((largura-300)//2, (altura-250)//2), (300, 50)):
                                    escolha = "permutações"
                                elif verificar_clique_botao(evento_prompt.pos, ((largura-300)//2, (altura-100)//2), (300, 50)):
                                    escolha = "heurística"
                                elif verificar_clique_botao(evento_prompt.pos, ((largura-300)//2, (altura+50)//2), (300, 50)):
                                    escolha = "back"
                                    

                    tela.blit(background, (0, 0))
                    if escolha == "permutações":
                        caminho, custo_total = calcular_melhor_rota(graph, amigos, start, saida)
                    elif escolha == "heurística":
                        caminho, custo_total = calcular_heuristica_vizinho_mais_proximo(graph, amigos, start, saida)

                    if caminho is not None and custo_total != float('inf'):
                        desenhar_botao(tela, "Animar célula por célula", ((largura-350)//2,(altura-100)//2), (350, 40), WHITE, BLACK)
                        desenhar_botao(tela, "Mostrar o caminho direto", ((largura-350)//2,(altura)//2), (350, 40), WHITE, BLACK)
                        pygame.display.flip()

                        escolha_visualizacao = None
                        while escolha_visualizacao is None:
                            for evento_prompt in pygame.event.get():
                                if evento_prompt.type == pygame.QUIT:
                                    pygame.quit()
                                    sys.exit()
                                elif evento_prompt.type == pygame.MOUSEBUTTONDOWN:
                                    x, y = evento_prompt.pos
                                    if verificar_clique_botao(evento_prompt.pos, ((largura-350)//2,(altura-100)//2), (350, 40)):
                                        escolha_visualizacao = "animar"
                                    elif verificar_clique_botao(evento_prompt.pos, ((largura-350)//2,(altura)//2), (350, 40)):
                                        escolha_visualizacao = "direto"

                        # caminho, custo_total = calcular_melhor_rota(graph, amigos, start, saida, SimulatedAnnealing)

                        if escolha_visualizacao == "animar":
                            tela.fill(GRAY)
                            animar_caminho(tela, mapa, caminho, start, amigos, saida)

                # Verifica clique dentro do mapa
                elif y < 840:
                    coluna = x // TAMANHO_CELULA
                    linha = y // TAMANHO_CELULA
                    if evento.button == 1:  # Botão esquerdo
                        mapa[linha][coluna] = tipo_atual
                        graph = criar_grafo(mapa, {0: 1, 1: 3, 2: 6, 3: 4, 4: float('inf')})

            elif evento.type == pygame.KEYDOWN:
                if pygame.K_0 <= evento.key <= pygame.K_4:
                    tipo_atual = evento.key - pygame.K_0

        desenhar_mapa(tela, mapa, start, amigos, saida)
        if (caminho is None or custo_total == float('inf')) and escolha is not None and escolha != "back":
            fonte = pygame.font.Font(None, 36)
            texto = fonte.render("Não foi possível encontrar um caminho", True, RED)
            tela.blit(texto, (largura - texto.get_width() - 10, 850))

        if caminho and custo_total is not None:
            for passo in caminho:
                pygame.draw.rect(tela, YELLOW, (passo[1] * TAMANHO_CELULA, passo[0] * tamanho_celula, tamanho_celula, tamanho_celula))

            mostrar_custo(tela, custo_total, largura)

        fonte = pygame.font.Font(None, 36)
        texto = fonte.render(f"Terreno Atual: {TERRENOS[tipo_atual][1]} (Tecla {tipo_atual})", True, BLACK)
        tela.blit(texto, (10, 850))

        desenhar_botao(tela, "Menu", (30, 890), (100, 40), BLUE, WHITE) 
        desenhar_botao(tela, "Carregar Mapa", (170, 890), (200, 40), PURPLE, WHITE)
        desenhar_botao(tela, "Calcular Caminho", (400, 890), (220, 40), RED, WHITE)
        desenhar_botao(tela, "Reset", (largura-180, 890), (150, 40), ORANGE, WHITE)

        pygame.display.flip()
    

if __name__ == "__main__":
    criar_interface()
