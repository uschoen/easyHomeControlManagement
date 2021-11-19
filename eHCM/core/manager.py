'''
Created on 01.12.2021

@author: uschoen
'''
__version__ = '0.9'

__author__ = 'ullrich schoen'

# Standard library imports
import threading
import logging
import time

# Local library imports
from core.coreBase import coreBase
from core.coreDefaults import coreDefaults
from core.coreLogger import coreLogger
from core.coreEvents import coreEvents
from core.coreConfiguration import coreConfiguration
from core.coreModule import coreModule
from core.coreDevice import coreDevices
from core.coreChannels import coreChannels
from core.coreCluster import coreCluster
from core.script.scriptManager import scriptManager 
from core.exception import defaultEXC

# defaults
LOG=logging.getLogger(__name__)
CORELOOP=10

class manager(
              coreBase,
              coreDefaults,
              coreLogger,
              coreEvents,
              coreModule,
              coreDevices,
              coreConfiguration,
              coreCluster,
              coreChannels,
              scriptManager
              ):
    
    """A thread-safe class acting like a singleton"""
    _instance = None
    _lock = threading.Lock()

    def __new__(cls,configFile=None,debugType=None):
        if not cls._instance:
            with cls._lock:
                cls._instance = object.__new__(cls)
        return cls._instance
    
    def __init__(self,configFile=None,debugType=None):
        if hasattr(self, 'firstrun'):
            return
        self.__initFirstRun(configFile,debugType)
        
    def __initFirstRun(self,configFile=None,debugType=None):    
        self.firstrun=True
        self.coreShutdown=False
        self.debugType=debugType
        
        '''
        #####################################################
        start up corebase information and function
        #####################################################
        '''
        coreBase.__init__(self)
        
        LOG.info("starting core on host %s in root path %s run at /%s"%(self.host,self.rootPath,self.runPath))
        
        '''
        #####################################################
        load configuration 
        #####################################################
        '''
        coreDefaults.__init__(self)
        coreLogger.__init__(self)
        coreCluster.__init__(self)
        coreModule.__init__(self)
        '''
        self.args: configurtion of the core 
        '''
        self.args={}
        
        
        self.args=self.getCoreDefaults()['config']
        try:
            if not configFile == None:
                self.args.update(self.loadJSON(configFile))
        except:
            LOG.warning("can not load config file %s, use default config"%(configFile))
        
        '''
        #####################################################
        load core module
        #####################################################
        '''
        coreEvents.__init__(self)  
        coreConfiguration.__init__(self)  
        coreDevices.__init__(self)
        coreChannels.__init__(self)
        scriptManager.__init__(self)
        
        
        LOG.info("init core manager finish, version %s"%(__version__))  
        
    def start(self):
        '''
        #####################################################
        coreloop
        #####################################################
        '''
        try:
            LOG.info("start up core")
            try:
                self._onboot()
            except (defaultEXC):
                LOG.error("can't call the onboot event")
            while 1:
                LOG.debug("coreLoop is running")
                time.sleep(CORELOOP)
        except (SystemExit, KeyboardInterrupt) as e:
            LOG.critical("get signal to kill coreManager process! coreManager going down !!")
            raise e
        except:
            raise defaultEXC("unkown error in coreLoop",True)
        finally:
            LOG.critical("stop coreLoop %s"%(self.host))
            self._shutdown()
    
    def _shutdown(self):
        '''
        ################################################################
        internal function to shutdown this coreServer
        
        exception: 
        ################################################################
        '''
        try:
            if self.coreShutdown:
                return
            self.coreShutdown=True
            LOG.warning("start to shutdown core %s"%(self.host))
            try:
                # Call Event
                self._onshutdown()
            except (defaultEXC):
                LOG.error("can't call the onshutdown event")
                
            LOG.warning("wait 5 sec, to shutdown core %s finaly"%(self.host))
            time.sleep(5)
        except:
            LOG.error("some error in _shutdown coreServer",exc_info=True)
            
    def shutdown(self,hostID=None,forceUpdate=False):
        '''
        ################################################################
        shutdown the corserver
        
        objectID: CoreID (format core@hostename)
        forceUpdate: send request du other core
        ################################################################
        '''
        try:
            if hostID==None:
                hostID="core@%s"%(self.host)
            if self.ifonThisHost(hostID):
                self._shutdown()
            else:
                self.updateRemoteCore(forceUpdate,hostID,'shutdown',hostID)
        except:
            LOG.error("some error in shutdown coreServer", exc_info=True)