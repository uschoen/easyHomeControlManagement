'''
Created on 01.12.2021

@author: uschoen
'''


__version__='9.0'
__author__ = 'ullrich schoen'

# Standard library imports

import logging
from core.exception import defaultEXC

LOG=logging.getLogger(__name__)

class defaultError(defaultEXC):
    '''
    
    '''
    pass

class cmdError(defaultEXC):
    '''
    
    '''
    pass

class testError(defaultEXC):
    '''
    
    '''
    pass