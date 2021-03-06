import numpy as np
import random
from itertools import product
from typing import Optional, List


class BoardState:
    def __init__(self, board: np.ndarray, current_player: int = 1, in_the_process_of_taking: bool = False):
        self.board: np.ndarray = board
        self.current_player: int = current_player
        self.in_the_process_of_taking: bool = in_the_process_of_taking

    def inverted(self) -> 'BoardState':
        return BoardState(board=self.board[::-1, ::-1] * -1, current_player=self.current_player * -1)

    def copy(self) -> 'BoardState':
        return BoardState(self.board.copy(), self.current_player, self.in_the_process_of_taking)

    def do_move(self, from_x, from_y, to_x, to_y) -> Optional['BoardState']:

        from_ = self.board[from_y, from_x]
        to_ = self.board[to_y, to_x]

        if from_x == to_x and from_y == to_y:
            return None  # invalid move')
        if max(from_x, from_y, to_x, to_y) > 7 or min(from_x, from_y, to_x, to_y) < 0:
            return None  # invalid request
        if from_ <= 0 or from_ == 3 or \
        to_ != 0:
            return None
        if self.in_the_process_of_taking and from_ != 4 and from_ != 5:
            return None

        result = self.copy()
        result.in_the_process_of_taking = False

        if from_ == 1 or from_ == 4:
            return result.move_soldier(from_x, from_y, to_x, to_y)

        elif from_ == 2 or from_ == 5:
            return result.move_stain(from_x, from_y, to_x, to_y)

    def move_stain(self, from_x, from_y, to_x, to_y):
        if abs(to_x - from_x) != abs(to_y - from_y):
            return None
        dir_x = (to_x - from_x) // abs(to_x - from_x)  # вектор направления хода
        dir_y = (to_y - from_y) // abs(to_y - from_y)
        last_x = from_x  # следующая клетка после последнего взятия
        last_y = from_y
        is_fight = 0  # is_fight == 1 если дамка сбивает хотя бы одну шашку
        # предварительная проверка пути от from_ до to_
        for x, y in zip(range(from_x + dir_x, to_x, dir_x), range(from_y + dir_y, to_y, dir_y)):
            if self.board[y, x] > 0:
                return None
            if self.board[y, x] < 0:
                is_fight = 1
                last_x = x + dir_x
                last_y = y + dir_y
                if self.board[y + dir_y, x + dir_x] != 0:
                    return None
        # проверяем, вдруг надо было обязательно бить, но дамка сделала тихий ход
        if is_fight == 0:
            for i, j in product(range(8), range(8)):
                if self.find_way(i, j):
                    return None
        # проверяем, вдруг нельзя остановить в точке назначения, так как на траектории есть
        # клетка из которой можно продолжить бить
        if is_fight:
            if not self.stain_take_check(dir_x, dir_y, to_x, to_y, last_x, last_y):
                return None
        # если всё в порядке, то надо обозначить сбитые фигуры числом 3
        for x, y in zip(range(from_x + dir_x, to_x, dir_x), range(from_y + dir_y, to_y, dir_y)):
            if self.board[y, x] < 0:
                self.board[y, x] = 3
        # финальная обработка
        self.step(from_x, from_y, to_x, to_y)
        if self.in_the_process_of_taking == False:
            self.move_end()
        else:
            self.board[to_y, to_x] = 5
        return self

    def stain_take_check(self, dir_x, dir_y, to_x, to_y, last_x, last_y):
        y_prev = last_y - dir_y
        x_prev = last_x - dir_x
        remember = self.board[y_prev, x_prev]
        self.board[y_prev, x_prev] = 3
        self.board[to_y, to_x] = 2
        fw = self.find_way(to_x, to_y)
        self.board[to_y, to_x] = 0
        if fw == False:
            for x, y in zip(range(last_x + dir_x, 8 if dir_x > 0 else -1, dir_x), \
            range(last_y + dir_y, 8 if dir_y > 0 else -1, dir_y)):
                if x == to_x:
                    continue
                if self.board[y, x] != 0:
                    break
                self.board[y, x] = 2
                if self.find_way(x, y):
                    self.board[y_prev, x_prev] = remember
                    self.board[y, x] = 0
                    return False
                self.board[y, x] = 0
        else:
            self.in_the_process_of_taking = True
        self.board[y_prev, x_prev] = remember
        return True

    def move_end(self):
        for i, j in product(range(8), range(8)):
                if self.board[i, j] == 3:
                    self.board[i, j] = 0
                if self.board[i, j] > 3:
                    self.board[i, j] -= 3

    def move_soldier(self, from_x, from_y, to_x, to_y):
        if abs(to_x - from_x) == from_y - to_y == 1:
                for i, j in product(range(8), range(8)):
                        if self.find_way(i, j):
                            return None
                self.step(from_x, from_y, to_x, to_y)

        elif abs(to_x - from_x) == abs(from_y - to_y) == 2 and \
        self.board[(to_y + from_y) // 2, (to_x + from_x) // 2] < 0:
            self.board[(to_y + from_y) // 2, (to_x + from_x) // 2] = 3
            self.step(from_x, from_y, to_x, to_y)
            if self.find_way(to_x, to_y) == 1:
                self.board[to_y, to_x] = 4
                if to_y == 0:
                    self.board[to_y, to_x] = 5
                self.in_the_process_of_taking = True
            else:
                self.move_end()
        else:
            return None
        return self

    def step(self, from_x, from_y, to_x, to_y):
        self.board[to_y, to_x] = self.board[from_y, from_x]
        self.board[from_y, from_x] = 0
        if to_y == 0:
            self.board[to_y, to_x] = 2

    def find_way(self, from_x, from_y) -> bool:  # позволяет найти варианты боя из данное позиции
        if max(from_x, from_y) > 7 or min(from_x, from_y) < 0:
            return 0
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]  # виды направлений
        if self.board[from_y, from_x] == 1 or self.board[from_y, from_x] == 4:  # если шашка
            for i in directions:
                to_x = from_x + i[0] * 2
                to_y = from_y + i[1] * 2
                if max(to_x, to_y) > 7 or min(to_x, to_y) < 0:
                    continue
                if self.board[to_y, to_x] == 0 and self.board[from_y + i[1], from_x + i[0]] < 0:
                    return 1

        if self.board[from_y, from_x] == 2 or self.board[from_y, from_x] == 5:  # если дамка
            for i in directions:
                for x, y in zip(range(from_x + i[0] * 2, 8 if i[0] > 0 else -1, i[0]), \
                range(from_y + i[1] * 2, 8 if i[1] > 0 else -1, i[1])):
                    this_field = self.board[y, x]
                    prev_field = self.board[y - i[1], x - i[0]]
                    if this_field > 0 or prev_field > 0:
                        break
                    if this_field == 0 and prev_field < 0:              
                        return True
                    if this_field < 0 and prev_field < 0:
                        break
        return False

    def get_possible_moves(self) -> List['BoardState']:
        possible_moves = []
        for from_x, from_y, to_x, to_y in product(range(8), range(8), range(8), range(8)):
            help_board = self.do_move(from_x, from_y, to_x, to_y)
            if help_board is not None:
                possible_moves.append(help_board)
        for i in range(len(possible_moves)):
            rand_ind = random.randint(0, len(possible_moves) - 1)
            possible_moves[rand_ind], possible_moves[i] = \
            possible_moves[i], possible_moves[rand_ind]
        return possible_moves

    @property
    def is_game_finished(self) -> bool:
        return self.get_possible_moves() == []

    @property
    def get_winner(self) -> Optional[int]:
        ...  # todo

    @staticmethod
    def initial_state() -> 'BoardState':
        board = np.zeros(shape=(8, 8), dtype=np.int8)
    
        # 1 - шашка первого игрока, 2 - дамка первого игрока,
        # -1 и -2 - шашка и дамка второго игрока
        # 4, 5 - шашка и дамка, которые находятся в процессе взятия,
        # 3 - сбитая фигура, ещё не снятая с доски
        
        for i, j in product(range(5, 8), range(4)):
            board[i, j * 2 + 1 - i % 2] = 1
        for i, j in product(range(3), range(4)):
            board[i, j * 2 + 1 - i % 2] = -1
        
        return BoardState(board, 1)

    def save_board(self, file_name):
        with open(file_name, "w") as f:
            f.write(str(self.current_player) + '\n')
            f.write(str(self.in_the_process_of_taking) + '\n')
            for i, j in product(range(8), range(8)):
                    f.write(str(self.board[j, i]) + '\n')

    def open_saved_board(self, file_name):
        with open(file_name, "r") as f:
             self.current_player = f.readline()
             self.in_the_process_of_taking = True if f.readline() == 'True' else False
             for i, j in product(range(8), range(8)):
                  self.board[j, i] = f.readline()
