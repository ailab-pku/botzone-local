from botzone import *
from botzone.online.viewer.reversi import ReversiTextViewer

class ReversiEnv(Env):
    '''
    Description:
        Traditional reversi game.
        
        Decision order: In each turn only one player decide.
        Request: {"x": Number, "y": Number} for each player, {"x": -1, "y": -1}
        for the first turn.
        Response: {"x": Number, "y": Number} for my decision, {"x": -1, "y": -1}
        for skipping.
        
        Episode Termination:
            When both players have no position to move. The player with more
            stones on the board wins.
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
        self.board = b = [[0 for i in range(8)] for j in range(8)]
        b[3][3] = b[4][4] = 2 # 2 for white
        b[3][4] = b[4][3] = 1 # 1 for black
        self.last_action = {'x' : -1, 'y' : -1}
        self.display = [None]
        if self.viewer: self.viewer.reset()
        self.valid_move = [self._valid_move(color) for color in (1, 2)]
    
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
            assert x == -1 and y == -1 or (x, y) in self.valid_move[cur_player]
        except:
            # Invalid action
            self.round = None
            self.display.append({'winner' : 1 - cur_player})
            return (2, 0) if cur_player else (0, 2)
        color = cur_player + 1
        if x != -1 and y != -1:
            self.board[x][y] = color
            for i, j in self.valid_move[cur_player][(x, y)]:
                self.board[i][j] = color
        self.round += 1
        self.last_action = action
        # check episode ends
        self.valid_move = [self._valid_move(color) for color in (1, 2)]
        if not self.valid_move[0] and not self.valid_move[1]:
            # both players have no valid moves
            self.round = None
            black, white = (len([0 for i in range(8) for j in range(8) if self.board[i][j] == color]) for color in (1, 2))
            if black > white:
                self.display.append({'x' : x, 'y' : y, 'winner' : 0})
                return (2, 0)
            if white > black:
                self.display.append({'x' : x, 'y' : y, 'winner' : 1})
                return (0, 2)
            self.display.append({'x' : x, 'y' : y})
            return (1, 1)
        self.display.append({'x' : x, 'y' : y})
    
    def render(self, mode = 'ansi'):
        if mode == 'ansi':
            if self.viewer is None:
                self.viewer = ReversiTextViewer()
                self.viewer.reset()
            self.viewer.render(self.display)
            self.display = []
        else:
            super(ReversiEnv, self).render(mode)
    
    def close(self):
        self.closed = True
    
    def seed(self, seed = None):
        # No randomness
        pass

    def _valid_move(self, color):
        valid = {}
        for i in range(8):
            for j in range(8):
                if self.board[i][j] == 0:
                    change = self._test_change(i, j, color)
                    if change:
                        valid[(i, j)] = change
        return valid
    
    def _test_change(self, x, y, color):
        b = self.board
        change = []
        for dx, dy in ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)):
            t = []
            nx = x + dx
            ny = y + dy
            while self._in_board(nx, ny) and b[nx][ny] == 3 - color:
                t.append((nx, ny))
                nx += dx
                ny += dy
            if not (self._in_board(nx, ny) and b[nx][ny] == color): continue
            change.extend(t)
        return change
    
    def _in_board(self, x, y):
        return 0 <= x < 8 and 0 <= y < 8