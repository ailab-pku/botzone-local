from rich import box, print
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from botzone.online.viewer.viewer import TextViewer

class AmazonsTextViewer(TextViewer):
    '''
    {blackCount, whiteCount} in first round,
    {blackCount, whiteCount[,x0, y0, x1, y1, x2, y2][, winner, err]} in other rounds.
    '''
    
    def __init__(self, size = 8):
        self.stones = ' ●○●'
        self.size = size
    
    def reset(self, initdata = None):
        self.board = b = [[0 for j in range(self.size)] for i in range(self.size)]
        self.round = -1
        p = (self.size + 2) // 3
        b[0][p - 1] = b[p - 1][0] = b[-p][0] = b[-1][p - 1] = 1 # 1 for black
        b[0][-p] = b[p - 1][-1] = b[-p][-1] = b[-1][-p] = 2 # 2 for white
        self.count = [0, 0]
    
    def render(self, displays, bootstrap = True):
        b = self.board
        # Recover state
        for display in displays:
            self.round += 1
            self.count = [display['blackCount'], display['whiteCount']]
            if 'x0' not in display: continue
            x0 = display['x0']
            if x0 == -1: continue
            y0 = display['y0']
            x1 = display['x1']
            y1 = display['y1']
            x2 = display['x2']
            y2 = display['y2']
            color = 2 - self.round % 2
            b[x1][y1] = b[x0][y0]
            b[x0][y0] = 0
            b[x2][y2] = -1

        message = 'Round: %d\n%s: %d\n%s: %d\nNext: %s' % (
            self.round,
            self.stones[1],
            self.count[0],
            self.stones[2],
            self.count[1],
            self.stones[1 + self.round % 2]
        )
        styles = [[self.stones[b[i][j]] if b[i][j] >= 0 else Text(self.stones[b[i][j]], style = 'blue') for j in range(self.size)] for i in range(self.size)]
        if displays:
            d = displays[-1]
            if not d: d = {}
            x0 = d.get('x0', -1)
            y0 = d.get('y0', -1)
            if x0 != -1 and isinstance(styles[x0][y0], str):
                styles[x0][y0] = Text(styles[x0][y0], 'on red')
            x1 = d.get('x1', -1)
            y1 = d.get('y1', -1)
            if x1 != -1:
                styles[x1][y1] = Text(styles[x1][y1], 'on green')
            x2 = d.get('x2', -1)
            y2 = d.get('y2', -1)
            if x2 != -1:
                styles[x2][y2].style = 'blue on yellow'
            if 'winner' in d:
                message += '\n%s wins!' % self.stones[d['winner'] + 1]
        t = Table.grid(padding = (0, 1))
        t.add_row('', *map(chr, range(65, 65 + self.size)))
        for j in range(self.size):
            t.add_row(str(1 + j), *[styles[i][j] for i in range(self.size)])
        tt = Table.grid(padding = (0, 4))
        tt.add_row(t, message)
        print(Panel.fit(tt, box = box.SQUARE))