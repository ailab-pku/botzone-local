from collections import defaultdict
from rich import box, print
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from botzone.online.viewer.viewer import TextViewer

class KingzTextViewer(TextViewer):
    '''
    {
        status: opening/combat/end/finish
        count: list of 100 int,
        type: list of 100 int,
        belong: list of 100 int,
        operation: list of 2 list of 4 int (x, y, w, d),
        [winner: int,]
        [err: message]
    }
    '''
    
    def reset(self, initdata = None):
        self.color = ('default', 'bright_yellow', 'bright_cyan')
        self.round = -1
    
    def render(self, displays, bootstrap = True):
        operation = None
        display = {}
        for display in displays:
            self.round += 1
            status = display['status']
            if status == 'opening':
                self.count = display['count']
                self.info = display['type']
                self.belong = display['belong']
                continue
            operation = display.get('operation', None)
            if 'count' in display:
                self.count = display['count']
                self.info = display['type']
                self.belong = display['belong']
            elif operation:
                # Process state
                battle = defaultdict(lambda : [0, 0, 0])
                for p in range(2):
                    x, y, w, d = operation[p]
                    self.count[x * 10 + y] -= w
                    x += (-1, 1, 0, 0, 0)[d]
                    y += (0, 0, -1, 1, 0)[d]
                    battle[(x, y)][p + 1] += w
                for x, y in battle:
                    battle[(x, y)][self.belong[x * 10 + y]] += self.count[x * 10 + y]
                    self.count[x * 10 + y] = 0
                for x, y in battle:
                    neutral, red, blue = self._battle(*battle[(x, y)])
                    self.count[x * 10 + y] = neutral + red + blue
                    if neutral: self.belong[x * 10 + y] = 0
                    elif red: self.belong[x * 10 + y] = 1
                    elif blue: self.belong[x * 10 + y] = 2
                for i in range(10):
                    for j in range(10):
                        if self.belong[i * 10 + j] == 0: continue
                        if self.info[i * 10 + j] == 2: self.count[i * 10 + j] += 2
                        if self.info[i * 10 + j] == 1: self.count[i * 10 + j] += 1
                        if self.info[i * 10 + j] == 0 and self.round % 8 == 0: self.count[i * 10 + j] += 1
        
        troops = [0, 0, 0]
        growth = [0, 0, 0]
        for i in range(100):
                troops[self.belong[i]] += self.count[i]
                growth[self.belong[i]] += (0.125, 1, 2, 0)[self.info[i]]
        message = (Text('\nRound : %d\n\nTroops: ' % self.round)
            + Text(str(troops[1]), style = 'on ' + self.color[1])
            + ' : '
            + Text(str(troops[2]), style = 'on ' + self.color[2])
            + ' : '
            + Text(str(troops[0]), style = 'on ' + self.color[0])
            + '\n\nGrowth: '
            + Text(str(growth[1]), style = 'on ' + self.color[1])
            + ' : '
            + Text(str(growth[2]), style = 'on ' + self.color[2])
        )
        err = display.get('err', None)
        if err: message += '\n\n' + err
        
        draws = [[self._draw(self.info[i * 10 + j], self.belong[i * 10 + j], self.count[i * 10 + j])
            for j in range(10)]
            for i in range(10)]
        if operation:
            for p in range(2):
                x, y, w, d = operation[p]
                if d < 4 and w:
                    draws[x][y].style = 'red ' + draws[x][y].style
                    x += (-1, 1, 0, 0, 0)[d]
                    y += (0, 0, -1, 1, 0)[d]
                    draws[x][y].style = 'green ' + draws[x][y].style
        t = Table.grid()
        for row in draws: t.add_row(*row)
        for column in t.columns: column.width = 5
        tt = Table.grid(padding = (0, 4))
        tt.add_row(t, message)
        print(Panel.fit(tt, box = box.SQUARE))
    
    def _battle(self, neutral, red, blue):
        t = min(red, blue)
        red -= t
        blue -= t
        if red > 0:
            t = min(red, neutral)
            red -= t
            neutral -= t
        else:
            t = min(blue, neutral)
            blue -= t
            neutral -= t
        return neutral, red, blue
    
    def _draw(self, info, belong, count):
        if info == -1: return Text('\n\n', justify = 'center', style = 'on bright_black')
        if info == 1:
            return Panel(Text(str(count), justify = 'center'), padding = 0, style = 'on ' + self.color[belong], box = box.SQUARE)
        if info == 2:
            return Panel(Text(str(count), justify = 'center'), padding = 0, style = 'on ' + self.color[belong], box = box.DOUBLE)
        return Text('\n%d\n' % count if count else '\n\n', justify = 'center', style = 'on ' + self.color[belong])