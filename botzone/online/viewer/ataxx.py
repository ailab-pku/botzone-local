from rich import box, print
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from botzone.online.viewer.viewer import TextViewer

class AtaxxTextViewer(TextViewer):
    '''
    Empty string in first round, {x0, y0, x1, y1[, winner, err]} in other rounds.
    '''
    
    def __init__(self):
        self.stones = ' ●○'
    
    def reset(self, initdata = None):
        self.board = b = [[0 for j in range(7)] for i in range(7)]
        self.round = -1
        self.count = [0, 2, 2]
        b[0][0] = b[-1][-1] = 1 # 1 for black
        b[0][-1] = b[-1][0] = 2 # 2 for white
    
    def render(self, displays, bootstrap = True):
        b = self.board
        # Recover state
        for display in displays:
            self.round += 1
            if not display: display = {}
            change = []
            if 'x0' not in display: continue
            x0 = display['x0']
            y0 = display['y0']
            x1 = display['x1']
            y1 = display['y1']
            if x0 == -1: continue
            color = 2 - self.round % 2
            if abs(x1 - x0) == 2 or abs(y1 - y0) == 2:
                b[x0][y0] = 0
                self.count[color] -= 1
            b[x1][y1] = color
            self.count[color] += 1
            for dx, dy in ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)):
                nx = x1 + dx
                ny = y1 + dy
                if self._in_board(nx, ny) and b[nx][ny] == 3 - color:
                    change.append((nx, ny))
            for nx, ny in change:
                b[nx][ny] = color
            self.count[color] += len(change)
            self.count[3 - color] -= len(change)

        message = 'Round: %d\n%s: %d\n%s: %d\nNext: %s' % (
            self.round,
            self.stones[1],
            self.count[1],
            self.stones[2],
            self.count[2],
            self.stones[1 + self.round % 2]
        )
        style_before = lambda s: Text(s, style = 'on blue')
        style_cur = lambda s: Text(s, style = 'on red')
        style_change = lambda s: Text(s, style = 'yellow')
        style_normal = lambda s: s
        styles = [[style_normal for i in range(7)] for j in range(7)]
        if displays:
            d = displays[-1]
            if not d: d = {}
            x0 = d.get('x0', -1)
            y0 = d.get('y0', -1)
            if x0 != -1:
                styles[x0][y0] = style_before
            x1 = d.get('x1', -1)
            y1 = d.get('y1', -1)
            if x1 != -1:
                styles[x1][y1] = style_cur
            if 'winner' in d:
                message += '\n%s wins!' % self.stones[d['winner'] + 1]
            for x, y in change: styles[x][y] = style_change
        t = Table.grid(padding = (0, 1))
        t.add_row('', *map(chr, range(65, 65 + 7)))
        for j in range(7):
            t.add_row(str(1 + j), *[styles[i][j](self.stones[b[i][j]]) for i in range(7)])
        tt = Table.grid(padding = (0, 4))
        tt.add_row(t, message)
        print(Panel.fit(tt, box = box.SQUARE))

    def _in_board(self, x, y):
        return 0 <= x < 7 and 0 <= y < 7