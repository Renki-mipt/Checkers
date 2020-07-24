from typing import Optional

from .boardstate import BoardState


class PositionEvaluation:
    def __call__(self, board: BoardState) -> float:
        value = 0
        for i in range(8):
            for j in range(8):
                if board.board[i, j] == 1:
                    value += 1
                if board.board[i, j] == 2:
                    value += 4
                if board.board[i, j] == -1:
                    value -= 1
                if board.board[i, j] == -2:
                    value -= 4
        return value


class AI:
    def __init__(self, position_evaluation: PositionEvaluation, search_depth: int):
        self.position_evaluation: PositionEvaluation = position_evaluation
        self.depth: int = search_depth

    def next_move(self, board: BoardState) -> Optional[BoardState]:
        max = -100
        better_board = None
        moves = board.get_possible_moves()
        for i in moves:
            value = 0
            if i.in_the_process_of_taking == 1:
                value = self.better_move(i, 0)
            else:
                value = self.better_move(i.inverted(), 1)
            if value > max:
                max = value
                better_board = i
        return better_board

    def better_move(self, board: BoardState, step_number) -> int:
        min_max = -100 if step_number % 2 == 0 else 100
        if step_number == 4:
            PE = PositionEvaluation()
            return PE.__call__(board)
        moves = board.get_possible_moves()
        value = 0
        if moves == []:
            return -100 if step_number % 2 == 0 else 100
        for i in moves:
            if i.in_the_process_of_taking is True:
                value = self.better_move(i, step_number)
            else:
                value = self.better_move(i.inverted(), step_number + 1)
            if value > min_max and step_number % 2 == 0:
                min_max = value
            if value < min_max and step_number % 2 == 1:
                min_max = value
        return min_max
