from collections import defaultdict
from copy import deepcopy
import random

from botzone import *
from botzone.online.viewer.fightthelandlord import FightTheLandlordTextViewer

class FightTheLandlordEnv(Env):
    '''
    Description:
        Traditional FightTheLandlord game, with fixed position.
        Rule: https://wiki.botzone.org.cn/index.php?title=FightTheLandlord
        
        Decision order: In each turn only one player decide.
        Initdata: {
            seed: random seed, integer
            allocation: initial card, [list of 20, list of 17, list of 17]
            publiccard: public card, list of 3
        }
        Request:
            First: {history: [upup, up], publiccard: [...], own: [...]}
            Others: {history: [upup, up]}
        Response:
            [...], empty for pass.
        
        Episode Termination:
            The one who drops all card wins.
        Score:
            Two peasants share their average score.
            In case of invalid response, score is (-1, 2.5, 2.5) or (2.5, -1, -1)
    '''
    
    metadata = {'render.modes': ['ansi']}
    
    def __init__(self, small = True):
        # Initialize configurations, possible viewers and state
        self.agents = None
        self.round = None
        self.closed = False
        self.initdata = {}
        self._seed = None
        self.display = []
        self.viewer = None
        self.small = small
        
        self.score_type = {
            'pass' : 0,
            'single' : 1,
            'pair' : 2,
            'triple' : 4,
            'triple_with_single' : 4,
            'triple_with_pair' : 4,
            'straight' : 6,
            'pair_straight' : 6,
            'airplane' : 8,
            'airplane_with_single' : 8,
            'airplane_with_pair' : 8,
            'four_with_single' : 8,
            'four_with_pair' : 8,
            'bomb' : 10,
            'space_shuttle' : 10,
            'space_shuttle_with_single' : 10,
            'space_shuttle_with_pair' : 10,
            'rocket' : 16
        }
    
    @property
    def player_num(self):
        return 3
    
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
        if 'seed' in initdata:
            self.seed(initdata['seed'])
        if self._seed:
            random.seed(self._seed)
        if 'allocation' in initdata:
            self.allocation = initdata['allocation']
        else:
            allo = list(range(54))
            random.shuffle(allo)
            self.allocation = [allo[:20], allo[20 : -17], allo[-17 : ]]
        if 'publiccard' in initdata:
            self.publiccard = initdata['publiccard']
        else:
            self.publiccard = self.allocation[0][ : 3]
        self.initdata = dict(allocation = self.allocation, publiccard = self.publiccard)
        self.display = [self.initdata]
        if self.viewer: self.viewer.reset(self.initdata)
        self.hand = deepcopy(self.allocation)
        self.score = [0, 0, 0]
        self.history = [[], []]
        self.to_beat = None
    
    def step(self):
        if self.closed:
            raise AlreadyClosed()
        if self.round is None:
            raise ResetNeeded()
        
        cur = self.round % 3
        # provide request
        if self.round < 3:
            request = dict(own = self.allocation[cur], publiccard = self.publiccard, history = self.history)
        else:
            request = dict(history = self.history)
        # deep copy for safety
        action = deepcopy(self.agents[cur].step(deepcopy(request)))
        self.round += 1
        try:
            t = self._check_poker_type(action)
            if t[0] == 'pass':
                # check whether he can pass
                if not (self.history[0] or self.history[1]):
                    raise Error('INVALID_PASS')
                if not self.history[1]:
                    self.to_beat = None
            else:
                # check validity of each card
                for card in action:
                    if card not in self.allocation[cur]:
                        raise Error('MISSING_CARD')
                    if card not in self.hand[cur]:
                        raise Error('REPEATED_CARD')
                self.hand[cur] = list(set(self.hand[cur]) - set(action))
                # check beat
                if self.to_beat:
                    if t[0] == 'rocket':
                        pass
                    elif t[0] == 'bomb':
                        if self.to_beat[0] == 'rocket' or self.to_beat[0] == 'bomb' and t[2] <= self.to_beat[2]:
                            raise Error('LESS_COMPARE')
                    else:
                        if t[0] != self.to_beat[0]:
                            raise Error('MISMATCH_CARDTYPE')
                        if t[1] != self.to_beat[1]:
                            raise Error('MISMATCH_CARDLENGTH')
                        if t[2] <= self.to_beat[2]:
                            raise Error('LESS_COMPARE')
                self.to_beat = t
            self.score[cur] += self.score_type[t[0]]
            self.history.pop(0)
            self.history.append(action)
            # check episode ends
            if not self.hand[cur]:
                score = [0, 2, 2] if cur else [2, 0, 0]
                if self.small:
                    for i in range(3): score[i] += self.score[i] / 100
                score[1] = score[2] = (score[1] + score[2]) / 2
                self.display.append({
                    '0': score[0], '1': score[1], '2': score[2],
                    'event': {'player': cur, 'action': action}
                })
                self.round = None
                return tuple(score)
        except Error as e:
            score = (2.5, -1, -1) if cur else (-1, 2.5, 2.5)
            self.display.append({
                '0': score[0], '1': score[1], '2': score[2],
                'event': {'player': cur, 'action': []},
                'errorInfo': e.args[0]
            })
            self.round = None
            return score
        self.display.append({'event': {'player': cur, 'action': action}})
    
    def render(self, mode = 'ansi'):
        if mode == 'ansi':
            if self.viewer is None:
                self.viewer = FightTheLandlordTextViewer()
                self.viewer.reset(self.initdata)
            self.viewer.render(self.display)
            self.display = []
        else:
            super(FightTheLandlordEnv, self).render(mode)
    
    def close(self):
        self.closed = True
    
    def _check_poker_type(self, cards):
        # check validity
        if not isinstance(cards, list): raise Error('INVALID_INPUT')
        for i in cards:
            if not isinstance(i, int): raise Error('BAD_FORMAT')
            if not 0 <= i < 54: raise Error('OUT_OF_RANGE')
        # check type
        l = len(cards)
        if l == 0:
            return 'pass', l
        d = defaultdict(int)
        for i in cards:
            d[i // 4 if i < 53 else 14] += 1
        cnt = sorted(d.values(), reverse = True) # key pattern
        pattern = sorted(d.items(), key = lambda item: (item[1], item[0]), reverse = True) # pattern
        main = pattern[0][0] # main card
        if cnt == [1]:
            return 'single', l, main
        if cnt == [2]:
            return 'pair', l, main
        if cnt == [3]:
            return 'triple', l, main
        if cnt == [3, 1]:
            return 'triple_with_single', l, main
        if cnt == [3, 2]:
            return 'triple_with_pair', l, main
        if cnt == [4]:
            return 'bomb', l, main
        if cnt == [4, 1, 1]:
            return 'four_with_single', l, main
        if cnt == [4, 2, 2]:
            return 'four_with_pair', l, main
        lcnt = len(cnt)
        points = sorted(d.keys(), reverse = True) # card points
        if points == [14, 13]:
            return 'rocket', l, main
        if cnt[0] == cnt[-1] == 1 and lcnt >= 5 and points[0] - points[-1] == l - 1 and main <= 11:
            return 'straight', l, main
        if cnt[0] == cnt[-1] == 2 and lcnt >= 3 and points[0] - points[-1] == lcnt - 1 and main <= 11:
            return 'pair_straight', l, main
        if cnt[0] == cnt[-1] == 3 and points[0] - points[-1] == lcnt - 1 and main <= 11:
            return 'airplane', l, main
        if cnt[0] == cnt[-1] == 4 and points[0] - points[-1] == lcnt - 1 and main <= 11:
            return 'space_shuttle', l, main
        if lcnt % 2 == 0 and lcnt >= 4 and main <= 11:
            lcnt //= 2
            if main - pattern[lcnt - 1][0] == lcnt - 1:
                if cnt[0] == cnt[lcnt - 1] == 3:
                    if cnt[lcnt] == cnt[-1] == 1:
                        return 'airplane_with_single', l, main
                    if cnt[lcnt] == cnt[-1] == 2:
                        return 'airplane_with_pair', l, main
                if cnt[0] == cnt[lcnt - 1] == 4:
                    if cnt[lcnt] == cnt[-1] == 1:
                        return 'space_shuttle_with_single', l, main
                    if cnt[lcnt] == cnt[-1] == 2:
                        return 'space_shuttle_with_pair', l, main
        raise Error('INVALID_CARDTYPE')
