from copy import deepcopy
import importlib

from botzone.error import Error

def load(name):
    mod_name, attr_name = name.split(':')
    mod = importlib.import_module(mod_name)
    fn = getattr(mod, attr_name)
    return fn

class EnvSpec:
    '''
    A specification for a particular instance of the environment.
    
    Args:
        id: environment ID
        entry_point: Python entry point of the environment class (module:class)
        kwargs: dict of kwargs to pass to environment class
    '''
    
    def __init__(self, id, entry_point = None, **kwargs):
        self.id = id
        self.entry_point = entry_point
        self.kwargs = kwargs
        if id.find('-') == -1:
            raise Error('Wrong format of Env ID!')
        self.name, *ver = id.split('-')
        self.ver = '-'.join(ver)
    
    def make(self, **kwargs):
        if self.ver == 'wrap':
            # For wrapper env in Online Botzone
            from botzone.online.game import GameConfig, Game
            env = Game(GameConfig.fromName(self.name))
            return env
        if self.entry_point is None:
            raise Error('No entry point for deprecated Env %s' % self.id)
        newkwargs = self.kwargs.copy()
        newkwargs.update(kwargs)
        if callable(self.entry_point):
            env = self.entry_point(**newkwargs)
        else:
            cls = load(self.entry_point)
            env = cls(**newkwargs)
        spec = deepcopy(self)
        spec.kwargs = newkwargs
        env.spec = spec
        return env
    
    def __repr__(self):
        return 'EnvSpec(%s)' % self.id

class EnvRegistry:
    '''
    Register an env by ID.
    '''
    
    def __init__(self):
        self.env_specs = {}
    
    def register(self, id, **kwargs):
        if id in self.env_specs:
            raise Error('Cannot re-register id: %s' % id)
        self.env_specs[id] = EnvSpec(id, **kwargs)
    
    def make(self, id, **kwargs):
        if id not in self.env_specs:
            raise Error('Env id %s not found!' % id)
        spec = self.env_specs[id]
        return spec.make(**kwargs)
    
    def all(self):
        return self.env_specs.values()

# Global registry
registry = EnvRegistry()

def register(id, **kwargs):
    return registry.register(id, **kwargs)

def make(id, **kwargs):
    return registry.make(id, **kwargs)

def all():
    return registry.all()
