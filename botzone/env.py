from botzone.agent import Agent
from botzone.error import *

class Env(object):

    @property
    def player_num(self):
        '''
        Number of players of this game.
        
        Returns:
            A constant indicating number of players needed.
        '''
        raise NotImplementedError

    def init(self, agents):
        '''
        Initialize agents used by this environment.
        
        Parameters:
            agents - A list of botzone.Agent instances.
        '''
        assert isinstance(agents, list), 'Parameter `agents` must be a list!'
        assert len(agents) == self.player_num, '%d agents expected but %d given!' % (self.player_num, len(agents))
        for agent in agents:
            assert issubclass(type(agent), Agent), 'Parameter `agents` must be a list of botzone.Agent instances!'
        self.agents = agents

    def reset(self, initdata = None):
        '''
        Prepare for a new episode. The env should initialize its internal state
        in this method. In trivial cases where the episode ends at once, return
        scores of each agent.
        Note: this method can be called when last episode has NOT finished, and
        it should do necessary cleanup before preparing for new episode.
        
        Parameters:
            initdata - Data needed to initialize an episode, e.g. some initial
            configuration of the environment.
        
        Returns:
            A tuple contains the score of each agent if the episode ends
            immediately, or None otherwise.
        
        Raises:
            AlreadyClosed - If close() is ever called.
            AgentsNeeded - If init() is never called.
        '''
        raise NotImplementedError

    def step(self):
        '''
        One step of the environment. In this method the env will call some of
        the agents to request a response, and return scores of each agent if
        this episode ends.
        Note: if last episode has finished and step() is mistakenly called
        before reset(), a robust implementation is responsible to check for this
        situation and raise an `ResetNeeded` Error, e.g. by checking some
        internal state which is cleared whenever an episode is finished and is
        reset in reset().
        
        Returns:
            A tuple contains the score of each agent if the episode ends, or
            None otherwise.
        
        Raises:
            AlreadyClosed - If close() is ever called.
            ResetNeeded - If called before reset() when last episode has
            finished.
        '''
        raise NotImplementedError

    def render(self, mode = 'human'):
        '''
        Render current state. This method can be called any time after reset()
        and before close(), rendering states updated by last call of step().
        Note: Even if an episode has finished, render() should still be able to
        render the states by not clearing states needed when episode ends.
        
        Parameters:
            mode - Render mode used. Modes supported should be specified in
            Env.metadata['render.modes'].
        
        Raises:
            AlreadyClosed - If close() is ever called.
            UnsupportedMode - If mode is not supported.
        
        Example:
        
        class MyEnv(Env):
            metadata = {'render.modes': ['human', 'ansi']}
            
            def render(self, mode = 'human'):
                if mode == 'human':
                    ... # render by a popup window
                elif mode == 'ansi':
                    ... # render by printing a terminal-style text
                else:
                    super(MyEnv, self).render(mode)
        '''
        raise UnsupportedMode()

    def close(self):
        '''
        Perform necessary cleanup. This method must be called before program
        exits as soon as Env instance is successfully created. After close() is
        called, calling reset(), step() or render() will always raise an
        AlreadyClosed Error. Multiple calls of close() are possible and should
        not raise Errors.
        Note: this method will NOT call close() of each agent. The user must
        close agents on their own.
        '''
        pass
    
    def seed(self, seed = None):
        '''
        Sets the seed for this env's random number generator. Override this
        method if environment contains no randomness.
        
        Parameters:
            seed - Seed specified.
        '''
        if seed is not None: assert isinstance(seed, int) and seed >= 0, 'Seed must be a non-negative integer or omitted'
        self._seed = seed

    def __enter__(self):
        '''Support with-statement for the environment.'''
        return self

    def __exit__(self, *args):
        '''Support with-statement for the environment.'''
        self.close()
        return False
