import random

from botzone import *

class TicTacToeAgent(Agent):
    '''
    Random strategy.
    '''
    
    def __init__(self):
        self.board = None
        self.closed = False
    
    def reset(self):
        if self.closed:
            raise AlreadyClosed()
        self.board = [[0 for j in range(3)] for i in range(3)]
        self.role = 2
    
    def step(self, request):
        if self.closed:
            raise AlreadyClosed()
        if self.board is None:
            raise ResetNeeded()
        x = request['x']
        y = request['y']
        if x < 0 and y < 0:
            self.role = 1
        else:
            self.board[x][y] = 1
        l = [i for i in range(9) if not self.board[i // 3][i % 3]]
        pos = random.choice(l)
        x = pos // 3
        y = pos % 3
        self.board[x][y] = 1
        return {'x' : x, 'y' : y}
    
    def close(self):
        self.closed = True