from rich import box
from rich import print as rprint
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from botzone.online.viewer.viewer import TextViewer

class ChineseStandardMahjongTextViewer(TextViewer):
    '''
    {action = INIT, quan = 0..3}
    {action = DEAL, hand, tileCnt}
    {action = BUHUA, player, tile, tileCnt}
    {action = DRAW, player, tile, tileCnt}
    {action = PLAY, player, tile, tileCnt}
    {action = CHI, player, tile, tileCHI, tileCnt}
    {action = PENG, player, tile, tileCnt}
    {action = GANG, player, tile, tileCnt}
    {action = BUGANG, player, tile, tileCnt}
    {action = HU, player, fan = [{name, cnt, value}], fanCnt, score}
    {action = HUANG, tileCnt}
    {action = WA, player, score}
    '''
    
    def __init__(self, duplicate = True):
        self.duplicate = duplicate
        r = lambda s: Text(s, style = 'red')
        g = lambda s: Text(s, style = 'green')
        b = lambda s: Text(s, style = 'blue')
        draw = dict(
            J1 = r('\n中 \n'),
            J2 = g('\n發 \n'),
            J3 = b('╔═╗\n║ ║\n╚═╝'),
            T1 = r('\n | \n'),
            T2 = g(' | \n\n | '),
            T3 = g(' | \n\n| |'),
            T4 = g('| |\n\n| |'),
            T5 = g('| |\n') + r(' | ') + g('\n| |'),
            T6 = g('|||\n\n|||'),
            T7 = r(' | ') + g('\n|||\n|||'),
            T8 = g('|Ʌ|\n\n|V|'),
            T9 = g('|') + r('|') + g('|\n|') + r('|') + g('|\n|') + r('|') + g('|'),
            B1 = r('\n ● \n'),
            B2 = g(' ● ') + b('\n\n ● '),
            B3 = g('●  \n') + r(' ● \n') + b('  ●'),
            B4 = g('●') + b(' ●\n\n● ') + g('●'),
            B5 = g('●') + b(' ●\n ') + r('●') + b(' \n● ') + g('●'),
            B6 = g('● ●') + r('\n● ●\n● ●'),
            B7 = g('●●●') + r('\n● ●\n● ●'),
            B8 = b('●●●\n●●●\n●●'),
            B9 = b('●●●') + r('\n●●●') + g('\n●●●')
        )
        for i in range(4): draw['F%d' % (i + 1)] = b('\n%s \n' % '東南西北'[i])
        for i in range(4): draw['H%d' % (i + 1)] = r('\n%s \n' % '春夏秋冬'[i])
        for i in range(4): draw['H%d' % (i + 5)] = b('\n%s \n' % '梅蘭竹菊'[i])
        for i in range(9): draw['W%d' % (i + 1)] = b('一二三四五六七八九'[i]) + r('\n\n 萬')
        draw['back'] = Text('   \n   \n   ', style = 'on green')
        self.draw = draw
        self.wind = ['East', 'South', 'West', 'North']
    
    def reset(self, initdata = None):
        self.round = -1
        self.player = -1
        self.tile = None
        self.score = None
        self.hands = None
        self.fan = None
        self.discards = [[] for i in range(4)]
    
    def render(self, displays, bootstrap = True):
        if not displays: return
        # Recover state
        for display in displays:
            self.round += 1
            if display['action'] == 'INIT':
                self.prevalentWind = display['quan']
            elif display['action'] == 'DEAL':
                self.tileCnt = display['tileCnt']
                self.hands = [[x for x in hand if not x.startswith('H')] for hand in display['hand']]
                self.flowers = [[x for x in hand if x.startswith('H')] for hand in display['hand']]
                self.packs = [[] for i in range(4)]
            elif display['action'] == 'BUHUA':
                self.tileCnt = display['tileCnt']
                self.player = display['player']
                tile = display['tile']
                self.msg = 'BUHUA ' + tile
                self.flowers[self.player].append(tile)
            elif display['action'] == 'DRAW':
                self.tileCnt = display['tileCnt']
                if self.tile and not self.msg.startswith('BUGANG'): self.discards[self.player].append(self.tile)
                self.player = display['player']
                self.tile = display['tile']
                self.msg = 'DRAW ' + self.tile
            elif display['action'] == 'PLAY':
                self.tileCnt = display['tileCnt']
                self.hands[self.player].append(self.tile)
                self.player = display['player']
                self.tile = display['tile']
                self.hands[self.player].remove(self.tile)
                self.msg = 'PLAY ' + self.tile
            elif display['action'] == 'CHI':
                self.tileCnt = display['tileCnt']
                self.player = display['player']
                tileChow = display['tileCHI']
                color = tileChow[0]
                num = int(tileChow[1])
                for i in range(-1, 2):
                    tile = color + str((num + i))
                    if tile != self.tile: self.hands[self.player].remove(tile)
                    self.packs[self.player].append(tile)
                self.msg = 'CHI ' + self.tile
                self.tile = display['tile']
                self.hands[self.player].remove(self.tile)
                self.msg += '\nPLAY ' + self.tile
            elif display['action'] == 'PENG':
                self.tileCnt = display['tileCnt']
                self.player = display['player']
                for i in range(2): self.hands[self.player].remove(self.tile)
                for i in range(3): self.packs[self.player].append(self.tile)
                self.msg = 'PENG ' + self.tile
                self.tile = display['tile']
                self.hands[self.player].remove(self.tile)
                self.msg += '\nPLAY ' + self.tile
            elif display['action'] == 'GANG':
                self.tileCnt = display['tileCnt']
                player = display['player']
                tile = display['tile']
                self.hands[player].append(self.tile)
                for i in range(4): self.hands[player].remove(tile)
                if player == self.player:
                    # in secret
                    self.packs[player].extend(['back', 'back', tile, 'back'])
                else:
                    for i in range(4): self.packs[player].append(tile)
                self.player = player
                self.msg = 'GANG ' + tile
                self.tile = None
            elif display['action'] == 'BUGANG':
                self.tileCnt = display['tileCnt']
                player = display['player']
                tile = display['tile']
                self.hands[self.player].append(self.tile)
                self.hands[player].remove(tile)
                self.packs[player].insert(self.packs[player].index(tile), tile)
                self.msg = 'BUGANG ' + tile
            elif display['action'] == 'HU':
                self.player = display['player']
                self.fan = display['fan']
                self.fanCnt = display['fanCnt']
                self.score = display['score']
                self.hands[self.player].append(self.tile)
                self.msg = 'HU'
                self.tile = None
            elif display['action'] == 'HUANG':
                self.tileCnt = display['tileCnt']
                self.score = [0, 0, 0, 0]
                if self.tile: self.discards[self.player].append(self.tile)
                self.tile = None
                self.player = -1
            else:
                self.player = display['player']
                self.score = display['score']
                self.msg = display['action']
                self.tile = None
        
        # Render
        if not self.hands:
            # Round 0
            print(self.wind[self.prevalentWind], 'Wind, Round', self.round)
            return
        if self.duplicate:
            print(self.wind[self.prevalentWind], 'Wind, Round', self.round)
        else:
            print(self.wind[self.prevalentWind], 'Wind, Round', self.round, ',', self.tileCnt, 'tiles left.')
        captions = ['\nPlayer %d\n\n%s' % (i + 1, self.wind[i]) for i in range(4)]
        hands = []
        for i in range(4):
            t = Table(show_header = False, box = box.SQUARE, padding = 0)
            t.add_row(*(self.draw[tile] for tile in sorted(self.hands[i])))
            hands.append(t)
        packs = []
        for i in range(4):
            t = Table(show_header = False, box = box.SQUARE, padding = 0)
            t.add_row(*(self.draw[tile] for tile in sorted(self.flowers[i])), *(self.draw[tile] for tile in self.packs[i]))
            packs.append(t)
        tiles = ['' for i in range(4)]
        if self.player >= 0 and self.tile: tiles[self.player] = Panel.fit(self.draw[self.tile], box = box.SQUARE, padding = 0)
        msgs = ['' for i in range(4)]
        if self.duplicate:
            for i in range(4): msgs[i] += '%d tiles left.\n\n' % self.tileCnt[i]
        if self.score:
            for i in range(4): msgs[i] += 'Score: %d\n\n' % self.score[i]
        if self.player >= 0:
            msgs[self.player] += self.msg
        t = Table(show_lines = True, show_header = False, box = box.SQUARE, padding = 0)
        for i in range(4):
            t.add_row(captions[i], hands[i], packs[i], tiles[i], msgs[i])
        rprint(t)
        print('Tiles discarded:')
        t = Table(show_lines = True, show_header = False, box = box.SQUARE, padding = 0)
        for i in range(4):
            t.add_row(*(self.draw[tile] for tile in self.discards[i]))
        rprint(t)
        if self.fan:
            print('Total Fan:', self.fanCnt)
            for fan in self.fan:
                print('%s %d Fan * %d' % (fan['name'], fan['value'], fan['cnt']))
