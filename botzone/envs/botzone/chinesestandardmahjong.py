from collections import defaultdict
from copy import deepcopy
import random

from botzone import *
from botzone.online.viewer.chinesestandardmahjong import ChineseStandardMahjongTextViewer

try:
    from MahjongGB import MahjongFanCalculator
except:
    print('MahjongGB library required! Please visit https://github.com/ailab-pku/PyMahjongGB for more information.')
    raise

class ChineseStandardMahjongEnv(Env):
    '''
    Description:
        Mahjong using Chinese Standard Rule.
        Rule: https://wiki.botzone.org.cn/index.php?title=Chinese-Standard-Mahjong/en
        
        Decision order: Four players act simutaneously in each turn.
        Initdata: {
            srand: random seed, integer
            quan: prevalent wind, 0..3 for east/south/west/north
            walltiles: a string represents initial tile wall, each tile split by space
        }
        Request and response:
            See https://wiki.botzone.org.cn/index.php?title=Chinese-Standard-Mahjong/en#Bot_Input_and_Output
        
        Episode Termination:
            Some player makes Mahjong or a draw when tile wall runs out.
        Score:
            Basic score = 8;
            Win by self drawn:
                winner is (Basic score + Fan points) * 3;
                loser is -(Basic score + Fan points);
            Win by ignition:
                winner is Basic score * 3 + Fan points;
                loser of ignition: -(Basic score + Fan points);
                other losers: -Basic score.
            Draw:
                0 for all.
    '''
    
    metadata = {'render.modes': ['ansi']}
    
    def __init__(self, duplicate = True):
        # Initialize configurations, possible viewers and state
        self.agents = None
        self.round = None
        self.closed = False
        self.initdata = {}
        self._seed = None
        self.display = []
        self.viewer = None
        self.duplicate = duplicate
    
    @property
    def player_num(self):
        return 4
    
    def reset(self, initdata = None):
        if self.closed:
            raise AlreadyClosed()
        if self.agents is None:
            raise AgentsNeeded()
        # Initialize each agent
        for agent in self.agents:
            agent.reset()
        # Initialize state for new episode
        self.round = 0
        if not initdata: initdata = {}
        if 'srand' in initdata:
            self.seed(initdata['srand'])
        if self._seed:
            random.seed(self._seed)
        if 'quan' in initdata:
            self.prevalentWind = initdata['quan']
        else:
            self.prevalentWind = random.randint(0, 3)
        if 'walltiles' in initdata:
            self.tileWall = initdata['walltiles'].split()
            assert len(self.tileWall) == 136 if self.duplicate else 144
        else:
            self.tileWall = []
            for j in range(4):
                for i in range(1, 10):
                    self.tileWall.append('W' + str(i))
                    self.tileWall.append('B' + str(i))
                    self.tileWall.append('T' + str(i))
                for i in range(1, 5):
                    self.tileWall.append('F' + str(i))
                for i in range(1, 4):
                    self.tileWall.append('J' + str(i))
            if not self.duplicate:
                for i in range(1, 9):
                    self.tileWall.append('H' + str(i))
            random.shuffle(self.tileWall)
        self.initdata = dict(quan = self.prevalentWind, walltiles = self.tileWall)
        self.display = [dict(quan = self.prevalentWind, action = 'INIT')]
        if self.viewer: self.viewer.reset(self.initdata)
        
        if self.duplicate:
            self.tileWall = [self.tileWall[i * 34 : (i + 1) * 34] for i in range(4)]
        self.shownTiles = defaultdict(int)
        self.state = -1
        self.requests = ['0 %d %d' % (seatWind, self.prevalentWind) for seatWind in range(4)]
    
    def step(self):
        if self.closed:
            raise AlreadyClosed()
        if self.round is None:
            raise ResetNeeded()
        
        responses = [self.agents[i].step(self.requests[i]) for i in range(4)]
        self.round += 1
        
        try:
            for i in range(4):
                # check response format
                if not isinstance(responses[i], str):
                    raise Error(i)
            if self.state == -1:
                # Prepare to deal
                for i in range(4):
                    if responses[i] != 'PASS':
                        raise Error(i)
                self._deal()
            elif self.state == 0:
                # Prepare to draw
                for i in range(4):
                    if responses[i] != 'PASS':
                        raise Error(i)
                self._draw(self.curPlayer)
            elif self.state == 1:
                # Prepare to discard
                for i in range(4):
                    if i != self.curPlayer and responses[i] != 'PASS':
                        raise Error(i)
                response = responses[self.curPlayer].split()
                if response[0] == 'HU':
                    self.shownTiles[self.curTile] += 1
                    return self._checkMahjong(self.curPlayer, isSelfDrawn = True, isAboutKong = self.isAboutKong)
                elif response[0] == 'PLAY':
                    if len(response) != 2: raise Error(self.curPlayer)
                    self._discard(self.curPlayer, response[1])
                elif response[0] == 'GANG' and not self.myWallLast and not self.wallLast:
                    if len(response) != 2: raise Error(self.curPlayer)
                    self._kong(self.curPlayer, response[1])
                elif response[0] == 'BUGANG' and not self.myWallLast and not self.wallLast:
                    if len(response) != 2: raise Error(self.curPlayer)
                    self._promoteKong(self.curPlayer, response[1])
                else:
                    raise Error(self.curPlayer)
                self.isAboutKong = False
            elif self.state == 2:
                # Prepare to CHOW/PUNG/KONG/HU
                if responses[self.curPlayer] != 'PASS': raise Error(self.curPlayer)
                t = [response.split() for response in responses]
                # Priority: HU > PUNG/KONG > CHOW
                for j in range(4):
                    i = (self.curPlayer + j) % 4
                    if responses[i] == 'HU':
                        return self._checkMahjong(i)
                else:
                    for i in range(4):
                        if responses[i] == 'GANG' and self._canDrawTile(i) and not self.wallLast:
                            self._kong(i, self.curTile)
                            break
                        elif t[i][0] == 'PENG' and not self.wallLast and len(t[i]) == 2:
                            self._pung(i, self.curTile, t[i][1])
                            break
                    else:
                        i = (self.curPlayer + 1) % 4
                        if t[i][0] == 'CHI' and not self.wallLast and len(t[i]) == 3:
                            self._chow(i, t[i][1], t[i][2])
                        else:
                            for i in range(4):
                                if responses[i] != 'PASS': raise Error(i)
                            if self.wallLast:
                                # A draw
                                self.display.append(dict(action = 'HUANG', tileCnt = self._tileCnt()))
                                self.round = None
                                return (0, 0, 0, 0)
                            # Next player
                            self.curPlayer = (self.curPlayer + 1) % 4
                            self._draw(self.curPlayer)
            elif self.state == 3:
                if responses[self.curPlayer] != 'PASS': raise Error(self.curPlayer)
                for j in range(4):
                    i = (self.curPlayer + j) % 4
                    if responses[i] == 'HU':
                        return self._checkMahjong(i, isAboutKong = True)
                else:
                    for i in range(4):
                        if responses[i] != 'PASS': raise Error(i)
                    self._draw(self.curPlayer)
        except Error as e:
            player = e.args[0]
            score = [10] * 4
            score[player] = -30
            self.round = None
            self.display.append(dict(action = 'WA', player = player, score = score))
            return tuple(score)
    
    def _drawTile(self, player):
        if self.duplicate:
            return self.tileWall[player].pop()
        return self.tileWall.pop()
    
    def _canDrawTile(self, player):
        if self.duplicate:
            return bool(self.tileWall[player])
        return bool(self.tileWall)
    
    def _tileCnt(self):
        if self.duplicate:
            return [len(h) for h in self.tileWall]
        return len(self.tileWall)
    
    def _deal(self):
        self.hands = []
        self.flowers = []
        self.packs = []
        alls = [[] for i in range(4)]
        for i in range(4):
            hand = []
            flower = []
            while len(hand) < 13:
                tile = self._drawTile(i)
                alls[i].append(tile)
                if tile.startswith('H'): flower.append(tile)
                else: hand.append(tile)
            self.hands.append(hand)
            self.flowers.append(flower)
            self.packs.append([])
        flowerCount = ' '.join(str(len(f)) for f in self.flowers)
        flowerTiles = [f for f in flower for flower in self.flowers]
        self.requests = [' '.join(['1', flowerCount, ' '.join([*f, *flowerTiles])]) for f in self.hands]
        self.state = 0
        self.curPlayer = 0
        self.drawAboutKong = False
        self.display.append(dict(action = 'DEAL', hand = alls, tileCnt = self._tileCnt()))
    
    def _draw(self, player):
        tile = self._drawTile(player)
        self.myWallLast = not self._canDrawTile(player)
        self.wallLast = not self._canDrawTile((player + 1) % 4)
        self.isAboutKong = self.drawAboutKong
        self.drawAboutKong = False
        if tile.startswith('H'):
            self.state = 0
            self.flowers[player].append(tile)
            self.requests = ['3 %d BUHUA %s' % (player, tile)] * 4
            self.display.append(dict(action = 'BUHUA', player = player, tile = tile, tileCnt = self._tileCnt()))
        else:
            self.state = 1
            self.curTile = tile
            self.requests = ['2 %s' % tile if i == player else '3 %d DRAW' % player
                for i in range(4)]
            self.display.append(dict(action = 'DRAW', player = player, tile = tile, tileCnt = self._tileCnt()))
    
    def _discard(self, player, tile):
        self.hands[player].append(self.curTile)
        if tile not in self.hands[player]: raise Error(player)
        self.hands[player].remove(tile)
        self.shownTiles[tile] += 1
        self.curTile = tile
        self.state = 2
        self.requests = ['3 %d PLAY %s' % (player, tile)] * 4
        self.display.append(dict(action = 'PLAY', player = player, tile = tile, tileCnt = self._tileCnt()))
    
    def _kong(self, player, tile):
        self.hands[player].append(self.curTile)
        if self.hands[player].count(tile) < 4: raise Error(player)
        for i in range(4): self.hands[player].remove(tile)
        # offer: 0 for self, 123 for up/oppo/down
        self.packs[player].append(('GANG', tile, (player + 4 - self.curPlayer) % 4))
        self.shownTiles[tile] = 4
        self.state = 0
        self.curPlayer = player
        self.drawAboutKong = True
        self.requests = ['3 %d GANG' % player] * 4
        self.display.append(dict(action = 'GANG', player = player, tile = tile, tileCnt = self._tileCnt()))
    
    def _pung(self, player, tile, discard):
        self.hands[player].append(self.curTile)
        if self.hands[player].count(tile) < 3: raise Error(player)
        for i in range(3): self.hands[player].remove(tile)
        # offer: 0 for self, 123 for up/oppo/down
        self.packs[player].append(('PENG', tile, (player + 4 - self.curPlayer) % 4))
        self.shownTiles[tile] += 2
        if discard not in self.hands[player]: raise Error(player)
        self.hands[player].remove(discard)
        self.shownTiles[discard] += 1
        self.state = 2
        self.curPlayer = player
        self.wallLast = not self._canDrawTile((player + 1) % 4)
        self.curTile = discard
        self.requests = ['3 %d PENG %s' % (player, discard)] * 4
        self.display.append(dict(action = 'PENG', player = player, tile = discard, tileCnt = self._tileCnt()))
    
    def _chow(self, player, tile, discard):
        self.hands[player].append(self.curTile)
        self.shownTiles[self.curTile] -= 1
        color = tile[0]
        num = int(tile[1])
        for i in range(-1, 2):
            t = color + str(num + i)
            if t not in self.hands[player]: raise Error(player)
            self.hands[player].remove(t)
            self.shownTiles[t] += 1
        # offer: 123 for which tile is offered
        self.packs[player].append(('CHI', tile, int(self.curTile[1]) - num + 2))
        if discard not in self.hands[player]: raise Error(player)
        self.hands[player].remove(discard)
        self.shownTiles[discard] += 1
        self.state = 2
        self.curPlayer = player
        self.wallLast = not self._canDrawTile((player + 1) % 4)
        self.curTile = discard
        self.requests = ['3 %d CHI %s %s' % (player, tile, discard)] * 4
        self.display.append(dict(action = 'CHI', player = player, tile = discard, tileCHI = tile, tileCnt = self._tileCnt()))
    
    def _promoteKong(self, player, tile):
        self.hands[player].append(self.curTile)
        idx = -1
        for i in range(len(self.packs[player])):
            if self.packs[player][i][0] == 'PENG' and self.packs[player][i][1] == tile:
                idx = i
        if idx < 0: raise Error(player)
        self.hands[player].remove(tile)
        offer = self.packs[player][idx][2]
        self.packs[player][idx] = ('GANG', tile, offer)
        self.shownTiles[tile] = 4
        self.state = 3
        self.curPlayer = player
        self.curTile = tile
        self.drawAboutKong = True
        self.requests = ['3 %d BUGANG %s' % (player, tile)] * 4
        self.display.append(dict(action = 'BUGANG', player = player, tile = tile, tileCnt = self._tileCnt()))
    
    def _checkMahjong(self, player, isSelfDrawn = False, isAboutKong = False):
        try:
            fans = MahjongFanCalculator(
                pack = tuple(self.packs[player]),
                hand = tuple(self.hands[player]),
                winTile = self.curTile,
                flowerCount = len(self.flowers[player]),
                isSelfDrawn = isSelfDrawn,
                is4thTile = self.shownTiles[self.curTile] == 4,
                isAboutKong = isAboutKong,
                isWallLast = self.wallLast,
                seatWind = player,
                prevalentWind = self.prevalentWind,
                verbose = True
            )
            f = []
            fanCnt = 0
            for fanPoint, cnt, fanName, fanNameEn in fans:
                f.append(dict(name = fanName, cnt = cnt, value = fanPoint))
                fanCnt += fanPoint * cnt
            if fanCnt < 8: raise Error('Not Enough Fans')
            if isSelfDrawn:
                score = [-(8 + fanCnt)] * 4
                score[player] = (8 + fanCnt) * 3
            else:
                score = [-8] * 4
                score[player] = 8 * 3 + fanCnt
                score[self.curPlayer] -= fanCnt
            self.display.append(dict(
                action = 'HU',
                player = player,
                fan = f,
                fanCnt = fanCnt,
                score = score
            ))
            self.round = None
            return tuple(score)
        except Exception as e:
            raise Error(player)
    
    def render(self, mode = 'ansi'):
        if mode == 'ansi':
            if self.viewer is None:
                self.viewer = ChineseStandardMahjongTextViewer(duplicate = self.duplicate)
                self.viewer.reset(self.initdata)
            self.viewer.render(self.display)
            self.display = []
        else:
            super(ChineseStandardMahjongEnv, self).render(mode)
    
    def close(self):
        self.closed = True