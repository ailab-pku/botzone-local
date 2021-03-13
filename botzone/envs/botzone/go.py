from copy import deepcopy

from botzone import *
from botzone.online.viewer.go import GoTextViewer

class GoEnv(Env):
    '''
    Description:
        Traditional Go with:
            `size`*`size` board, (default = 8)
            komi = `komi`, (default = 0.75)
            area scoring rule,
            positional superko rule.
        
        Decision order: In each turn only one player decide.
        Request: {"x": Number, "y": Number} for each player, {"x": -2, "y": -2}
        for the first turn.
        Response: {"x": Number, "y": Number} for my decision, {"x": -1, "y": -1}
        for pass.
        
        Episode Termination:
            When both players pass.
        Score:
            2 for winner and 0 for loser.
    '''
    
    metadata = {'render.modes': ['ansi']}
    
    def __init__(self, size = 8, komi = 0.75):
        # Initialize configurations, possible viewers and state
        self.agents = None
        self.round = None
        self.closed = False
        self.display = []
        self.viewer = None
        self.size = size
        self.komi = komi
    
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
        self.history = set()
        self.history.add(self._hash())
        self.last_action = {'x' : -2, 'y' : -2}
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
            x = int(action['x'])
            y = int(action['y'])
            assert x == y == -1 or self._in_board(x, y) and self.board[x][y] == 0
        except:
            # Invalid action
            self.round = None
            self.display.append({'winner' : 1 - cur_player, 'error_info' : 'Invalid input!'})
            return (2, 0) if cur_player else (0, 2)
        color = cur_player + 1
        self.round += 1
        if x == y == -1:
            # pass
            if self.last_action['x'] == -1:
                # episode ends
                ax, ay = self._count_area()
                winner = 0 if ax - ay > self.komi else 1
                self.round = None
                self.display.append({'winner' : winner, 'stones' : {'0' : ax, '1' : ay, 'komi' : self.komi}})
                return (0, 2) if winner else (2, 0)
            else:
                self.last_action = dict(x = x, y = y)
                self.display.append('')
        else:
            self.board[x][y] = color
            # check remove
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
            remove = []
            for liberty, group in surround:
                if liberty == 0:
                    for nx, ny in group:
                        self.board[nx][ny] = 0
                        remove.append(dict(x = nx, y = ny))
            # check my liberty
            liberty, group = self._count_liberty(x, y)
            if liberty == 0:
                # Invalid action
                self.round = None
                self.display.append({'winner' : 1 - cur_player, 'error_info' : 'Suicide forbidden!', 'color' : cur_player, 'x' : x, 'y' : y})
                return (2, 0) if cur_player else (0, 2)
            # check superko
            h = self._hash()
            if h in self.history:
                # Invalid action
                self.round = None
                self.display.append({'winner' : 1 - cur_player, 'error_info' : 'Superko violation!', 'color' : cur_player, 'x' : x, 'y' : y})
                return (2, 0) if cur_player else (0, 2)
            self.history.add(h)
            self.last_action = dict(x = x, y = y)
            self.display.append(dict(color = cur_player, x = x, y = y, remove = remove))
    
    def _hash(self):
        h = 0
        for i in range(1, self.size + 1):
            for j in range(1, self.size + 1):
                h = h * 3 + self.board[i][j]
        return hash(h)
    
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
    
    def _count_area(self):
        area = [0, 0]
        visited = [[0 for i in range(self.size + 2)] for j in range(self.size + 2)]
        for i in range(1, self.size + 1):
            for j in range(1, self.size + 1):
                if self.board[i][j]:
                    # stone
                    area[self.board[i][j] - 1] += 1
                    continue
                if visited[i][j]: continue
                # new connected area
                reach = [0, 0]
                cnt = 0
                q = [(i, j)]
                visited[i][j] = 1
                while q:
                    x, y = q.pop(0)
                    cnt += 1
                    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                        nx = x + dx
                        ny = y + dy
                        if self.board[nx][ny] == 0 and not visited[nx][ny]:
                            visited[nx][ny] = 1
                            q.append((nx, ny))
                        if self.board[nx][ny] > 0:
                            reach[self.board[nx][ny] - 1] = 1
                if not(reach[0] ^ reach[1]): reach = [0.5, 0.5]
                area[0] += reach[0] * cnt
                area[1] += reach[1] * cnt
        return area
    
    def render(self, mode = 'ansi'):
        if mode == 'ansi':
            if self.viewer is None:
                self.viewer = GoTextViewer(size = self.size)
                self.viewer.reset()
            self.viewer.render(self.display)
            self.display = []
        else:
            super(GoEnv, self).render(mode)
    
    def close(self):
        self.closed = True
    
    def seed(self, seed = None):
        # No randomness
        pass