from copy import deepcopy

from botzone import *
from botzone.online.viewer.nogo import NoGoTextViewer

class NoGoEnv(Env):
    '''
    Description:
        Traditional NoGo with `size`*`size` board. (default = 9)
        
        Decision order: In each turn only one player decide.
        Request: {"x": Number, "y": Number} for each player, {"x": -1, "y": -1}
        for the first turn.
        Response: {"x": Number, "y": Number} for my decision.
        
        Episode Termination:
            The first player who cannot move loses.
        Score:
            2 for winner and 0 for loser.
    '''
    
    metadata = {'render.modes': ['ansi']}
    
    def __init__(self, size = 9):
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
        self.board = b = [[0 for i in range(self.size + 2)] for j in range(self.size + 2)]
        for i in range(self.size + 2):
            b[i][0] = b[i][-1] = b[0][i] = b[-1][i] = -1
        self.last_action = {'x' : -1, 'y' : -1}
        self.display = ['']
        if self.viewer: self.viewer.reset()
    
    def step(self):
        if self.closed:
            raise AlreadyClosed()
        if self.round is None:
            raise ResetNeeded()
        
        cur_player = self.round % 2
        action = deepcopy(self.agents[cur_player].step(self.last_action))
        # check validity of action
        try:
            x = int(action['x']) + 1
            y = int(action['y']) + 1
            assert self._in_board(x, y) and self.board[x][y] == 0
        except:
            # Invalid action
            self.round = None
            self.display.append({'winner' : 1 - cur_player, 'err' : 'Invalid input!'})
            return (2, 0) if cur_player else (0, 2)
        color = cur_player + 1
        self.round += 1
        self.board[x][y] = color
        self.last_action = dict(x = x - 1, y = y - 1)
        if not self._check_valid(x, y):
            self.round = None
            self.display.append({'winner' : 1 - cur_player, 'err' : 'Invalid move!', 'color' : cur_player, 'x' : x - 1, 'y' : y - 1})
            return (2, 0) if cur_player else (0, 2)
        # check episode ends
        if not self._has_valid_move(3 - color):
            self.round = None
            self.display.append({'winner' : cur_player, 'color' : cur_player, 'x' : x - 1, 'y' : y - 1})
            return (0, 2) if cur_player else (2, 0)
        self.display.append({'color' : cur_player, 'x' : x - 1, 'y' : y - 1})
    
    def _in_board(self, x, y):
        return 0 < x <= self.size and 0 < y <= self.size
    
    def _count_liberty(self, x, y):
        color = self.board[x][y]
        group = set()
        liberty = 0
        visited = [[0 for i in range(self.size + 2)] for j in range(self.size + 2)]
        q = [(x, y)]
        visited[x][y] = 1
        while q:
            x, y = q.pop(0)
            group.add((x, y))
            for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                nx = x + dx
                ny = y + dy
                if self.board[nx][ny] == 0 and not visited[nx][ny]:
                    # liberty
                    visited[nx][ny] = 2
                    liberty += 1
                if self.board[nx][ny] == color and not visited[nx][ny]:
                    # in group
                    visited[nx][ny] = 1
                    q.append((nx, ny))
        return liberty, group
    
    def _check_valid(self, x, y):
        color = self.board[x][y]
        # check my liberty
        liberty, group = self._count_liberty(x, y)
        if liberty == 0: return False
        # check capture
        surround = []
        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            nx = x + dx
            ny = y + dy
            if self.board[nx][ny] == 3 - color:
                for liberty, group in surround:
                    if (nx, ny) in group:
                        break
                else:
                    surround.append(self._count_liberty(nx, ny))
                    if surround[-1][0] == 0: return False
        return True
    
    def _has_valid_move(self, color):
        for i in range(1, self.size + 1):
            for j in range(1, self.size + 1):
                if self.board[i][j] == 0:
                    # try it
                    self.board[i][j] = color
                    if self._check_valid(i, j):
                        self.board[i][j] = 0
                        return True
                    self.board[i][j] = 0
        return False
    
    def render(self, mode = 'ansi'):
        if mode == 'ansi':
            if self.viewer is None:
                self.viewer = NoGoTextViewer(size = self.size)
                self.viewer.reset()
            self.viewer.render(self.display)
            self.display = []
        else:
            super(NoGoEnv, self).render(mode)
    
    def close(self):
        self.closed = True
    
    def seed(self, seed = None):
        # No randomness
        pass