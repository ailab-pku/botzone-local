import random

from botzone import *
from botzone.online.viewer.minesweeper import MineSweeperTextViewer

class MineSweeperEnv(Env):
    '''
    Description:
        Traditional minesweeper game.
        
        Initdata: {
            "width": Number of [11, 80], default 30
            "height": Number of [11, 40], default 20
            "minecount": Number of [11, 100], default 80
            "seed": random seed
        }
        
        Request: {
            "width": Number,
            "height": Number,
            "minecount": Number,
            "changed": [{
                "row": Number,
                "col": Number,
                "val": Number   # 9 for mine
            }]
        }
        Response: {"row": Number, "col": Number}
        
        Episode Termination:
            When the number of mines left equals to the number of unopened cells.
        Score:
            The percentage of mines left.
    '''
    
    metadata = {'render.modes': ['ansi']}
    
    def __init__(self):
        # Initialize configurations, possible viewers and state
        self.agents = None
        self.round = None
        self.closed = False
        self.initdata = {}
        self._seed = None
        self.display = []
        self.viewer = None
    
    @property
    def player_num(self):
        return 1
    
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
        if not initdata: initdata = {}
        self.width = int(initdata.get('width', 30))
        if not 10 < self.width <= 80:
            self.width = 30
        self.height = int(initdata.get('height', 20))
        if not 10 < self.height <= 40:
            self.height = 20
        self.minecount = int(initdata.get('minecount', 80))
        if not 10 < self.minecount <= 100:
            self.minecount = 80
        if 'seed' in initdata:
            self.seed(initdata['seed'])
        self.initdata = dict(width = self.width, height = self.height, minecount = self.minecount)
        if self._seed: random.seed(self._seed)
        mines = [(x, y) for x in range(self.height) for y in range(self.width)]
        random.shuffle(mines)
        mines = mines[ : self.minecount]
        self.board = [[0 for i in range(self.width)] for j in range(self.height)]
        for x, y in mines:
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    nx = x + dx
                    ny = y + dy
                    if self._in_board(nx, ny):
                        self.board[nx][ny] += 1
        for x, y in mines:
            self.board[x][y] = 9
        self.reveal = [[False for i in range(self.width)] for j in range(self.height)]
        self.cellleft = self.width * self.height
        self.mineleft = self.minecount
        self.status = None
        self.display = [{'status' : None}]
        if self.viewer: self.viewer.reset(self.initdata)
    
    def step(self):
        if self.closed:
            raise AlreadyClosed()
        if self.round is None:
            raise ResetNeeded()
        
        action = self.agents[0].step(dict(
            width = self.width,
            height = self.height,
            minecount = self.minecount,
            changed = self.status
        ))
        # check validity of action
        try:
            row = action['row']
            col = action['col']
            assert not self.reveal[row][col]
        except:
            # Invalid action
            self.round = None
            self.display.append(dict(msg = 'INVALIDMOVE'))
            return (0, )
        # process move
        self.status = []
        q = [(row, col)]
        self.reveal[row][col] = True
        while q:
            x, y = q.pop(0)
            val = self.board[x][y]
            self.status.append(dict(row = x, col = y, val = val))
            if val == 9: self.mineleft -= 1
            if val == 0:
                for dx in range(-1, 2):
                    for dy in range(-1, 2):
                        nx = x + dx
                        ny = y + dy
                        if self._in_board(nx, ny) and not self.reveal[nx][ny]:
                            q.append((nx, ny))
                            self.reveal[nx][ny] = True
        self.cellleft -= len(self.status)
        self.round += 1
        # check episode ends
        if self.cellleft == self.mineleft:
            self.round = None
            self.display.append(dict(msg = 'FINISH', status = self.status))
            return (self.mineleft / self.minecount * 100, )
        self.display.append(dict(status = self.status))
    
    def render(self, mode = 'ansi'):
        if mode == 'ansi':
            if self.viewer is None:
                self.viewer = MineSweeperTextViewer()
                self.viewer.reset(self.initdata)
            self.viewer.render(self.display)
            self.display = []
        else:
            super(MineSweeperEnv, self).render(mode)
    
    def close(self):
        self.closed = True
    
    def _in_board(self, x, y):
        return 0 <= x < self.height and 0 <= y < self.width