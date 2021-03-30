from collections import defaultdict
from copy import deepcopy
from random import randint as rand

from botzone import *
from botzone.online.viewer.kingz import KingzTextViewer

class KingzEnv(Env):
    '''
    Description:
        A popular SLG.
        
        Initdata: int=4/6/8 (size of the board)
        
        Request:
            First round: [map0, map1, ..., map99, x, y]
            Other rounds: [x, y, w, d]
        
        Response:
            [x, y, w, d]
        
        Episode Termination:
            Player whose base is conquered loses. When round exceeds 'limit'(default = 400), the total amount of troops is compared.
        Score:
            2 for winner and 0 for loser, 1 for both in case of a draw.
    '''
    
    metadata = {'render.modes': ['ansi']}
    
    def __init__(self, limit = 300):
        # Initialize configurations, possible viewers and state
        self.agents = None
        self.round = None
        self.closed = False
        self.initdata = {}
        self._seed = None
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
        if initdata: initdata = int(initdata)
        else: initdata = 10
        if initdata not in range(4, 12, 2):
            initdata = 10
        self.initdata = self.size = initdata
        if self._seed: random.seed(self._seed)
        # -1 for obstacle, 0 for empty, 1 for castle, 2 for base
        self.info = [[0 for i in range(10)] for i in range(10)]
        # number of troops
        self.board = [[0 for i in range(10)] for i in range(10)]
        # territory
        self.color = [[0 for i in range(10)] for i in range(10)]
        self._generate_map()
        self.display = [dict(
            status = 'opening',
            count = [self.board[i][j] for i in range(10) for j in range(10)],
            type = [self.info[i][j] for i in range(10) for j in range(10)],
            belong = [self.color[i][j] for i in range(10) for j in range(10)]
        )]
        if self.viewer: self.viewer.reset(self.initdata)
    
    def step(self):
        if self.closed:
            raise AlreadyClosed()
        if self.round is None:
            raise ResetNeeded()
        
        if self.round == 0:
            self.requests = [[-1 if self.info[i][j] == -1 else self.board[i][j] for i in range(10) for j in range(10)] for p in range(2)]
            x, y = self.base
            self.requests[0].extend((x, y))
            self.requests[1].extend((9 - x, 9 - y))
        else:
            self.requests = self.last_actions
            self.requests.reverse()
        self.last_actions = actions = [deepcopy(self.agents[p].step(self.requests[p])) for p in range(2)]
        self.round += 1
        # check validity of action
        battle = defaultdict(lambda : [0, 0, 0])
        invalid = [0, 0]
        for p in range(2):
            try:
                x, y, w, d = actions[p] # check format
                w = int(w) # check format
                assert 0 <= x < 10 and 0 <= y < 10 # in range
                assert self.color[x][y] == p + 1 # my territory
                assert 0 <= w < self.board[x][y] # enough troops
                self.board[x][y] -= w
                x += (-1, 1, 0, 0, 0)[d]
                y += (0, 0, -1, 1, 0)[d]
                assert 0 <= x < 10 and 0 <= y < 10 # in range
                assert self.info[x][y] != -1 # not obstacle
                battle[(x, y)][p + 1] += w
            except:
                invalid[p] = 1
        if invalid[0] or invalid[1]:
            self.round = None
            winner = 3 - invalid[0] - invalid[1] * 2
            self.display.append(dict(
                status = 'end',
                winner = winner,
                err = ('BOTH INVALID', 'PLAYER 1 INVALID', 'PLAYER 2 INVALID')[winner]
            ))
            return ((1, 1), (2, 0), (0, 2))[winner]
        # process move
        for x, y in battle:
            battle[(x, y)][self.color[x][y]] += self.board[x][y]
            self.board[x][y] = 0
        for x, y in battle:
            neutral, red, blue = self._battle(*battle[(x, y)])
            self.board[x][y] = neutral + red + blue
            if neutral: self.color[x][y] = 0
            elif red: self.color[x][y] = 1
            elif blue: self.color[x][y] = 2
        for i in range(10):
            for j in range(10):
                if self.color[i][j] == 0: continue
                if self.info[i][j] == 2: self.board[i][j] += 2
                if self.info[i][j] == 1: self.board[i][j] += 1
                if self.info[i][j] == 0 and self.round % 8 == 0: self.board[i][j] += 1
        display = dict(
            status = 'combat',
            #count = [self.board[i][j] for i in range(10) for j in range(10)],
            #type = [self.info[i][j] for i in range(10) for j in range(10)],
            #belong = [self.color[i][j] for i in range(10) for j in range(10)],
            operation = deepcopy(self.last_actions)
        )
        # check episode ends
        x, y = self.base
        if self.color[x][y] == 2 or self.color[9 - x][9 - y] == 1:
            if self.color[x][y] == 2:
                if self.color[9 - x][9 - y] == 1:
                    winner = 0
                else:
                    winner = 2
            else:
                winner = 1
            self.round = None
            display['status'] = 'finish'
            display['winner'] = winner
            display['err'] = ('BOTH KILL', 'PLAYER 1 KILL', 'PLAYER 2 KILL')[winner]
            self.display.append(display)
            return ((1, 1), (2, 0), (0, 2))[winner]
        if self.round == self.limit:
            t = 0
            for i in range(10):
                for j in range(10):
                    t += self.board[i][j] * ((self.color[i][j] == 1) - (self.color[i][j] == 2))
            if t > 0: winner = 1
            elif t < 0: winner = 2
            else: winner = 0
            self.round = None
            display['status'] = 'finish'
            display['winner'] = winner
            display['err'] = ('DRAW', 'PLAYER 1 WIN', 'PLAYER 2 WIN')[winner]
            self.display.append(display)
            return ((1, 1), (2, 0), (0, 2))[winner]
        self.display.append(display)
    
    def render(self, mode = 'ansi'):
        if mode == 'ansi':
            if self.viewer is None:
                self.viewer = KingzTextViewer()
                self.viewer.reset(self.initdata)
            self.viewer.render(self.display)
            self.display = []
        else:
            super(KingzEnv, self).render(mode)
    
    def close(self):
        self.closed = True
    
    def _generate_map(self):
        info = self.info
        b = self.board
        # This is a copy of original implementation on botzone.org
        while True:
            for i in range(0, 5):
                for j in range(0, 10):
                    t = 6
                    if i and j and info[i - 1][j - 1] == -1: t -= 2
                    if i and j != 9 and info[i - 1][j + 1] == -1: t -= 2
                    if i and info[i - 1][j] == -1: t += 2
                    if j and info[i][j - 1] == -1: t += 2
                    info[i][j] = info[9 - i][9 - j] = 0 if rand(0, t - 1) else -1
            if self.size == 8:
                for i in range(10):
                    info[i][0] = info[i][-1] = info[0][i] = info[-1][i] = -1
            if self.size == 6:
                for i in range(10):
                    info[i][1] = info[i][-2] = info[1][i] = info[-2][i] = -1
            if self.size == 4:
                for i in range(10):
                    info[i][2] = info[i][-3] = info[2][i] = info[-3][i] = -1
            x = rand(0, 9)
            y = rand(0, 9)
            if x >= 5:
                x = 9 - x
                y = 9 - y
            self._dfs(x, y)
            if info[x][y] == 1 and info[9 - x][9 - y] == 1: break
        self.base = x, y
        info[x][y] = info[9 - x][9 - y] = 2
        b[x][y] = b[9 - x][9 - y] = 10
        self.color[x][y] = 1
        self.color[9 - x][9 - y] = 2
        for i in range(0, 5):
            for j in range(0, 10):
                if info[i][j] == 1:
                    if rand(0, 9) == 0:
                        b[i][j] = b[9 - i][9 - j] = rand(0, 24) + rand(0, 24) + rand(0, 24) + rand(0, 24) + 5
                    else:
                        info[i][j] = info[9 - i][9 - j] = 0
    
    def _dfs(self, x, y):
        if x < 0 or x >= 10 or y < 0 or y >= 10 or self.info[x][y] != 0: return
        self.info[x][y] = 1
        self._dfs(x - 1, y)
        self._dfs(x + 1, y)
        self._dfs(x, y - 1)
        self._dfs(x, y + 1)
    
    def _battle(self, neutral, red, blue):
        t = min(red, blue)
        red -= t
        blue -= t
        if red > 0:
            t = min(red, neutral)
            red -= t
            neutral -= t
        else:
            t = min(blue, neutral)
            blue -= t
            neutral -= t
        return neutral, red, blue