from copy import deepcopy

from botzone import *
from botzone.online.viewer.amazons import AmazonsTextViewer

class AmazonsEnv(Env):
    '''
    Description:
        Traditional Amazons game with `size`*`size` board. (default = 8)
        
        Decision order: In each turn only one player decide.
        Request: {x0, y0, x1, y1, x2, y2} for each player, -1 for all for the
        first turn.
        Response: {x0, y0, x1, y1, x2, y2} for my decision.
        
        Episode Termination:
            The first player who is unable to move loses.
        Score:
            2 for winner and 0 for loser.
    '''
    
    metadata = {'render.modes': ['ansi']}
    
    def __init__(self, size = 8):
        # Initialize configurations, possible viewers and state
        self.agents = None
        self.round = None
        self.closed = False
        self.display = []
        self.viewer = None
        self.size = size
    
    @property
    def player_num(self):
        return 2
    
    def reset(self, initdata = None):
        if self.closed:
            raise AlreadyClosed()
        if self.agents is None:
            raise AgentsNeeded()
        # Initialize each agent
        for agent in self.agents:
            agent.reset()
        # Initialize state for new episode
        self.round = 0
        self.board = b = [[0 for j in range(self.size)] for i in range(self.size)]
        p = (self.size + 2) // 3
        b[0][p - 1] = b[p - 1][0] = b[-p][0] = b[-1][p - 1] = 1 # 1 for black
        b[0][-p] = b[p - 1][-1] = b[-p][-1] = b[-1][-p] = 2 # 2 for white
        self.last_action = {
            'x0' : -1, 'y0' : -1
            , 'x1' : -1, 'y1' : -1
            , 'x2' : -1, 'y2' : -1
        }
        if self.viewer: self.viewer.reset()
        self.valid_move = v = self._valid_move()
        self.display = [dict(blackCount = len(v[0]), whiteCount = len(v[1]))]
    
    def step(self):
        if self.closed:
            raise AlreadyClosed()
        if self.round is None:
            raise ResetNeeded()
        
        cur_player = self.round % 2
        action = deepcopy(self.agents[cur_player].step(self.last_action))
        # check validity of action
        try:
            x0 = action['x0']
            y0 = action['y0']
            x1 = action['x1']
            y1 = action['y1']
            x2 = action['x2']
            y2 = action['y2']
            assert (x0, y0, x1, y1, x2, y2) in self.valid_move[cur_player]
        except:
            # Invalid action
            self.round = None
            self.display.append(dict(
                winner = 1 - cur_player,
                blackCount = len(self.valid_move[0]),
                whiteCount = len(self.valid_move[1])
            ))
            return (2, 0) if cur_player else (0, 2)
        color = cur_player + 1
        self.board[x0][y0] = 0
        self.board[x1][y1] = color
        self.board[x2][y2] = -1
        self.round += 1
        self.last_action = action
        # check episode ends
        self.valid_move = v = self._valid_move()
        if not v[1 - cur_player]:
            self.round = None
            self.display.append(dict(
                winner = cur_player,
                blackCount = len(v[0]),
                whiteCount = len(v[1]),
                x0 = x0, y0 = y0,
                x1 = x1, y1 = y1,
                x2 = x2, y2 = y2
            ))
            return (0, 2) if cur_player else (2, 0)
        self.display.append(dict(
            blackCount = len(v[0]),
            whiteCount = len(v[1]),
            x0 = x0, y0 = y0,
            x1 = x1, y1 = y1,
            x2 = x2, y2 = y2
        ))
    
    def render(self, mode = 'ansi'):
        if mode == 'ansi':
            if self.viewer is None:
                self.viewer = AmazonsTextViewer(size = self.size)
                self.viewer.reset()
            self.viewer.render(self.display)
            self.display = []
        else:
            super(AmazonsEnv, self).render(mode)
    
    def close(self):
        self.closed = True
    
    def seed(self, seed = None):
        # No randomness
        pass

    def _valid_move(self):
        valid = [[], []]
        b = self.board
        for x0 in range(self.size):
            for y0 in range(self.size):
                if b[x0][y0] > 0:
                    for dx1 in range(-1, 2):
                        for dy1 in range(-1, 2):
                            if dx1 or dy1:
                                x1 = x0 + dx1
                                y1 = y0 + dy1
                                while self._in_board(x1, y1) and b[x1][y1] == 0:
                                    for dx2 in range(-1, 2):
                                        for dy2 in range(-1, 2):
                                            if dx2 or dy2:
                                                x2 = x1 + dx2
                                                y2 = y1 + dy2
                                                while self._in_board(x2, y2) and (b[x2][y2] == 0 or x2 == x0 and y2 == y0):
                                                    valid[b[x0][y0] - 1].append((x0, y0, x1, y1, x2, y2))
                                                    x2 = x2 + dx2
                                                    y2 = y2 + dy2
                                    x1 = x1 + dx1
                                    y1 = y1 + dy1
        return valid
    
    def _in_board(self, x, y):
        return 0 <= x < self.size and 0 <= y < self.size