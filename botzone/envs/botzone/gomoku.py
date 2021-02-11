from botzone import *
from botzone.online.viewer.gomoku import GomokuTextViewer

class GomokuEnv(Env):
    '''
    Description:
        Freestyle gomoku, with no restricted move.
        
        Decision order: In each turn only one player decide.
        Request: {"x": Number, "y": Number} for each player, {"x": -1, "y": -1}
        for the first turn.
        Response: {"x": Number, "y": Number} for my decision.
        
        Episode Termination:
            The one who first forms five-in-a-row wins, or a tie if the board is filled.
        Score:
            2 for winner and 0 for loser, 1 for both in case of a tie.
    '''
    
    metadata = {'render.modes': ['ansi']}
    
    def __init__(self):
        # Initialize configurations, possible viewers and state
        self.agents = None
        self.round = None
        self.closed = False
        self.display = []
        self.viewer = None
    
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
        self.board = b = [[0 for i in range(15)] for j in range(15)]
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
            assert self._in_board(x, y)
        except:
            # Invalid action
            self.round = None
            self.display.append({'winner' : 1 - cur_player})
            return (2, 0) if cur_player else (0, 2)
        color = cur_player + 1
        self.board[x][y] = color
        self.round += 1
        self.last_action = action
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
                self.display.append(dict(color = cur_player, x = x, y = y, winner = cur_player))
                return (0, 2) if cur_player else (2, 0)
        if self.round == 15 * 15:
            self.display.append(dict(color = cur_player, x = x, y = y, winner = 'none'))
            return (1, 1)
        self.display.append(dict(color = cur_player, x = x, y = y))
    
    def _in_board(self, x, y):
        return 0 <= x < 15 and 0 <= y < 15
    
    def render(self, mode = 'ansi'):
        if mode == 'ansi':
            if self.viewer is None:
                self.viewer = GomokuTextViewer()
                self.viewer.reset()
            self.viewer.render(self.display)
            self.display = []
        else:
            super(GomokuEnv, self).render(mode)
    
    def close(self):
        self.closed = True
    
    def seed(self, seed = None):
        # No randomness
        pass