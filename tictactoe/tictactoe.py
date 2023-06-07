"""
Tic Tac Toe Player
"""

import math
from copy import deepcopy
from random import randint

X = "X"
O = "O"
EMPTY = None
#NEXT_PLAYER = ""


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    #raise NotImplementedError
    X_count=0
    O_count=0
    for row in range(3):
        for col in range(3):
            if board[row][col] == X:
                X_count += 1
            if board[row][col] == O:
                O_count += 1
    if X_count == O_count:
        return X
    if X_count > O_count:
        return O
    
def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    #raise NotImplementedError    
    actions_possible = []

    for i in range(3):
        for j in range(3):
            if board[i][j] == EMPTY:
                actions_possible.append((i,j))
    
    return actions_possible

def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    #raise NotImplementedError
    if action not in actions(board):
        raise UserWarning("Illegal Move")
    new_board = deepcopy(board)
    new_board[action[0]][action[1]] = player(new_board)
    return new_board

def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    #raise NotImplementedError
    winner = False
    winner_name = EMPTY
    
    #Row checking
    for i in range(3):
        for j in range(3):
            if board[i][j] is not EMPTY and board[i][0] is board[i][j]:
                winner = True
            else:
                winner = False
                break
        if winner:
            winner_name = board[i][0]
            break
    
    #Col checking
    if not winner:
        for i in range(3):
            for j in range(3):
                if board[j][i] is not EMPTY and board[0][i] is board[j][i]:
                    winner = True
                else:
                    winner = False
                    break
            if winner:
                winner_name = board[0][i]
                break
    
    #Diag checking
    if not winner:
        for i in range(3):
            if board[i][i] is not EMPTY and board[0][0] is board[i][i]:
                winner = True
            else:
                winner = False
                break
        if winner:
            winner_name = board[0][0]

    #Diag opposite checking
    if not winner:
        for i in range(3):
            if board[i][2-i] is not EMPTY and board[0][2] is board[i][2-i]:
                winner = True
            else:
                winner = False
                break
        if winner:
            winner_name = board[0][2]

    return winner_name

def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    #raise NotImplementedError
    
    #Checking for winner
    if winner(board) is not EMPTY:
        return True
    #Checking for possible moves if there is no winner
    if len(actions(board)) is 0:
        return True
    
    return False


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    #raise NotImplementedError
    
    winner_name = winner(board)

    if winner_name is X:
        return 1
    elif winner_name is O :
        return -1
    else:
        return 0

def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    #raise NotImplementedError
    board_player = player(board)
    tie_action = []
    possible_moves = actions(board)
    
    #In case AI opens the board, this will make the first move faster.
    if len(possible_moves) is 9:
        return possible_moves[randint(0,8)]
    if terminal(board):
        return None

    for move in possible_moves:
        new_board = result(board, move)
        estimated_board_value = get_board_value(new_board)
        #input("action:")
        #print(f"{estimated_board_value} for action {action}:")
        if board_player is X and estimated_board_value is 1:
            return move
        if board_player is O and estimated_board_value is -1:
            return move
        if estimated_board_value is 0:
            tie_action.append(move)
    
    return tie_action[randint(0,len(tie_action)-1)]

def print_board(board):
    """
    Print the board for debugging
    """

    for i in range(3):
        for j in range(3):
            if board[i][j] is EMPTY:
                print(" ", end=',')
            else:
                print(f"{board[i][j]}", end=',')
        print("\n")

def get_board_value(board):
    """
    Using MiniMax algorithm, estimate the best possible value of the given unfinished board.
    """
    if terminal(board):
        return utility(board)
    else:
        board_player = player(board)
        all_actions = actions(board)
        maxValue = -2
        minValue = 2
        for action in all_actions:
            new_board = result(board, action)
            estimated_value = get_board_value(new_board)
            
            if board_player is X:
                maxValue = max(maxValue, estimated_value)
                if maxValue is 1:
                    break
            if board_player is O:
                minValue = min(minValue, estimated_value)
                if minValue is -1:
                    break
        
        if board_player is X:
            return maxValue
        if board_player is O:
            return minValue

            



        
