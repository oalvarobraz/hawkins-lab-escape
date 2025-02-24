import pygame
import sys
import heapq
from itertools import permutations
from aStar import *

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

def carregar_mapa_txt(caminho_arquivo):
    with open(caminho_arquivo, 'r') as f:
        mapa = [list(map(int, linha.strip().split())) for linha in f.readlines()]
    return mapa

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
                        mapa = carregar_mapa_txt("mapa.txt")
                        return mapa, True
                    except FileNotFoundError:
                        print("Erro: Arquivo 'mapa.txt' não encontrado.")
                        return [[0 for _ in range(42)] for _ in range(42)], False

def animar_caminho(tela, mapa, caminho, tamanho_celula, start, amigos, saida, delay=0.1):
    custo_acumulado = 0
    fonte = pygame.font.Font(None, 36)

    # Tempo inicial da animação
    tempo_inicio = pygame.time.get_ticks()
    i = 0

    while i < len(caminho):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        tempo_atual = pygame.time.get_ticks()
        if tempo_atual - tempo_inicio >= delay * 1000:
            passo = caminho[i]
            custo_acumulado += AStar(mapa).custo_terreno(passo)

            desenhar_mapa(tela, mapa, tamanho_celula, start, amigos, saida)
            pygame.draw.rect(tela, YELLOW, (passo[1] * tamanho_celula, passo[0] * tamanho_celula, tamanho_celula, tamanho_celula))

            pygame.draw.rect(tela, GRAY, (10, 850, 400, 40))
            texto_custo = fonte.render(f"Custo acumulado: {custo_acumulado}", True, BLACK)
            tela.blit(texto_custo, (10, 850))

            pygame.display.flip()

            i += 1
            tempo_inicio = pygame.time.get_ticks()

def desenhar_mapa(tela, mapa, tamanho_celula, start, amigos, saida):
    linhas, colunas = len(mapa), len(mapa[0])
    for linha in range(linhas):
        for coluna in range(colunas):
            cor, _ = TERRENOS[mapa[linha][coluna]]
            pygame.draw.rect(tela, cor, (coluna * tamanho_celula, linha * tamanho_celula, tamanho_celula, tamanho_celula))
            pygame.draw.rect(tela, GRAY, (coluna * tamanho_celula, linha * tamanho_celula, tamanho_celula, tamanho_celula), 1)

    if start:
        pygame.draw.rect(tela, GREEN, (start[1] * tamanho_celula, start[0] * tamanho_celula, tamanho_celula, tamanho_celula))
    for amigo in amigos:
        pygame.draw.rect(tela, CYAN, (amigo[1] * tamanho_celula, amigo[0] * tamanho_celula, tamanho_celula, tamanho_celula))
    if saida:
        pygame.draw.rect(tela, ORANGE, (saida[1] * tamanho_celula, saida[0] * tamanho_celula, tamanho_celula, tamanho_celula))

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
                    caminho, custo_total = None, None

                elif verificar_clique_botao(evento.pos, (30, 890), (150, 40)):
                    criar_interface()
                
                elif verificar_clique_botao(evento.pos, (170, 890), (200, 40)):
                    mapa = carregar_mapa_txt("mapa.txt")
                    caminho, custo_total = [], None
                
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
                                    escolha = None

                    tela.blit(background, (0, 0))
                    if escolha == "permutações":
                        caminho, custo_total = calcular_melhor_rota(mapa, amigos, start, saida)
                    elif escolha == "heurística":
                        caminho, custo_total = calcular_heuristica_vizinho_mais_proximo(mapa, amigos, start, saida)

                    if caminho is not None:
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

                        caminho, custo_total = calcular_melhor_rota(mapa, amigos, start, saida)

                        if escolha_visualizacao == "animar":
                            tela.fill(GRAY)
                            animar_caminho(tela, mapa, caminho, tamanho_celula, start, amigos, saida)

                # Verifica clique dentro do mapa
                elif y < 840:
                    coluna = x // tamanho_celula
                    linha = y // tamanho_celula
                    if evento.button == 1:  # Botão esquerdo
                        mapa[linha][coluna] = tipo_atual

            elif evento.type == pygame.KEYDOWN:
                if pygame.K_0 <= evento.key <= pygame.K_4:
                    tipo_atual = evento.key - pygame.K_0

        desenhar_mapa(tela, mapa, tamanho_celula, start, amigos, saida)
        if caminho is None and escolha is not None:
            fonte = pygame.font.Font(None, 36)
            texto = fonte.render("Não foi possível encontrar um caminho", True, RED)
            tela.blit(texto, (largura - texto.get_width() - 10, 850))

        if caminho and custo_total is not None:
            for passo in caminho:
                pygame.draw.rect(tela, YELLOW, (passo[1] * tamanho_celula, passo[0] * tamanho_celula, tamanho_celula, tamanho_celula))

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
