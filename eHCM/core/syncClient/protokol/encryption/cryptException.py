'''
Created on 01.12.2018

@author: uschoen
'''


__version__='6.0'
__author__ = 'ullrich schoen'

# Standard library imports

import logging

LOG=logging.getLogger(__name__)
      
              
class cryptException(Exception):
    def __init__(self, msg="unkown error occured",traceback=False):
        super(cryptException, self).__init__(msg)
        LOG.critical(msg,exc_info=traceback)
