import execjs
import json
import os

from botzone import Agent
from botzone.error import *
from botzone.online.api import BotzoneAPI
from botzone.online.game import GameConfig
from botzone.online.sandbox import SandBox

class BotConfig:
    '''
    Config of a bot. If you want to use an online bot, call fromID() to download
    config from botzone. If you want to test a local bot that has not been
    uploaded yet, contruct config yourself.
    '''

    @classmethod
    def fromID(cls, ver_id, path = None, force_download = False
        , userfile = False, userfile_path = None):
        '''
        Download bot config and (optionally) code & userfile from botzone. If no
        code & userfile cache is found, you may be asked to login to an account
        accessible to code & userfile.
        
        Parameters:
            ver_id - Bot ID copied from botzone
            path - Target folder to download code. Default folder is `bot/`
            relative to this file.
            force_download - If set to False, cached code & userfile (if exists)
            in target folder will be used. Default is False.
            userfile - Whether the bot uses userfile in `/data`. Default is
            False.
            userfile_path - Target folder to download userfile. Default folder
            is `bot/({user_id}/)` relative to this file.
        '''
        if path is None:
            path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bot')
        else:
            assert os.path.isdir(path)
        if userfile:
            if userfile_path is None:
                userfile_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bot')
            else:
                assert os.path.isdir(userfile_path)
        # Download config if no cache
        config_path = os.path.join(path, ver_id + '.conf')
        if os.path.exists(config_path):
            with open(config_path) as f:
                bot = json.load(f)
        else:
            bot = BotzoneAPI.get_bot(ver_id)
            with open(config_path, 'w') as f:
                json.dump(bot, f)
        ver = bot['ver']
        user_id = bot['user']['_id']
        bot = bot['bot']
        game = GameConfig.fromID(bot['game'])
        extension = bot['extension']
        simpleio = bot['simpleio']
        keep_running = bot['enable_keep_running']
        # Download bot if no cache
        path = os.path.join(path, ver_id + '.' + extension)
        if force_download or not os.path.exists(path):
            while not BotzoneAPI.download_bot(bot['_id'], ver, path):
                # not login, ask user
                print('You need to login to download this bot, type y to login')
                if input() != 'y':
                    raise RuntimeError('User canceled login')
                while not BotzoneAPI.login():
                    print('Log in failed, try again.')
        # Download userfile if no cache
        if userfile:
            if force_download or not os.path.exists(os.path.join(userfile_path, user_id)):
                while not BotzoneAPI.download_userfile(user_id, userfile_path):
                    # not login, ask user
                    print('You need to login to download userfile, type y to login')
                    if input() != 'y':
                        raise RuntimeError('User canceled login')
                    while not BotzoneAPI.login():
                        print('Log in failed, try again.')
            userfile_path = os.path.join(userfile_path, user_id)
        return cls(game, path, extension, simpleio = simpleio, keep_running = keep_running, userfile_path = userfile_path if userfile else None)

    def __init__(self, game, path, extension, simpleio = False, keep_running = False, userfile_path = None):
        '''
        Create your own bot config.
        
        Parameters:
            game - GameConfig used by this bot. See botzone.online.game.GameConfig
            for more details.
            path - Path to store code of this bot.
            extension - Compiler of this bot. See botzone.online.compiler.config
            for more details.
            simpleio - Whether to use simple io. The game must support simpleio
            and NodeJS is required to be installed.
            keep_running - Whether to allow keep-running.
            userfile_path - Local folder to store userfile used by this bot.
            If bot does not use userfile, set to None.
        '''
        self.game = game
        self.path = path
        self.extension = extension
        self.simpleio = simpleio
        if simpleio:
            assert game.support_simpleio, "Game %s does not support simpleio!" % game.name
            self.transform_code = game.transform_code
        self.keep_running = keep_running
        self.userfile_path = userfile_path

class Bot(Agent):
    '''
    This class provides a universal wrapper for bot online.
    '''

    def __init__(self, config):
        '''
        Create bot instance from BotConfig.
        
        Parameters:
            config - BotConfig instance.
        '''
        assert isinstance(config, BotConfig), 'Parameter config must be BotConfig instance!'
        self.config = config
        self.globaldata = None
        self.sandbox = sandbox = SandBox(config.path, config.extension)
        try:
            # create sandbox
            sandbox.create()
            # copy user file
            if config.userfile_path:
                sandbox.copy(config.userfile_path)
            # compile user code
            sandbox.compile()
        except:
            sandbox.close()
            raise
        # internal state
        self.requests = None
        self.requested_keep_running = False
        # retrieve globaldata if exists
        self.globaldata_path = os.path.splitext(config.path)[0] + '.globaldata'
        if os.path.exists(self.globaldata_path):
            with open(self.globaldata_path, 'rb') as f:
                self.globaldata = str(f.read(), encoding = 'utf-8')

    def reset(self):
        if self.sandbox is None:
            raise AlreadyClosed()
        if self.requested_keep_running:
            # Still running last episode, kill it
            self.sandbox.run_kill()
        self.requests = []
        self.responses = []
        self.requested_keep_running = False
        self.data = None

    def step(self, request):
        if self.sandbox is None:
            raise AlreadyClosed()
        if self.requests is None:
            raise ResetNeeded()
        self.requests.append(request)
        
        # construct input data
        if self.config.simpleio:
            if self.requested_keep_running:
                input = self.config.transform_code['request_from_json'](request)
            else:
                n = len(self.requests)
                input = [str(n)]
                for i in range(n - 1):
                    input.append(self.config.transform_code['request_from_json'](self.requests[i]))
                    input.append(self.responses[i])
                input.append(self.config.transform_code['request_from_json'](request))
                if self.data:
                    input.append(self.data)
                if self.globaldata:
                    input.append(self.globaldata)
                input = '\n'.join(input)
        else:
            if self.requested_keep_running:
                input = request
            else:
                input = dict(
                    requests = self.requests,
                    responses = self.responses
                )
                if self.data:
                    input['data'] = self.data
                if self.globaldata:
                    input['globaldata'] = self.globaldata
            input = json.dumps(input)
            
        output = self.sandbox.run(input, self.config.keep_running)

        # parse output from wrapper
        if output['keep_running']:
            self.requested_keep_running = True
        if output['verdict'] != 'OK':
            print('Bot:', output['verdict'], ', Log:')
            print(output)
            return None
        output = output['output']
        # parse output from user program: response+debug+data+globaldata
        if self.config.simpleio:
            l = output.split('\n')
            response = l[0]
            if len(l) > 2:
                data = l[2]
            else:
                data = None
            if len(l) > 3:
                globaldata = '\n'.join(l[3:])
            else:
                globaldata = None
            # only save raw response
            self.responses.append(response)
            try:
                response = self.config.transform_code['response_to_json'](response)
            except:
                print('Bot: Malformed simpleio string, Log:')
                print(response)
                return None
        else:
            try:
                output = json.loads(output)
            except:
                print('Bot: Malformed Json, Log:')
                print(output)
                return None
            if isinstance(output, dict) and 'response' in output:
                response = output.get('response', None)
                data = output.get('data', None)
                globaldata = output.get('globaldata', None)
            else:
                response = output
                data = globaldata = None
            self.responses.append(response)
        self.data = data
        if globaldata:
            # only update globaldata when user really updates it
            self.globaldata = globaldata
        return response
    
    def close(self):
        if self.sandbox:
            self.sandbox.close()
            self.sandbox = None
        if self.globaldata:
            # store globaldata
            with open(self.globaldata_path, 'wb') as f:
                f.write(bytearray(self.globaldata, encoding = 'utf-8'))
            self.globaldata = None
