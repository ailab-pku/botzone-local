class Error(Exception):
    pass

class ResetNeeded(Error):
    '''
    Raised when user tries to step an environment or an agent after an episode
    has finished.
    '''
    pass

class AlreadyClosed(Error):
    '''
    Raised when user tries to operate an environment or an agent after calling
    close().
    '''
    pass

class AgentsNeeded(Error):
    '''
    Raised when user tries to reset or step an environment before specifying
    agents used.
    '''
    pass

class UnsupportedMode(Error):
    '''
    Raised when user requests a rendering mode not supported by the environment.
    '''
    pass