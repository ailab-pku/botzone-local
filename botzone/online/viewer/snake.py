from rich import box
from rich import print
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from botzone.online.viewer.viewer import TextViewer

class SnakeTextViewer(TextViewer):
    '''
    First round: {'0': {x, y}, '1': {x, y}, width, height, obstacle: list of {x, y}}
    Other rounds: {'0': 0..3, '1': 0..3, 'grow': 'true'/'false'}
    Last round in case of crash: {['0': 0..3], ['1': 0..3], 'grow': 'true'/'false', 'winner', 'err'}
    '''
    
    def __init__(self):
        self.dx = [-1, 0, 1, 0]
        self.dy = [0, 1, 0, -1]
        self.draw_init = ['├:', ':┤']
        self.draw_head = [' !', ':─', ' ¡', '─:']
        self.draw_tail = [' ┴', '├─', ' ┬', '─┤']
        self.draw_body = {3 : ' └', 5 : ' │', 9 : '─┘', 6 : ' ┌', 12 : '─┐', 10 : '──'}
        self.draw_style = ['on green', 'on red']
        pass
    
    def reset(self, initdata = None):
        self.round = -1
    
    def render(self, displays, bootstrap = True):
        # Recover state
        display = {}
        for display in displays:
            self.round += 1
            if self.round == 0:
                self.width = display['width']
                self.height = display['height']
                self.board = [[0 for i in range(self.height)] for j in range(self.width)]
                for p in display['obstacle']:
                    self.board[p['y'] - 1][p['x'] - 1] = 1
                self.body = [[], []]
                for i in range(2):
                    p = display[str(i)]
                    self.body[i].append((p['y'] - 1, p['x'] - 1))
            else:
                for i in range(2):
                    x, y = self.body[i][-1]
                    if str(i) in display:
                        d = 3 - display[str(i)]
                        self.body[i].append((x + self.dx[d], y + self.dy[d]))
                    if display['grow'] == 'false':
                        self.body[i].pop(0)
        grid = [['▓▓' if i else '  ' for i in row] for row in self.board]
        for i in range(2):
            body = self.body[i]
            l = len(body)
            if l == 1:
                x, y = body[0]
                # draw initial
                grid[x][y] = Text(self.draw_init[i], style = self.draw_style[i])
                continue
            # draw head
            x, y = body[-1]
            if 0 <= x < self.width and 0 <= y < self.height:
                # in case of invalid move
                grid[x][y] = Text(self.draw_head[self._direction(body[-1], body[-2])], style = self.draw_style[i])
            # draw body
            for j in range(1, l - 1):
                x, y = body[j]
                grid[x][y] = Text(self.draw_body.get((1 << self._direction(body[j], body[j - 1])) + (1 << self._direction(body[j], body[j + 1])), '??'), style = self.draw_style[i])
            # draw tail
            x, y = body[0]
            grid[x][y] = Text(self.draw_tail[self._direction(body[0], body[1])], style = self.draw_style[i])
        message = '\n\nRound: %d\n\nLength: %d' % (self.round, len(self.body[0]))
        if 'winner' in display:
            message += '\n\nPlayer %s wins!' % display['winner']
        t = Table.grid()
        for row in grid: t.add_row(*row)
        t = Panel.fit(t, box = box.SQUARE, padding = 0)
        tt = Table.grid(padding = (0, 4))
        tt.add_row(t, message)
        print(tt)

    def _direction(self, p1, p2):
        x, y = p1
        for k in range(4):
            if (x + self.dx[k], y + self.dy[k]) == p2:
                return k