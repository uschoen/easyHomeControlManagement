'''
Created on 01.12.2018

@author: uschoen
'''


__version__='7.0'
__author__ = 'ullrich schoen'

# Standard library imports

import logging

LOG=logging.getLogger(__name__)

class localCoreException(Exception):
    def __init__(self, msg="unkown error occured",traceback=False):
        super(localCoreException, self).__init__(msg)
        self.msg = msg
        LOG.critical(msg,exc_info=traceback)

class encryptionException(Exception):
    def __init__(self, msg="unkown error occured",traceback=False):
        super(encryptionException, self).__init__(msg)
        self.msg = msg
        LOG.critical(msg,exc_info=traceback)
                    
class protocolException(Exception):
    def __init__(self, msg="unkown error occured",traceback=False):
        super(protocolException, self).__init__(msg)
        self.msg = msg
        LOG.critical(msg,exc_info=traceback)

class remoteCoreException(Exception):
    def __init__(self, msg="unkown error occured",traceback=False):
        super(remoteCoreException, self).__init__(msg)
        self.msg = msg
        LOG.critical(msg,exc_info=traceback)
       
