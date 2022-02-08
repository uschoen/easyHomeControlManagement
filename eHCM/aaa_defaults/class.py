'''
Created on 01.12.2021

@author: uschoen
'''

__version__='0.9'
__author__ = 'ullrich schoen'

# Standard library imports
import logging

# Local application imports
from .exception import defaultEXC


LOG=logging.getLogger(__name__) 

def CLASSNAME(self,objectID,var_2,forceUpdate=False):
        '''
        update a Core connector
        
        objectID:      core objectID
        ...
        forceUpdate:    true/false(default) force update remote core
        
        return
        
        exception: clusterException
        '''
        try:
            pass
            self.updateRemoteCore(forceUpdate,objectID,self.thisMethode,objectID,var 2)
        except:
            raise defaultEXC("some unkown error in %s"%(self.thisMethode))

def CLASSNAME(self,objectID,var_2,forceUpdate=False):
        '''
        update a Core connector
        
        objectID:      core objectID
        ...
        forceUpdate:    true/false(default) force update remote core
        
        return
        
        exception: clusterException
        '''
        try:
            if self.ifonThisHost(objectID):
                '''
                job only for this host
                ''' 
            self.updateRemoteCore(forceUpdate,objectID,self.thisMethode,objectID,var 2)
        except:
            raise defaultEXC("some unkown error in %s"%(self.thisMethode))