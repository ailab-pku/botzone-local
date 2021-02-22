from copy import deepcopy
import random

from botzone import *
from botzone.online.viewer.snake import SnakeTextViewer

class SnakeEnv(Env):
    '''
    Description:
        Two-player Snake game.
        Rule: https://wiki.botzone.org.cn/index.php?title=Snake
        
        Decision order: Two players act simutaneously in each turn.
        Initdata: {
            width: Number of 10~12
            height: Number of 10~16
            "0": {x: Number, y: Number} # initial pos
            "1": {x: Number, y: Number} # initial pos
            obstacle: list of {x: Number, y: Number}
        }
        Request:
            First: {width, height, x, y, obstacle}
            Others: {direction: 0..3} of the other player in the last turn
        Response:
            {direction: 0..3} for (-1,0), (0,1), (1,0), (0,-1)
        
        Episode Termination:
            The first player to give an invalid move loses, or a tie if both.
        Score:
            2 for winner and 0 for loser, 1 for both in case of a tie.
    '''
    
    metadata = {'render.modes': ['ansi']}
    
    def __init__(self):
        self.agents = None
        self.round = None
        self.closed = False
        self.initdata = {}
        self._seed = None
        self.display = []
        self.viewer = None
        self.dx = [-1, 0, 1, 0]
        self.dy = [0, 1, 0, -1]
    
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
        if not initdata: initdata = {}
        if 'seed' in initdata:
            self.seed(initdata['seed'])
        if self._seed:
            random.seed(self._seed)
        self.width = initdata.get('width', random.randint(10, 12))
        self.height = initdata.get('height', random.randint(10, 16))
        self.body = [[(1, 1)], [(self.height, self.width)]]
        for i in range(2):
            if str(i) in initdata:
                self.body[i] = [(initdata[str(i)]['x'], initdata[str(i)]['y'])]
        if 'obstacle' in initdata:
            obs = [(d['x'], d['y']) for d in initdata['obstacle']]
        else:
            obs = [(x, y) for x in range(1, self.height + 1) for y in range(1, self.width + 1)]
            obs = obs[1 : (len(obs) + 1) // 2]
            random.shuffle(obs)
            obs = obs[: self.height * self.width // 20]
            obs.extend([(self.height + 1 - x, self.width + 1 - y) for x, y in obs])
        self.board = [[0 for i in range(self.width + 2)] for j in range(self.height + 2)]
        for i in range(self.width + 2): self.board[0][i] = self.board[-1][i] = -2
        for j in range(self.height + 2): self.board[j][0] = self.board[j][-1] = -2
        for x, y in obs:
            self.board[x][y] = -1
        for i in range(2):
            for x, y in self.body[i]:
                self.board[x][y] = i + 1
        self.initdata = {
            'width' : self.width,
            'height' : self.height,
            '0' : {'x' : self.body[0][0][0], 'y' : self.body[0][0][1]},
            '1' : {'x' : self.body[1][0][0], 'y' : self.body[1][0][1]},
            'obstacle' : [{'x' : x, 'y' : y} for x, y in obs]
        }
        self.display = [self.initdata]
        if self.viewer: self.viewer.reset(self.initdata)
        self.last_actions = (0, 0)
    
    def step(self):
        if self.closed:
            raise AlreadyClosed()
        if self.round is None:
            raise ResetNeeded()
        # provide request
        if self.round == 0:
            requests = [{
                'width' : self.width,
                'height' : self.height,
                'obstacle' : self.initdata['obstacle'],
                'x' : self.initdata[str(i)]['x'],
                'y' : self.initdata[str(i)]['y']
            } for i in range(2)]
        else:
            requests = [{'direction' : d} for d in reversed(self.last_actions)]
        # deep copy for safety
        actions = [deepcopy(self.agents[i].step(deepcopy(requests[i]))) for i in range(2)]
        self.last_actions = []
        grow = self.round < 10 or self.round % 3 == 0
        self.round += 1
        # check validity
        for i in range(2):
            try:
                d = actions[i].get('direction', None)
                assert isinstance(d, int) and 0 <= d < 4
            except:
                score = ((0, 2), (2, 0))[i]
                self.display.append({'winner' : 2 - i, 'grow' : 'true' if grow else 'false'})
                self.round = None
                return score
            self.last_actions.append(d)
            x, y = self.body[i][-1]
            x += self.dx[d]
            y += self.dy[d]
            self.body[i].append((x, y))
            if not grow:
                x, y = self.body[i].pop(0)
                self.board[x][y] = 0
        # move
        e = 0
        if self.body[0][-1] == self.body[1][-1]: e = 3
        else:
            for i in range(2):
                x, y = self.body[i][-1]
                if self.board[x][y] == 0:
                    self.board[x][y] = i + 1
                else:
                    e += i + 1
        if e:
            score = ((0, 2), (2, 0), (1, 1))[e - 1]
            d = {'grow' : 'true' if grow else 'false',
                '0' : self.last_actions[0],
                '1' : self.last_actions[1]
            }
            if e < 3: d['winner'] = e - 1
            self.display.append(d)
            self.round = None
            return score
        self.display.append({
            'grow' : 'true' if grow else 'false',
            '0' : self.last_actions[0],
            '1' : self.last_actions[1]
        })
    
    def render(self, mode = 'ansi'):
        if mode == 'ansi':
            if self.viewer is None:
                self.viewer = SnakeTextViewer()
                self.viewer.reset(self.initdata)
            self.viewer.render(self.display)
            self.display = []
        else:
            super(SnakeEnv, self).render(mode)
    
    def close(self):
        self.closed = True