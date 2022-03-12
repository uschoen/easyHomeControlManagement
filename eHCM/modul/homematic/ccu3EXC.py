'''
Created on 01.12.2021

@author: uschoen
'''


__version__='0.9'
__author__ = 'ullrich schoen'

# Standard library imports

import logging

LOG=logging.getLogger(__name__)

class ccu3xmlEXC(Exception):
    '''
    
    '''
    def __init__(self, msg="unkown error occured",tracback=False):
        super(ccu3xmlEXC, self).__init__(msg)
        self.msg = msg
        LOG.critical(msg,exc_info=tracback)
        
class ccu3EXC(Exception):
    '''
    
    '''
    def __init__(self, msg="unkown error occured",tracback=False):
        super(ccu3EXC, self).__init__(msg)
        self.msg = msg
        LOG.critical(msg,exc_info=tracback)   

class ccu3RPCserverEXC(Exception):
    '''
    
    '''
    def __init__(self, msg="unkown error occured",tracback=False):
        super(ccu3RPCserverEXC, self).__init__(msg)
        self.msg = msg
        LOG.critical(msg,exc_info=tracback)       
        
class ccu3RPCEXC(Exception):
    '''
    
    '''
    def __init__(self, msg="unkown error occured",tracback=False):
        super(ccu3RPCEXC, self).__init__(msg)
        self.msg = msg
        LOG.critical(msg,exc_info=tracback)       