from rich import box, print
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from botzone.online.viewer.viewer import TextViewer

class GoTextViewer(TextViewer):
    '''
    Empty string in first and pass round,
    {color, x, y, remove: [{x, y}]} in other rounds,
    {winner[, color, x, y][, stones: {'0', '1', komi}][, error, error_info]} in final round.
    '''
    
    def __init__(self, size = 8):
        self.stones = ' ●○'
        self.size = size
    
    def reset(self, initdata = None):
        self.board = [[0 for j in range(self.size)] for i in range(self.size)]
        self.round = -1
    
    def render(self, displays, bootstrap = True):
        b = self.board
        x = y = -1
        # Recover state
        for display in displays:
            self.round += 1
            if not display: continue
            if 'x' not in display: continue
            x = display['x'] - 1
            y = display['y'] - 1
            color = display['color']
            self.board[x][y] = color + 1
            for d in display['remove']:
                self.board[d['x'] - 1][d['y'] - 1] = 0
        
        message = 'Round: %d' % self.round
        if displays:
            if 'x' not in display:
                x = y = -1
            if 'winner' in display:
                message += '\n\nwinner: %s' % self.stones[display['winner'] + 1]
                if 'stones' in display:
                    display = display['stones']
                    for i in range(2):
                        message += ('\n\n%s: %f' % (self.stones[i + 1], display[str(i)])).rstrip('0').rstrip('.')
                    message += ('\n\nkomi: %f' % display['komi']).rstrip('0').rstrip('.')
                if 'error_info' in display:
                    message += '\n\nError: %s' % display['error_info']
            elif 'x' not in display and self.round > 0:
                message += '\n\n%s pass!' % self.stones[2 - self.round % 2]
            else:
                message += '\n\nNext: %s' % self.stones[self.round % 2 + 1]
        t = Table.grid(padding = (0, 1))
        t.add_row('', *map(chr, range(65, 65 + self.size)))
        for j in range(self.size):
            t.add_row(str(1 + j), *[Text(self.stones[b[i][j]], style = 'red') if i == x and j == y else self.stones[b[i][j]] for i in range(self.size)])
        tt = Table.grid(padding = (0, 4))
        tt.add_row(t, message)
        print(Panel.fit(tt, box = box.SQUARE))