# Hawkins Lab Escape

## Descrição
**Hawkins Lab Escape** é um projeto que utiliza o algoritmo de busca heurística A* para resolver um problema inspirado no universo de *Stranger Things*. O objetivo é ajudar Eleven a reunir seus amigos no laboratório de Hawkins e escapar pela saída principal enquanto minimiza o custo do percurso, considerando diferentes tipos de terreno.

## Objetivo do Jogo
- Eleven deve:
  1. Encontrar Mike, Dustin, Lucas e Will em qualquer ordem.
  2. Levar o grupo até a saída do laboratório na posição final do mapa.
- Cada tipo de terreno tem um custo específico, e a melhor rota é determinada pela soma mínima desses custos.

## Funcionalidades
- Implementação do algoritmo A* para busca de menor custo.
- Representação do mapa em uma matriz 42x42.
- Custos variados para diferentes tipos de terreno:
  - Piso seco: +1
  - Piso molhado: +3
  - Fiação exposta: +6
  - Porta: +4
- Restrições de movimento: sem movimentação diagonal e sem passagem por paredes.
- Possibilidade de configurar mapas customizados.
- Exibição do custo total ao término da execução.
- Representação visual simples dos movimentos no console.

## Pré-requisitos
- Linguagem de programação utilizada: Python

## Como Executar
1. Clone este repositório:
   ```bash
   git clone https://github.com/oalvarobraz/hawkins-lab-escape.git
