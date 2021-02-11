from copy import deepcopy
import execjs
import json
import os

from botzone import Env
from botzone.error import *
from botzone.online import games
from botzone.online.viewer.viewer import *
from botzone.online.sandbox import SandBox

class GameConfig:
    '''
    Config of a game. If you want to use an existing game, call fromName() or
    fromID(). If you want to test a local game that is about to upload to
    botzone, contruct config yourself.
    '''

    @classmethod
    def fromName(cls, name):
        '''
        Construct GameConfig from name.
        
        Parameters:
            name - Name of the game.
        
        Raises：
            RuntimeError - If game not found.
        '''
        params = games.get_by_name(name)
        if not params:
            raise RuntimeError('Game %s not found!' % name)
        return cls(**params)

    @classmethod
    def fromID(cls, id):
        '''
        Construct GameConfig from ID.
        
        Parameters:
            id - ID of the game.
        
        Raises：
            RuntimeError - If game not found.
        '''
        params = games.get_by_id(id)
        if not params:
            raise RuntimeError('Game with ID %s not found!' % name)
        return cls(**params)

    def __init__(self, name, player, extension, keep_running, transform_code, judge_path = None, player_path = None, title = None):
        '''
        Create your own game config.
        
        Parameters:
            name - Name of the game.
            player - Number of players of the game.
            extension - Compiler of the judge program. See botzone.online.compiler.config
            for more details.
            keep_running - Whether to allow keep-running of the judge program.
            transform_code - A dict of form: {
                'supported' : Boolean, # False if not support simple_io
                'request_from_json': code snippet,
                'response_to_json': code snippet,
                'response_from_json': code snippet,
            }
            judge_path - Path to store judge program of this bot.
            player_path - Path to store gameplayer of this bot. Currently
            unsupported.
            title - Title of the game.
        '''
        self.name = name
        self.title = title
        self.player = player
        self.extension = extension
        self.keep_running = keep_running
        self.support_simpleio = transform_code['supported']
        if self.support_simpleio:
            try:
                node = execjs.get(execjs.runtime_names.Node)
            except:
                raise RuntimeError('NodeJS required to support simple_io, please install NodeJS first.')
            js_code = '''
                request_from_json = function(request){%s};
                response_to_json = function(response){%s};
                response_from_json = function(response){%s};
            ''' % (transform_code["request_from_json"]
                   , transform_code["response_to_json"]
                   , transform_code["response_from_json"]
            )
            context = node.compile(js_code)
            self.transform_code = dict(
                request_from_json = lambda request: context.call("request_from_json", request),
                response_to_json = lambda response: context.call("response_to_json", response),
                response_from_json = lambda response: context.call("response_from_json", response)
            )
        if judge_path is None:
            judge_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'game', name + '.' + extension)
        self.judge_path = judge_path
        if player_path is None:
            player_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'game', name + '.html')
        self.player_path = player_path

class Game(Env):
    '''
    This class provides a universal wrapper for games online.
    '''
    
    metadata = {'render.modes' : ['ansi']}
    
    def __init__(self, config):
        '''
        Create game instance from GameConfig.
        
        Parameters:
            config - GameConfig instance.
        '''
        self.agents = None
        assert isinstance(config, GameConfig), 'Parameter config must be GameConfig instance!'
        self.config = config
        self.sandbox = sandbox = SandBox(config.judge_path, config.extension)
        try:
            # create sandbox
            sandbox.create()
            # compile judge
            sandbox.compile()
        except:
            sandbox.close()
            raise
        # internal state
        self.log = None
        self.requested_keep_running = False
        self.display = []
        self.viewer = None

    @property
    def player_num(self):
        return self.config.player

    def reset(self, initdata = ''):
        if self.sandbox is None:
            raise AlreadyClosed()
        if self.agents is None:
            raise AgentsNeeded()
        # Initialize each agent
        for agent in self.agents:
            agent.reset()

        if self.requested_keep_running:
            # Still running last episode, kill it
            self.sandbox.run_kill()
            
        # Run judge for the first time
        self.requested_keep_running = False
        if initdata is None: initdata = ''
        input = dict(log = [], initdata = initdata)
        input = json.dumps(input)
        output = self.sandbox.run(input, self.config.keep_running)
        self.log = [output]
        self.display = []
        
        # parse output from wrapper
        if output['keep_running']:
            self.requested_keep_running = True
        if output['verdict'] != 'OK':
            print('Judge:', output['verdict'], ', Log:')
            print(output)
            raise RuntimeError('Unexpected judge failure')
        response = output['output']
        try:
            response = json.loads(response)
        except:
            print('Judge: Malformed Json, Log:')
            print(response)
            raise RuntimeError('Unexpected judge failure')
        output['output'] = response

        # parse output from judge: command+content+display+initdata
        self.display.append(response.get('display', None))
        if response['command'] == 'finish':
            # game over, return score
            self.log = None
            return tuple(response['content'][str(i)] for i in range(self.config.player))
        if response['command'] != 'request':
            print('Judge: Unrecognized command, Log:')
            print(response)
            raise RuntimeError('Unexpected judge failure')
        if 'initdata' in response:
            # initdata from judge override original one
            self.initdata = response['initdata']
        else:
            self.initdata = initdata
            
        if self.viewer: self.viewer.reset(self.initdata)

    def step(self):
        if self.sandbox is None:
            raise AlreadyClosed()
        if self.log is None:
            raise ResetNeeded()

        # run each agent
        responses = {}
        for i, request in self.log[-1]['output']['content'].items():
            # deepcopy for safety
            response = deepcopy(self.agents[int(i)].step(deepcopy(request)))
            responses[i] = dict(verdict = 'OK' if response is not None else 'ERR', response = response)
        self.log.append(responses)

        # run judge
        if self.requested_keep_running:
            input = responses
        else:
            input = dict(log = self.log, initdata = self.initdata)
        input = json.dumps(input)
        output = self.sandbox.run(input, self.config.keep_running)
        self.log.append(output)
        
        # parse output from wrapper
        if output['keep_running']:
            self.requested_keep_running = True
        if output['verdict'] != 'OK':
            print('Judge:', output['verdict'], ', Log:')
            print(output)
            raise RuntimeError('Unexpected judge failure')
        response = output['output']
        try:
            response = json.loads(response)
        except:
            print('Judge: Malformed Json, Log:')
            print(response)
            raise RuntimeError('Unexpected judge failure')
        output['output'] = response

        # parse output from judge: command+content+display+initdata
        self.display.append(response.get('display', None))
        if response['command'] == 'finish':
            # game over, return score
            self.log = None
            return tuple(response['content'][str(i)] for i in range(self.config.player))
        if response['command'] != 'request':
            print('Judge: Unrecognized command, Log:')
            print(response)
            raise RuntimeError('Unexpected judge failure')

    def close(self):
        if self.sandbox:
            self.sandbox.close()
            self.sandbox = None

    def render(self, mode = 'ansi'):
        if mode == 'ansi':
            if self.viewer is None:
                self.viewer = TextViewer.make(self.config.name)
                if self.viewer: self.viewer.reset(self.initdata)
            if self.viewer:
                self.viewer.render(self.display)
                self.display = []
            else:
                print(self.display[-1])
        else:
            super(Game, self).render(mode)
