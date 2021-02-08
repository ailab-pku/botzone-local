from botzone import *

class TicTacToeEnv(Env):
    '''
    Description:
        Traditional TicTacToe.
        
        Decision order: In each turn only one player decide.
        Request: {"x": Number, "y": Number} for each player, {"x": -1, "y": -1} for the first turn.
        Response: {"x": Number, "y": Number} for my decision.
        
        Episode Termination:
            (1) One player fills three blanks in a line and wins or
            (2) A tie if all blanks are filled without a winner.
        Score:
            2 for winner and 0 for loser, 1 for both in case of a tie.
    '''
    
    metadata = {'render.modes': ['ansi']}
    
    def __init__(self):
        # Initialize configurations, possible viewers and state
        self.agents = None
        self.round = None
        self.closed = False

    @property
    def player_num(self):
        return 2
    
    def reset(self):
        if self.closed:
            raise AlreadyClosed()
        if self.agents is None:
            raise AgentsNeeded()
        # Initialize each agent
        for agent in self.agents:
            agent.reset()
        # Initialize state for new episode
        self.round = 0
        self.board = [[0 for j in range(3)] for i in range(3)]
        self.last_action = {'x' : -1, 'y' : -1}
    
    def step(self):
        if self.closed:
            raise AlreadyClosed()
        if self.round is None:
            raise ResetNeeded()
        
        cur_player = self.round % 2
        action = self.agents[cur_player].step(self.last_action)
        # check validity of action
        try:
            x = action['x']
            y = action['y']
            assert 0 <= x < 3 and 0 <= y < 3
            assert self.board[x][y] == 0
        except:
            # Invalid action
            self.round = None
            return (2, 0) if cur_player else (0, 2)
        self.board[x][y] = cur_player + 1
        self.round += 1
        self.last_action = action
        # check tie
        if self.round == 9:
            self.round = None
            return (1, 1)
        # check winner
        if (self.board[x][0] == self.board[x][1] == self.board[x][2]
            or self.board[0][y] == self.board[1][y] == self.board[2][y]
            or x == y and self.board[0][0] == self.board[1][1] == self.board[2][2]
            or x + y == 2 and self.board[0][2] == self.board[1][1] == self.board[2][0]):
            self.round = None
            return (0, 2) if cur_player else (2, 0)
    
    def render(self, mode = 'ansi'):
        if mode == 'ansi':
            print('State:\n' + '\n'.join([''.join([' OX'[self.board[i][j]] for j in range(3)]) for i in range(3)]))
        else:
            super(TicTacToeEnv, self).render(mode)
    
    def close(self):
        self.closed = True
    
    def seed(self, seed = None):
        # No randomness
        pass
