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
            from botzone.online.viewer.minesweeper import MineSweeperViewer
            return MineSweeperTextViewer(*args, **kargs)
        elif name == 'Gomoku':
            from botzone.online.viewer.gomoku import GomokuTextViewer
            return GomokuTextViewer(*args, **kargs)
        elif name == 'Renju':
            from botzone.online.viewer.renju import RenjuTextViewer
            return RenjuTextViewer(*args, **kargs)
        return None