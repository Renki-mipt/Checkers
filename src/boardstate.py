import numpy as np
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
            return None  # invalid move
        if max(from_x, from_y, to_x, to_y) >= 8 or min(from_x, from_y, to_x, to_y) < 0:
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
        x = from_x + dir_x
        y = from_y + dir_y
        last_x = from_x  # следующая клетка после последнего взятия
        last_y = from_y
        is_fight = 0  # is_fight == 1 если дамка сбивает хотя бы одну шашку
        # предварительная проверка пути от from_ до to_
        while x != to_x:
            if self.board[y, x] > 0:
                return None
            if self.board[y, x] < 0:
                is_fight = 1
                last_x = x + dir_x
                last_y = y + dir_y
                if self.board[y + dir_y, x + dir_x] != 0:
                    return None
            x += dir_x
            y += dir_y
        # проверяем, вдруг надо было обязательно бить, но дамка сделала тихий ход
        if is_fight == 0:
            for i in range(8):
                for j in range(8):
                    if self.find_way(i, j):
                        return None
        # проверяем, вдруг нельзя остановить в точке назначения, так как на траектории есть
        # клетка из которой можно продолжить бить
        if is_fight:
            if not self.stain_take_check(dir_x, dir_y, to_x, to_y, last_x, last_y):
                return None
        # если всё в порядке, то надо обозначить сбитые фигуры числом 3
        x = from_x + dir_x
        y = from_y + dir_y
        while x != to_x:
            if self.board[y, x] < 0:
                self.board[y, x] = 3
            x += dir_x
            y += dir_y
        # финальная обработка
        self.step(from_x, from_y, to_x, to_y)
        if self.in_the_process_of_taking == 0:
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
        x = last_x + dir_x
        y = last_y + dir_y
        fw = self.find_way(to_x, to_y)
        self.board[to_y, to_x] = 0
        if fw == 0:
            while x >= 0 and x <= 7 and y >= 0 and y <= 7:
                if x == to_x:
                    x += dir_x
                    y += dir_y
                    continue
                if self.board[y, x] != 0:
                    break
                self.board[y, x] = 2
                if self.find_way(x, y):
                    self.board[y_prev, x_prev] = remember
                    self.board[y, x] = 0
                    return False
                self.board[y, x] = 0
                x += dir_x
                y += dir_y
        else:
            self.in_the_process_of_taking = 1
        self.board[y_prev, x_prev] = remember
        return True

    def move_end(self):
        for i in range(8):
            for j in range(8):
                if self.board[i, j] == 3:
                    self.board[i, j] = 0
                if self.board[i, j] > 3:
                    self.board[i, j] -= 3

    def move_soldier(self, from_x, from_y, to_x, to_y):
        if abs(to_x - from_x) == from_y - to_y == 1:
                for i in range(8):
                    for j in range(8):
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
                to_x = from_x + i[0] * 2
                to_y = from_y + i[1] * 2
                while max(to_x, to_y) <= 7 and min(to_x, to_y) >= 0:
                    this_field = self.board[to_y, to_x]
                    prev_field = self.board[to_y - i[1], to_x - i[0]]
                    if this_field > 0 or prev_field > 0:
                        break
                    if this_field == 0 and prev_field < 0:
                        return 1
                    if this_field < 0 and prev_field < 0:
                        break
                    to_x += i[0]
                    to_y += i[1]
        return 0

    def get_possible_moves(self) -> List['BoardState']:
        possible_moves = []
        for i in range(8):
            for j in range(8):
                if 0 < self.board[i, j] and self.board[i, j] != 3:
                    for k in range(8):
                        for m in range(8):
                            help_board = self.do_move(j, i, m, k)
                            if help_board is not None:
                                possible_moves.append(help_board)
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
        board[7, 0] = 1  # шашки первого игрока
        board[7, 2] = 1
        board[7, 4] = 1
        board[7, 6] = 1
        board[6, 1] = 1  # шашки первого игрока
        board[6, 3] = 1
        board[6, 5] = 1
        board[6, 7] = 1
        board[5, 0] = 1  # шашки первого игрока
        board[5, 2] = 1
        board[5, 4] = 1
        board[5, 6] = 1
        board[2, 1] = -1  # шашки противника
        board[2, 3] = -1
        board[2, 5] = -1
        board[2, 7] = -1
        board[1, 0] = -1  # шашки противника
        board[1, 2] = -1
        board[1, 4] = -1
        board[1, 6] = -1
        board[0, 1] = -1  # шашки противника
        board[0, 3] = -1
        board[0, 5] = -1
        board[0, 7] = -1

        return BoardState(board, 1)
