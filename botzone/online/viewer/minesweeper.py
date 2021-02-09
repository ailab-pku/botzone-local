import json
from rich import box, print
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from botzone.online.viewer.viewer import TextViewer

class MineSweeperTextViewer(TextViewer):
    '''
    {status: [{row, col, val}], msg: FINISH/INVALIDMOVE}
    '''
    
    def __init__(self):
        fgs = ['default', '#0000ff', '#008000', '#ff0000', '#000080', '#800000', '#008080', '#000000', '#808080', '#000000', 'default']
        chars = [' ', '1', '2', '3', '4', '5', '6', '7', '8', '●', ' ']
        bgs = ['#c0c0c0'] * 10 + ['#ffffff']
        self.draw = [Text(chars[i], style = '%s on %s' % (fgs[i], bgs[i])) for i in range(11)]
    
    def reset(self, initdata = None):
        if not initdata: initdata = {}
        self.width = initdata.get('width', 30)
        self.height = initdata.get('height', 20)
        self.mineleft = self.minecount = initdata.get('minecount', 80)
        self.board = [[10 for i in range(self.width)] for j in range(self.height)]
        self.round = -1
    
    def render(self, displays, bootstrap = True):
        b = self.board
        # Recover state
        for display in displays:
            self.round += 1
            if not display: continue
            status = display.get('status', None)
            if not status: status = []
            for pos in status:
                x = pos['row']
                y = pos['col']
                val = pos['val']
                b[x][y] = val
                if val == 9: self.mineleft -= 1
        
        message = 'Round: %d\nMines total: %d\nMines left: %d' % (
            self.round,
            self.minecount,
            self.mineleft
        )
        if displays:
            d = displays[-1]
            if not d: d = {}
            if 'msg' in d:
                if d['msg'] == 'INVALIDMOVE':
                    message += '\nInvalid move!'
                elif d['msg'] == 'FINISH':
                    message += '\nFinish!'
        t = Table.grid()
        for x in range(self.height):
            t.add_row(*(self.draw[b[x][y]] for y in range(self.width)))
        tt = Table.grid(padding = (0, 4))
        tt.add_row(t, message)
        print(Panel.fit(tt, box = box.SQUARE))