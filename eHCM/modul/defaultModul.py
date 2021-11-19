'''
Created on 01.12.2021

@author: uschoen

default modul

'''


__version__='0.9'
__author__ = 'ullrich schoen'

# Standard library imports
import threading
import logging
import time

# Local apllication constant
from core.exception import defaultEXC
from core.manager import manager as coreManager

LOG=logging.getLogger(__name__)

class defaultModul(threading.Thread):
    '''
    object um eine verbindung zu einem remote core aufzubauen 
    um remote command zu uebermitteln.
    '''
    
    def __init__(self,objectID,modulCFG):
        '''
        Constructor
        '''
        threading.Thread.__init__(self)
        
        """ core instance """
        self.core=coreManager()
        
        """ default config """
        self.config={
                        'enable':False,
                        'objectID':objectID
                      }
        self.config.update(modulCFG)
        self.config['objectID']=objectID
        
        """ modul running """
        self.running=False
        
        """ modul shutdown """
        self.ifShutdown=True
        
        LOG.debug("build default modul %s instance, version %s"%(__name__,__version__))
        
    def stopModul(self):
        '''
        '
        '    stop modul
        '
        '    exceptione: none
        '
        '''
        LOG.critical("stop modul %s"%(self.config['objectID']))
        self.running=False
    
    def startModul(self):
        '''
        '
        '    start modul
        '
        '    exceptione: none
        '
        '''
        LOG.info("starting modul %s"%(self.config['objectID']))
        self.running=True
        
    def shutDownModul(self):
        '''
        
        shutdown gateway
        
        exception: gatewayException
        
        '''
        try:
            if self.running:
                self.stopModul()
            LOG.critical("shutdown modul %s"%(self.config['objectID']))
            self.ifShutdown=False
        except:
            raise defaultEXC("can't shutdown modul %s"%(self.config['objectID']))
               
    def getConfiguration(self):
        """
        return the config from the modul
        
        return: dic
        """
        return self.config
    
    def run(self):
        '''
        '
        '    client loop
        '
        '    exception:    none
        '
        '''
        try:
            LOG.info("%s start"%(self.config['objectID']))
            while not self.ifShutdown:
                ''' running or stop '''
                while self.running:
                    try:
                        pass
                    except:
                        pass
                        self.stop()
                    time.sleep(0.5)
                else:
                    ''' shutdown '''  
                    LOG.info("modul %s is stop, is  defaultGateway"%(self.config['objectID']))
                time.sleep(1)
            else:
                LOG.info("modul %s is shutdown, is  defaultGateway"%(self.config['objectID']))
        except:
            LOG.critical("gateway %s is stop with error"%(self.config['objectID']),True)
    