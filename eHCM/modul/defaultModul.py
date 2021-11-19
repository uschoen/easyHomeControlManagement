'''
Created on 01.12.2018

@author: uschoen
'''


__version__='8.0'
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
        self.core=coreManager()
        self.config={
                        'enable':False,
                        'objectID':"unkown"
                      }
        self.config.update(modulCFG)
        ''' gateway running '''
        self.running=False
        
        self.ifShutdown=True
        ''' core instance '''
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
        return self.config
    
    def callBack(self,objectID,*args):
        '''
        '
        ' dummy callBack
        '
        '''
        LOG.error("modul %s have no callBack. Callback init by onjectID:%s"%(self.config['objectID'],objectID))
        return
    
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
                ''' shutdown '''    
                time.sleep(0.5)
            LOG.info("gateway %s is shutdown, is  defaultGateway"%(self.config['objectID']))
        except:
            LOG.error("gateway %s is stop with error"%(self.config['objectID']))
    