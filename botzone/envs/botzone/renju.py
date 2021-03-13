from botzone import *
from botzone.online.viewer.renju import RenjuTextViewer

class RenjuEnv(Env):
    '''
    Description:
        Freestyle gomoku, with exchange after 3rd move, with board `size`*`size`. (default = 15)
        
        Decision order: In each turn only one player decide.
        Request: {"x": Number, "y": Number} for each player, {"x": -1, "y": -1}
        for the first turn and for the turn after exchange.
        Response: {"x": Number, "y": Number} for my decision, {"x": -1, "y": -1}
        for exchange.
        
        Episode Termination:
            The one who first forms five-in-a-row wins, or a tie if the board is filled.
        Score:
            2 for winner and 0 for loser, 1 for both in case of a tie.
    '''
    
    metadata = {'render.modes': ['ansi']}
    
    def __init__(self, size = 15):
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
        self.board = b = [[0 for i in range(self.size)] for j in range(self.size)]
        self.last_action = {'x' : -1, 'y' : -1}
        self.display = [None]
        if self.viewer: self.viewer.reset()
    
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
            assert self._in_board(x, y) and self.board[x][y] == 0 or self.round == 3 and x == y == -1
        except:
            # Invalid action
            self.round = None
            self.display.append({'winner' : 1 - cur_player})
            return (2, 0) if cur_player else (0, 2)
        color = cur_player + 1
        self.round += 1
        self.last_action = action
        if x == y == -1:
            # exchange
            for i in range(self.size):
                for j in range(self.size):
                    if self.board[i][j]:
                        self.board[i][j] = 3 - self.board[i][j]
            self.display.append({'msg' : 'exchange'})
        else:
            self.board[x][y] = color
            # check episode ends
            for dx, dy in ((0, 1), (1, 0), (1, 1), (1, -1)):
                cnt = 1
                nx = x + dx
                ny = y + dy
                while self._in_board(nx, ny) and self.board[nx][ny] == color:
                    cnt += 1
                    nx += dx
                    ny += dy
                nx = x - dx
                ny = y - dy
                while self._in_board(nx, ny) and self.board[nx][ny] == color:
                    cnt += 1
                    nx -= dx
                    ny -= dy
                if cnt >= 5:
                    self.round = None
                    self.display.append(dict(color = cur_player, x = x, y = y, winner = cur_player))
                    return (0, 2) if cur_player else (2, 0)
            if self.round == self.size * self.size:
                self.round = None
                self.display.append(dict(color = cur_player, x = x, y = y, winner = 'none'))
                return (1, 1)
            self.display.append(dict(color = cur_player, x = x, y = y))
    
    def _in_board(self, x, y):
        return 0 <= x < self.size and 0 <= y < self.size
    
    def render(self, mode = 'ansi'):
        if mode == 'ansi':
            if self.viewer is None:
                self.viewer = RenjuTextViewer()
                self.viewer.reset()
            self.viewer.render(self.display)
            self.display = []
        else:
            super(RenjuEnv, self).render(mode)
    
    def close(self):
        self.closed = True
    
    def seed(self, seed = None):
        # No randomness
        pass