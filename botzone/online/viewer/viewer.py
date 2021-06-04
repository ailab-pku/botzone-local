class Viewer(object):
    
    def reset(self, initdata = None):
        raise NotImplementedError
    
    def render(self, displays, bootstrap):
        raise NotImplementedError

class TextViewer(Viewer):
    
    def reset(self, initdata = None):
        raise NotImplementedError
    
    def render(self, displays, bootstrap = True):
        raise NotImplementedError
    
    def make(name, *args, **kargs):
        if name == 'Reversi':
            from botzone.online.viewer.reversi import ReversiTextViewer
            return ReversiTextViewer(*args, **kargs)
        elif name == 'Minesweeper':
            from botzone.online.viewer.minesweeper import MineSweeperTextViewer
            return MineSweeperTextViewer(*args, **kargs)
        elif name == 'Gomoku':
            from botzone.online.viewer.gomoku import GomokuTextViewer
            return GomokuTextViewer(*args, **kargs)
        elif name == 'Renju':
            from botzone.online.viewer.renju import RenjuTextViewer
            return RenjuTextViewer(*args, **kargs)
        elif name == 'FightTheLandlord':
            from botzone.online.viewer.fightthelandlord import FightTheLandlordTextViewer
            return FightTheLandlordTextViewer(*args, **kargs)
        elif name == 'Snake':
            from botzone.online.viewer.snake import SnakeTextViewer
            return SnakeTextViewer(*args, **kargs)
        elif name == 'Ataxx':
            from botzone.online.viewer.ataxx import AtaxxTextViewer
            return AtaxxTextViewer(*args, **kargs)
        elif name == 'Amazons':
            from botzone.online.viewer.amazons import AmazonsTextViewer
            return AmazonsTextViewer(*args, **kargs)
        elif name == 'Go':
            from botzone.online.viewer.go import GoTextViewer
            return GoTextViewer(*args, **kargs)
        elif name == 'NoGo':
            from botzone.online.viewer.nogo import NoGoTextViewer
            return NoGoTextViewer(*args, **kargs)
        elif name == 'TicTacToe':
            from botzone.online.viewer.tictactoe import TicTacToeTextViewer
            return TicTacToeTextViewer(*args, **kargs)
        elif name == 'ChineseStandardMahjong':
            from botzone.online.viewer.chinesestandardmahjong import ChineseStandardMahjongTextViewer
            return ChineseStandardMahjongTextViewer(*args, **kargs)
        elif name == 'Kingz':
            from botzone.online.viewer.kingz import KingzTextViewer
            return KingzTextViewer(*args, **kargs)
        elif name == 'FightTheLandlord2':
            from botzone.online.viewer.fightthelandlord2 import FightTheLandlord2TextViewer
            return FightTheLandlord2TextViewer(*args, **kargs)
        return None