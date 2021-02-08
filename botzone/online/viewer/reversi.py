from rich import box, print
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from botzone.online.viewer.viewer import TextViewer

class ReversiTextViewer(TextViewer):
    '''
    Empty string in first or skipped round, {x, y, winner} in other rounds.
    '''
    
    def __init__(self):
        self.console = Console()
        self.stones = ' ●○'
    
    def reset(self):
        self.board = b = [[0 for j in range(8)] for i in range(8)]
        self.round = -1
        self.count = [0, 2, 2]
        b[3][3] = b[4][4] = 2 # 2 for white
        b[3][4] = b[4][3] = 1 # 1 for black
    
    def render(self, displays, bootstrap = True):
        b = self.board
        # Recover state
        for display in displays:
            self.round += 1
            if not display: display = {}
            change = []
            if 'x' not in display: continue
            if 'x' in display:
                x = display['x']
                y = display['y']
                color = 2 - self.round % 2
                b[x][y] = color
                self.count[color] += 1
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
        style_cur = lambda s: Text(s, style = 'red')
        style_change = lambda s: Text(s, style = 'yellow')
        style_normal = lambda s: s
        styles = [[style_normal for i in range(8)] for j in range(8)]
        if displays:
            d = displays[-1]
            if not d: d = {}
            if not 'x' in d and self.round:
                message += '\n%s skipped!' % self.stones[2 - self.round % 2]
            else:
                x = d.get('x', -1)
                y = d.get('y', -1)
                styles[x][y] = style_cur
            if 'winner' in d:
                message += '\n%s wins!' % self.stones[d['winner'] + 1]
            for x, y in change: styles[x][y] = style_change
        t = Table.grid(padding = (0, 1))
        t.add_row('', *map(str, range(1, 9)))
        for j in range(8):
            t.add_row(chr(65 + j), *[styles[i][j](self.stones[b[i][j]]) for i in range(8)])
        tt = Table.grid(padding = (0, 4))
        tt.add_row(t, message)
        print(Panel.fit(tt, box = box.SQUARE))

    def _in_board(self, x, y):
        return 0 <= x < 8 and 0 <= y < 8