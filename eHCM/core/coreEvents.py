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

class coreEvents():
    def __init__(self,*args):
        
        
        LOG.info("init core events finish, version %s"%(__version__))
    
    def _onboot(self):
        '''
        this function call at the boot state of the core
        
        this funktion will be exceued:
            _loadAllConfiguration(self.host)
            ...
            
         exception: eventException    
        '''
        try:
            LOG.info("core call onboot event")
            try:
                self._loadAllConfiguration()
            except :
                LOG.error("start without configuration, can't loadAllConfiguration")
        except:
            raise defaultEXC("some error in onboot event from core",True)
        
        
        
    def _onshutdown(self):
        '''
        this function call at the shutdown state of the core
        
        this funktion will be exceued:
            _saveAllConfiguration(self.host)
            ...
            
         exception: eventException    
        '''
        try:
            LOG.info("core call onshutdown event")
            '''
            shutdown all connectors
            '''
            try:
                self.shutDownAllModule("core@%s"%(self.host))
            except (Exception) as e:
                LOG.error("can't shutdown all core Connectors. MSG:"%(format(e)))
            '''
            shutdown remote core
            '''
            #try:
            #    self._shutdownAllCluster()
            #except (Exception) as e:
            #    LOG.error("can't shutdown all cluster connecion MSG: %s"%(format(e)))
                
            '''
            write Configuration
            '''
            try:
                self._writeAllConfiguration()
            except (Exception) as e:
                LOG.error("stop without saveAllConfiguration MSG: %s"%(format(e)))
                
            
        except:
            raise defaultEXC("some error in onshutdown event from core",True)
            