from BoardClasses import Move
from BoardClasses import Board
from copy import deepcopy
import time
import random
import math


class Node:
    def __init__(self, gameState, move: Move, amountChildren: int, board: Board):
        self.gameState = gameState
        self.plays = 10
        self.wins = 0.5
        self.amafPlays = 10
        self.amafWins = 0.5
        self.children = []
        self.parent = None
        self.movesExpanded = set()
        self.movesUnfinished = amountChildren
        self.move = move
        self.board = board

    def propagateCompletion(self) -> None:
        """
        If all children of this move has been expanded then tell parent
        that they have one less child to expand.
        """
        if self.parent == None:
            return
        
        if self.movesUnfinished > 0:
            self.movesUnfinished -= 1
        self.parent.propagateCompletion()

    def addChild(self, node) -> None:
        self.children.append(node)
        self.movesExpanded.add(tuple(node.move))
        node.parent = self
    
    def hasChildren(self) -> bool:
        return len(self.children) > 0
    
    def getWinsPlays(self) -> "int, int":
        return self.wins, self.plays
   
    def getAmafWinsPlays(self) -> "int, int":
        return self.amafWins, self.amafPlays
    
    def getBeta(self, val) -> float:
        return self.amafPlays / (self.plays + self.amafPlays + 4 * self.plays * self.amafPlays * pow(val, 2)) 

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
        self.tree = {}
        self.simTime = 6 #in seconds
        self.explorationVal = 2 #TODO: Update this to see variations
        self.bias = 0.1


    def get_move(self,move):
        if len(move) != 0:
            self.board.make_move(move,self.opponent[self.color])
        else:
            self.color = 1
        #moves = self.board.get_all_possible_moves(self.color)
        #index = randint(0,len(moves)-1)
        #inner_index =  randint(0,len(moves[index])-1)
        #move = moves[index][inner_index]
        # val, move = self._minimax(self.board, 4, True, self.color)
        # self.board.make_move(move,self.color)
        # print(val)
        # return move
        tupleBoard = tuple(tuple(sublist) for sublist in self.board.board)
        currState = (tupleBoard, self.opponent[self.color])
        nextMove = self._search(currState, self.board)
        return nextMove
    
    def _search(self, gameState, board: Board) -> Move:
        """
        Returns the best move        
        """
        results = {}
        
        if (gameState in self.tree):
            root = self.tree[gameState]
        else:
            nChildren = len(board.get_all_possible_moves(self.opponent[gameState[1]]))
            boardCopy = deepcopy(board)
            root = Node(gameState, None, nChildren, boardCopy)
        
        root.parent = None

        simCount = 0
        now = time.time()
        while time.time() - now < self.simTime and root.movesUnfinished > 0:
            pickedNode = self._treePolicy(root)
            result, actions = self._simulate(pickedNode.gameState)
            self._backProp(pickedNode, result, actions, player=pickedNode.gameState[1])
            simCount += 1
        
        for child in root.children:
            wins, plays = child.getWinsPlays()
            position = child.move
            results[tuple(position)] = (wins, plays)
        
        return self._bestAction(root)

    
    def _bestAction(self, node: Node) -> Move:
        """
        Returns the best Move by comparing nodes in the Monte Carlo Tree
        """
        mostPlays = float("-inf")
        bestWins = float("-inf")
        bestActions = []
        for child in node.children:
            wins, plays = child.getWinsPlays()

            if (plays > mostPlays):
                mostPlays = plays
                bestActions = [child.move]
                bestWins = wins
            elif plays == mostPlays:
                if wins > bestWins:
                    bestWins = wins
                    bestActions = [child.move]
                elif wins == bestWins:
                    bestActions.append(child.move)

        return random.choice(bestActions)

    
    def _backProp(self, node: Node, delta: float, actions, player) -> None:
        t = 0
        while node.parent != None:
            node.plays += 1
            node.wins += delta

            for u in range(t, len(actions[player])):
                if actions[player][u] not in actions[player][t:u]:
                    node.amafPlays += 1
                    node.amafWins += delta
            
            t += 1
            node = node.parent

        node.plays += 1
        node.wins += delta

        for u in range(t, len(actions[player])):
            if actions[player][u] not in actions[player][t:u]:
                node.amafPlays += 1
                node.amafWins += delta


    def _treePolicy(self, root: Node) -> Node:
        """
        Given a root node, determines which child to visit using UCB.
        """
        currNode = root

        while True and root.movesUnfinished > 0:
            legalMoves = currNode.board.get_all_possible_moves(self.opponent[currNode.gameState[1]])
            if currNode.board.is_win() != 0:
                #Someone has won
                currNode.propagateCompletion()
                return currNode
            elif len(currNode.children) < len(legalMoves):
                unexpanded = [move for move in legalMoves if tuple(move) not in currNode.movesExpanded]
                if len(unexpanded <= 0):
                    raise ValueError("Error from : StudentAI._treePolicy() - Expected unexpanded moves list to have a length greater than 0")
                move = random.choice(unexpanded)

                nextBoardState = deepcopy(currNode.board)
                nextBoardState.make_move(move, self.opponent[currNode.gameState[1]])
                nextState = (nextBoardState.board, self.opponent[currNode.gameState[1]])
                child = Node(nextState, move, len(legalMoves), nextBoardState) #might be wrong NChildren
                currNode.addChild(child)
                self.tree[nextState] = child

                return child
            else:
                currNode = self._bestChild(currNode)
            
            return currNode
        
    
    def _bestChild(self, node: Node) -> Node:
        enemyTurn = (node.gameState[1] != self.color)
        values = {} #dictionary; keys: Nodes, vals: float (representing how good it is)

        for child in node.children:
            wins, plays = child.getWinsPlays()
            aWins, aPlays = child.getAmafWinsPlays()

            if enemyTurn:
                wins = plays - wins
                aWins = aPlays - aWins
            
            _, parentPlays = node.getWinsPlays()
            beta = node.getBeta(self.bias)

            if aPlays > 0:
                values[child] = (1-beta) * (wins / plays) + beta * (aWins/aPlays) \
                    + self.explorationVal * math.sqrt(2 * math.log(parentPlays)/plays)
            else:
                values[child] = (wins/plays) + self.explorationVal * \
                    math.sqrt(2 * math.log(parentPlays)/ plays)
            
        bestChoice = max(values, key=values.get)
        return bestChoice
    

    def _simulate(self, gameNode: Node) -> "float, dict":
        gameState = gameNode.gameState
        currPlayer = self.opponent(gameState[1])
        actions = {gameState[1]: [], self.opponent[gameState[1]]: []}
        boardCopy = deepcopy(gameNode.board)

        while True:
            result = boardCopy.is_win() #0 = no winner , 1 = Black wins, 2 = White wins, -1 = Tie
            if result != 0:
                if result == self.color:
                    return 1, actions
                elif result == self.opponent[self.color]:
                    return 0, actions
                elif result == -1:
                    return .5, actions
                else:
                    raise ValueError("Error from: StudentAI._simulate() - Expected the result to be either: 0, 1, 2, -1")
            
            moves = boardCopy.get_all_possible_moves(currPlayer)
            picked = random.choice(moves)
            actions[currPlayer].append(picked)
            boardCopy.make_move(picked, currPlayer)
            currPlayer = self.opponent[currPlayer]
            




                
        

    # def _minimax(self, board: Board, depth: int, max_player:bool, color: int):
    #     winner = board.is_win("W" if color == 2 else "B")
    #     if depth == 0 or winner != 0:
    #         extra = 5 if winner == color else 0 if winner == 0 else -5
    #         return self._evaluate(board, color) + extra,  None

    #     if max_player:
    #         maxEval = float("-inf")
    #         best_move = None
    #         moves = board.get_all_possible_moves(color)
    #         for outerMove in range(len(moves)):
    #             for innerMove in range(len(moves[outerMove])):
    #                 board.make_move(moves[outerMove][innerMove], color)
    #                 evaluation = self._minimax(board, depth-1, False, 2 if color == 1 else 1)[0]
    #                 maxEval = max(maxEval, evaluation)
    #                 if maxEval == evaluation:
    #                     best_move = moves[outerMove][innerMove]
    #                 board.undo()
    #         return maxEval, best_move
    #     else:
    #         minEval = float("inf")
    #         best_move = None
    #         moves = board.get_all_possible_moves(color)
    #         for outerMove in range(len(moves)):
    #             for innerMove in range(len(moves[outerMove])):
    #                 board.make_move(moves[outerMove][innerMove], color)
    #                 evaluation = self._minimax(board, depth-1, True, 2 if color == 1 else 1)[0]
    #                 minEval = min(minEval, evaluation)
    #                 if minEval == evaluation:
    #                     best_move = moves[outerMove][innerMove]
    #                 board.undo()
    #         return minEval, best_move



    # def _evaluate(self, board:Board, color: int) -> float:
    #     total = 0
    #     kings = {color: 0, color+1: 0}
    #     for row in range(len(board.board)):
    #         for col in range(len(board.board[0])):
    #             if board.board[row][col].is_king:
    #                 if board.board[row][col].color == color:
    #                     kings[color] += 1
    #                 else:
    #                     kings[color+1] += 1

    #     if color == 1:
    #         total += self.board.black_count - self.board.white_count
    #     else:
    #         total += self.board.white_count - self.board.black_count
    #     total += (kings[color] * .5) - (kings[color+1] * .5)

    #     return total
