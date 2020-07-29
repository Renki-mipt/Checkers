from itertools import product # надо просто нажимать пробел всё время

import pygame
import time
from pygame import Surface

from src.ai import AI, PositionEvaluation
from src.boardstate import BoardState


def draw_board(screen: Surface, pos_x: int, pos_y: int, elem_size: int, board: BoardState):
    dark = (0, 0, 0)
    white = (200, 200, 200)

    for y, x in product(range(8), range(8)):
        color = white if (x + y) % 2 == 0 else dark
        position = pos_x + x * elem_size, pos_y + y * elem_size, elem_size, elem_size
        pygame.draw.rect(screen, color, position)

        figure = board.board[y, x]

        if figure == 0:
            continue

        if figure > 0:
            if figure == 3:
                figure_color = 200, 200, 200
            elif figure > 3:
                figure_color = 255, 0, 0
            else:
                figure_color = 255, 255, 255
        else:
            figure_color = 100, 100, 100
        r = elem_size // 2 - 10
        
        pygame.draw.circle(screen, figure_color, (position[0] + elem_size // 2, position[1] + elem_size // 2), r)
        if abs(figure) == 2 or figure == 5:
            r = 5
            negative_color = [255 - e for e in figure_color]
            pygame.draw.circle(screen, negative_color, (position[0] + elem_size // 2, position[1] + elem_size // 2), r)

def game_loop(screen: Surface, board: BoardState, ai: AI):
    grid_size = screen.get_size()[0] // 8

    player = 1
    while True:        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
        
        start_time = time.time()
       
        while True:
            new_board = ai.next_move(board if player == 1 else board.inverted())
            if new_board is None:
                break
            else:
                board = new_board if player == 1 else new_board.inverted()
                if new_board.in_the_process_of_taking == False:
                    player = player % 2 + 1
                    break
        
        if time.time() - start_time > 30.0:
            print('TL')
            break
                    
        draw_board(screen, 0, 0, grid_size, board)
        pygame.display.flip()
        
pygame.init()

screen: Surface = pygame.display.set_mode([512, 512])
ai = AI(PositionEvaluation(), search_depth=4)

game_loop(screen, BoardState.initial_state(), ai)

pygame.quit()    



  
