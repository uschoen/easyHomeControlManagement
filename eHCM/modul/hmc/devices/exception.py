'''
Created on 01.12.2021

@author: uschoen
'''


__version__='0.9'
__author__ = 'ullrich schoen'

# Standard library imports

import logging

LOG=logging.getLogger(__name__)


    

class deviceEXC(Exception):   
    def __init__(self, msg="unkown error occured",tracback=False):
        super(deviceEXC, self).__init__(msg)
        self.msg = msg
        LOG.critical(msg,exc_info=tracback)
        