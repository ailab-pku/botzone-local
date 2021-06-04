from rich import box
from rich import print as rprint
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from botzone.online.viewer.viewer import TextViewer

class FightTheLandlord2TextViewer(TextViewer):
    '''
    First 1~3 round: {allocation: list of 3*17, publiccard: list of 3, bid: list of 0~2}
    Other rounds: {
        0, 1, 2: score in the last round
        event: {player: 0..2, action: list}
        landlord: int
        bid: list of 1~3
        errored: list of errorinfo of {
            INVALID_INPUT_VERDICT_*: Agent failure!
            BAD_FORMAT: Bad format!
            INVALID_CARDTYPE: Invalid card type!
            INVALID_PASS: Invalid pass!
            MISMATCH_CARDTYPE: Card type mismatch!
            MISMATCH_CARDLENGTH: Card length mismatch!
            LESS_COMPARE: Smaller card!
            MISSING_CARD: Fake card!
            OUT_OF_RANGE: Invalid card!
            REPEATED_CARD: Repeated card!
            INVALID_BID: Invalid bid!
        }
    }
    '''
    
    def __init__(self):
        self.draw = [suit + num for num in ['3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A', '2'] for suit in '♥♦♠♣']
        self.draw.extend(['JOKER', 'JOKER'])
        self.draw = ['\n'.join(s.ljust(5)) for s in self.draw]
        for i in range(52):
            if i % 4 < 2:
                self.draw[i] = Text(self.draw[i], style = 'red')
        self.draw[-1] = Text(self.draw[-1], style = 'red')
        self.errMsg = dict(
            BAD_FORMAT = 'Bad format!',
            INVALID_CARDTYPE = 'Invalid card type!',
            INVALID_PASS = 'Invalid pass!',
            MISMATCH_CARDTYPE = 'Card type mismatch!',
            MISMATCH_CARDLENGTH = 'Card length mismatch!',
            LESS_COMPARE = 'Smaller card!',
            MISSING_CARD = 'Fake card!',
            OUT_OF_RANGE = 'Invalid card!',
            REPEATED_CARD = 'Repeated card!',
            INVALID_BID = 'Invalid bid!'
        )
        self.defaultErrMsg = 'Agent failure!'
    
    def reset(self, initdata = None):
        self.round = -1
    
    def render(self, displays, bootstrap = True):
        # Recover state
        display = {}
        cur = -2
        for display in displays:
            self.round += 1
            if self.round == 0:
                # First round
                self.hand = display['allocation']
                self.publiccard = display['publiccard']
                self.history = [None, None, None]
                self.errored = [None] * 3
                self.landlord = -1
                self.bid = []
                for h in self.hand: h.sort()
            else:
                if 'bid' in display: self.bid = display['bid']
                if 'allocation' not in display:
                    if 'errored' in display: self.errored = display['errored']
                    if self.round == len(self.bid):
                        # Bidding just over
                        self.landlord = display['landlord']
                        self.hand[self.landlord].extend(self.publiccard)
                        self.hand[self.landlord].sort()
                    elif 'event' in display:
                        cur = display['event']['player']
                        action = display['event']['action']
                        self.hand[cur] = [x for x in self.hand[cur] if x not in action]
                        self.history[cur] = action
        # Render
        msg = ['\nPlayer %d%s\n\n%s\n\n%d left' % (
            i,
            '\n[Robot] ' + self._get_err_msg(self.errored[i]) if self.errored[i] else '',
            'Unknown' if self.landlord == -1 else 'Landlord' if i == self.landlord else 'Peasant',
            len(self.hand[i])) for i in range(3)
        ]
        if '0' in display:
            for i in range(3):
                msg[i] += '\n\nScore: %f' % display[str(i)]
        if self.round == len(self.bid):
            status = ['\nBid %d points' % x for x in self.bid]
            while len(status) < 3: status.append('')
        else:
            status = []
            for i in range(3):
                if '0' not in display and i == (cur + 1) % 3:
                    status.append('\nNext')
                elif self.history[i] is None:
                    status.append('')
                elif isinstance(self.history[i], str):
                    status.append(self.history[i])
                elif self.history[i]:
                    status.append(self._get_cards_draw(self.history[i]))
                else:
                    status.append('\nPass')
        table = Table(show_header = False, show_lines = True, box = box.SQUARE)
        for i in range(3):
            table.add_row(msg[i], self._get_cards_draw(self.hand[i]), status[i])
        print('Round:', self.round)
        rprint(table)
    
    def _get_err_msg(self, errorInfo):
        return self.errMsg.get(errorInfo, self.defaultErrMsg)
    
    def _get_cards_draw(self, cards):
        if not cards: return ''
        table = Table(show_header = False, padding = 0, style = 'black on white', box = box.SQUARE)
        table.add_row(*(self.draw[card] for card in cards))
        table.add_row(*(Text(' ', style = 'on red') if card in self.publiccard else ' ' for card in cards))
        table.columns[-1].min_width = 6
        return table