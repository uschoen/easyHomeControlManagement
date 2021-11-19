'''
Created on 01.12.2018

@author: uschoen
'''

__version__='6.0'
__author__ = 'ullrich schoen'

# Standard library imports
import logging

# Local application imports


LOG=logging.getLogger(__name__)



class version2:
    def __init__(self,cfg,core):
        self.__core=core
        
        LOG.info("init protokol version2 finish, version %s"%(__version__))
    
    def reciveData(self,networkSocket,remoteCoreIP):
        try:
            pass
        except:
            pass
    
    def sendJob(self,job):
        try:
            pass
        except:
            pass