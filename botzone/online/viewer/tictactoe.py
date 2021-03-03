from rich import box, print
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from botzone.online.viewer.viewer import TextViewer

class TicTacToeTextViewer(TextViewer):
    '''
    Empty string in first round,
    {x, y} in other rounds,
    {winner[, x, y][, err]} in final round.
    '''
    
    def __init__(self):
        self.stones = ' OX'
    
    def reset(self, initdata = None):
        self.board = [[0 for j in range(3)] for i in range(3)]
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
            color = 2 - self.round % 2
            self.board[x][y] = color
        
        message = 'Round: %d' % self.round
        if displays and displays[-1]:
            winner = displays[-1].get('winner', None)
        elif self.round == 9:
            winner = ''
        else:
            winner = None
        if winner is not None:
            if isinstance(winner, int):
                message += '\n%s wins!' % self.stones[winner + 1]
            else:
                message += '\nA tie!'
        else:
            message += '\nNext: %s' % self.stones[self.round % 2 + 1]
        t = Table.grid(padding = (0, 1))
        t.add_row('', *map(chr, range(65, 65 + 3)))
        for j in range(3):
            t.add_row(str(1 + j), *[Text(self.stones[b[i][j]], style = 'red') if i == x and j == y else self.stones[b[i][j]] for i in range(3)])
        tt = Table.grid(padding = (0, 4))
        tt.add_row(t, message)
        print(Panel.fit(tt, box = box.SQUARE))