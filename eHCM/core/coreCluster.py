'''
Created on 01.12.2021

@author: uschoen
'''


__version__='0.9'
__author__ = 'ullrich schoen'

# Standard library imports
import logging
import os
from datetime import datetime
import time

# Local application imports
from .exception import defaultEXC


LOG=logging.getLogger(__name__)

class coreCluster():
    '''
    core events function
    '''
    def __init__(self,*args):
        
        
        self.coreClusterClients={}
        
        LOG.info("init core cluster finish, version %s"%(__version__))
    
    def updateRemoteCore(self,
                         forceUpdate,
                         objectID,
                         calling,
                         *args):
        pass
    
    def _loadClusterConfiguration(self,fileNameABS=None):
        '''
        load thecluster configuaion to a file
        '''
        try:
            if not self.ifFileExists(fileNameABS):
                if not self.ifPathExists(os.path.dirname(fileNameABS)):
                    self.makeDir(os.path.dirname(fileNameABS))
                LOG.info("create new file %s"%(fileNameABS))
                self.writeJSON(fileNameABS,{"version": __version__,"from":int(time.time())})
            LOG.info("load cluster configuration %s"%(fileNameABS))
            CFGFile={
                "version":"UNKOWN",
                "from":0
                }
            CFGFile.update(self.loadJSON(fileNameABS))
            LOG.info("cluster configuration file has version: %s from %s"%(CFGFile['version'],datetime.fromtimestamp(CFGFile['from'])))
            del(CFGFile['version'])
            del(CFGFile['from'])
            if len(CFGFile)==0:
                LOG.info("cluster configuration file is empty")
                return
            
            for coreName in CFGFile:
                try:
                    self.__restoreCoreConnector(coreName, CFGFile[coreName])
                except:
                    LOG.error("can't restore cluster  configuration %s"%(coreName),exc_info=True)
        except:
            raise defaultEXC ("can't loadClusterConfiguration")