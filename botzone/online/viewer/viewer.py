class Viewer(object):
    
    def reset(self):
        raise NotImplementedError
    
    def render(self, displays, bootstrap):
        raise NotImplementedError

class TextViewer(Viewer):
    
    def reset(self):
        raise NotImplementedError
    
    def render(self, displays, bootstrap = True):
        raise NotImplementedError
    
    def make(name, *args, **kargs):
        if name == 'Reversi':
            from botzone.online.viewer.reversi import ReversiTextViewer
            return ReversiTextViewer(*args, **kargs)
        return None