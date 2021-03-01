from rich import box, print
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from botzone.online.viewer.viewer import TextViewer

class NoGoTextViewer(TextViewer):
    '''
    Empty string in first and pass round,
    {color, x, y} in other rounds,
    {winner[, color, x, y][, err]} in final round.
    '''
    
    def __init__(self):
        self.stones = ' ●○'
    
    def reset(self, initdata = None):
        self.board = [[0 for j in range(9)] for i in range(9)]
        self.round = -1
    
    def render(self, displays, bootstrap = True):
        b = self.board
        x = y = -1
        # Recover state
        for display in displays:
            self.round += 1
            if not display: continue
            if 'x' not in display: continue
            x = display['x']
            y = display['y']
            color = display['color']
            self.board[x][y] = color + 1
        
        message = 'Round: %d' % self.round
        if displays:
            if 'x' not in display:
                x = y = -1
            if 'winner' in display:
                message += '\n\nwinner: %s' % self.stones[display['winner'] + 1]
                if 'err' in display:
                    message += '\n\nError: %s' % display['err']
            else:
                message += '\n\nNext: %s' % self.stones[self.round % 2 + 1]
        t = Table.grid(padding = (0, 1))
        t.add_row('', *map(chr, range(65, 65 + 9)))
        for j in range(9):
            t.add_row(str(1 + j), *[Text(self.stones[b[i][j]], style = 'red') if i == x and j == y else self.stones[b[i][j]] for i in range(9)])
        tt = Table.grid(padding = (0, 4))
        tt.add_row(t, message)
        print(Panel.fit(tt, box = box.SQUARE))