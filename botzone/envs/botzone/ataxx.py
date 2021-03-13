from botzone import *
from botzone.online.viewer.ataxx import AtaxxTextViewer

class AtaxxEnv(Env):
    '''
    Description:
        Traditional ataxx with empty board.
        
        Decision order: In each turn only one player decide.
        Request: {"x": Number, "y": Number} for each player, {"x": -1, "y": -1}
        for the first turn.
        Response: {"x": Number, "y": Number} for my decision.
        
        Episode Termination:
            (1) When one player has no position to move. All empty positions are
            considered to be the opponent's. The player with more stones on the
            board wins.
            (2) When the game exceeds `limit=400` rounds. The player with more stones on
            the board wins.
        Score:
            2 for winner and 0 for loser.
    '''
    
    metadata = {'render.modes': ['ansi']}
    
    def __init__(self, limit = 400):
        # Initialize configurations, possible viewers and state
        self.agents = None
        self.round = None
        self.closed = False
        self.display = []
        self.viewer = None
        self.limit = limit
    
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
        self.board = b = [[0 for i in range(7)] for j in range(7)]
        b[0][0] = b[-1][-1] = 1 # 1 for black
        b[0][-1] = b[-1][0] = 2 # 2 for white
        self.last_action = {'x0' : -1, 'y0' : -1, 'x1' : -1, 'y1' : -1}
        self.display = [None]
        if self.viewer: self.viewer.reset()
    
    def step(self):
        if self.closed:
            raise AlreadyClosed()
        if self.round is None:
            raise ResetNeeded()
        
        cur_player = self.round % 2
        color = cur_player + 1
        action = self.agents[cur_player].step(self.last_action)
        # check validity of action
        try:
            x0 = int(action['x0'])
            y0 = int(action['y0'])
            x1 = int(action['x1'])
            y1 = int(action['y1'])
            assert self._in_board(x0, y0) and self._in_board(x1, y1)
            assert self.board[x0][y0] == color
            assert x0 != x1 or y0 != y1
            assert abs(x0 - x1) <= 2 and abs(y0 - y1) <= 2
        except:
            # Invalid action
            self.round = None
            self.display.append({'winner' : 1 - cur_player})
            return (2, 0) if cur_player else (0, 2)
        if abs(x0 - x1) == 2 or abs(y0 - y1) == 2:
            self.board[x0][y0] = 0
        self.board[x1][y1] = color
        for i in range(-1, 2):
            for j in range(-1, 2):
                nx = x1 + i
                ny = y1 + j
                if self._in_board(nx, ny) and self.board[nx][ny] == 3 - color:
                    self.board[nx][ny] = color
        self.round += 1
        self.last_action = dict(x0 = x0, y0 = y0, x1 = x1, y1 = y1)
        # check episode ends
        if not self._has_valid_move(3 - color):
            winner = cur_player
            if sum(x.count(3 - color) for x in self.board) > 24:
                winner = 1 - winner
            self.display.append(dict(x0 = x0, y0 = y0, x1 = x1, y1 = y1, winner = winner))
            self.round = None
            return ((2, 0), (0, 2))[winner]
        if self.round > self.limit:
            winner = cur_player
            if sum(x.count(3 - color) for x in self.board) > sum(x.count(color) for x in self.board):
                winner = 1 - winner
            self.display.append(dict(x0 = x0, y0 = y0, x1 = x1, y1 = y1, winner = winner))
            self.round = None
            return ((2, 0), (0, 2))[winner]
        self.display.append(self.last_action)
    
    def render(self, mode = 'ansi'):
        if mode == 'ansi':
            if self.viewer is None:
                self.viewer = AtaxxTextViewer()
                self.viewer.reset()
            self.viewer.render(self.display)
            self.display = []
        else:
            super(AtaxxEnv, self).render(mode)
    
    def close(self):
        self.closed = True
    
    def seed(self, seed = None):
        # No randomness
        pass
    
    def _in_board(self, x, y):
        return 0 <= x < 7 and 0 <= y < 7
    
    def _has_valid_move(self, color):
        for i in range(7):
            for j in range(7):
                if self.board[i][j] == color:
                    for dx in range(-2, 3):
                        for dy in range(-2, 3):
                            if self._in_board(i + dx, j + dy) and self.board[i + dx][j + dy] == 0:
                                return True
        return False