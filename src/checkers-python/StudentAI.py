from random import randint
from BoardClasses import Move
from BoardClasses import Board
from copy import deepcopy
#The following part should be completed by students.
#Students can modify anything except the class name and exisiting functions and varibles.
class StudentAI():

    def __init__(self,col,row,p):
        self.col = col
        self.row = row
        self.p = p
        self.board = Board(col,row,p)
        self.board.initialize_game()
        self.color = ''
        self.opponent = {1:2,2:1}
        self.color = 2
    def get_move(self,move):
        if len(move) != 0:
            self.board.make_move(move,self.opponent[self.color])
        else:
            self.color = 1
        #moves = self.board.get_all_possible_moves(self.color)
        #index = randint(0,len(moves)-1)
        #inner_index =  randint(0,len(moves[index])-1)
        #move = moves[index][inner_index]
        val, move = self._minimax(self.board, 4, True, self.color)
        self.board.make_move(move,self.color)
        print(val)
        return move


    def _minimax(self, board: Board, depth: int, max_player:bool, color: int):
        winner = board.is_win("W" if color == 2 else "B")
        if depth == 0 or winner != 0:
            extra = 5 if winner == color else 0 if winner == 0 else -5
            return self._evaluate(board, color) + extra,  None

        if max_player:
            maxEval = float("-inf")
            best_move = None
            moves = board.get_all_possible_moves(color)
            for outerMove in range(len(moves)):
                for innerMove in range(len(moves[outerMove])):
                    board.make_move(moves[outerMove][innerMove], color)
                    evaluation = self._minimax(board, depth-1, False, 2 if color == 1 else 1)[0]
                    maxEval = max(maxEval, evaluation)
                    if maxEval == evaluation:
                        best_move = moves[outerMove][innerMove]
                    board.undo()
            return maxEval, best_move
        else:
            minEval = float("inf")
            best_move = None
            moves = board.get_all_possible_moves(color)
            for outerMove in range(len(moves)):
                for innerMove in range(len(moves[outerMove])):
                    board.make_move(moves[outerMove][innerMove], color)
                    evaluation = self._minimax(board, depth-1, True, 2 if color == 1 else 1)[0]
                    minEval = min(minEval, evaluation)
                    if minEval == evaluation:
                        best_move = moves[outerMove][innerMove]
                    board.undo()
            return minEval, best_move



    def _evaluate(self, board:Board, color: int) -> float:
        total = 0
        kings = {color: 0, color+1: 0}
        for row in range(len(board.board)):
            for col in range(len(board.board[0])):
                if board.board[row][col].is_king:
                    if board.board[row][col].color == color:
                        kings[color] += 1
                    else:
                        kings[color+1] += 1

        if color == 1:
            total += self.board.black_count - self.board.white_count
        else:
            total += self.board.white_count - self.board.black_count
        total += (kings[color] * .5) - (kings[color+1] * .5)

        return total
