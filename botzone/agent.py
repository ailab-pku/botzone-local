class Agent(object):

    def reset(self):
        '''
        Called by Env when a new episode starts. The agent should initialize
        its internal state in this method.
        Note: this method can be called when last episode has NOT finished from
        this agent's perspective, and it should do necessary cleanup before
        preparing for new episode.
        
        Raises:
            AlreadyClosed - If close() is ever called.
        '''
        raise NotImplementedError

    def step(self, request):
        '''
        Called by Env when requested to make a decision.
        Note: if last episode has finished and step() is mistakenly called
        before reset(), a robust implementation is responsible to check for this
        situation and raise an `ResetNeeded` Error, e.g. by checking some
        internal state which is cleared whenever an episode is finished and is
        reset in reset().
        
        Parameters:
            request - Observation provided by Env
        
        Returns:
            Response by this agent.
        
        Raises:
            AlreadyClosed - If close() is ever called.
            ResetNeeded - If called before reset() when last episode has
            finished.
        '''
        raise NotImplementedError

    def close(self):
        '''
        Perform necessary cleanup. This method must be called before program
        exits as soon as Agent instance is successfully created. After close()
        is called, calling reset() or step() will always raise an AlreadyClosed
        Error. Multiple calls of close() are possible and should not raise
        Errors.
        '''
        pass
