'''
Created on 01.03.2020

@author: uschoen
'''



__version__="9.0"
__author__="ullrich schoen"


# Standard library imports
import logging

# Local apllication constant
from core.events.exception import eventError
from core.events.onChangeEvent import onChangeEvent
from core.events.onCreateEvent import onCreateEvent
from core.events.onDeleteEvent import onDeleteEvent
from core.events.onRefreshEvent import onRefreshEvent
from core.events.onBootEvent import onBootEvent
from core.events.onShutdownEvent import onShutdownEvent

LOG=logging.getLogger(__name__)

class eventManager(object):
    '''
    classdoc
    
    '''
    deviceID="test@test"
    
    def __init__(self,eventsCFG={},restore=False):
        '''
    
        '''
        self.events={
            'onchange':onChangeEvent(eventsCFG.get('onchange',{}),restore),
            'onrefresh':onRefreshEvent(eventsCFG.get('onrefresh',{}),restore),
            'oncreate':onCreateEvent(eventsCFG.get('oncreate',{}),restore),
            'ondelete':onDeleteEvent(eventsCFG.get('ondelete',{}),restore),
            'onboot':onBootEvent(eventsCFG.get('onboot',{}),restore),
            'onshutdown':onShutdownEvent(eventsCFG.get('onShutdown',{}),restore)
            }
        
        LOG.debug("init deviceEvents for deviceID %s finish, version %s"%(self.deviceID,__version__))
    
    def updateEvents(self,eventCFG):
        try:
            for eventName in eventCFG:
                if eventName in self.events:
                    self.updateEventName(eventName,eventCFG[eventName])
                else:
                    LOG.error("can't find event name %s in deviceID %s"%(eventName,self.deviceID))
        except:
            eventError("can't update events for device ID:%s"%(self.deviceID),True) 
    
    def updateEventName(self,eventName,eventCFG):
        try:
            if eventName in self.events:
                self.events[eventName].updateParameter(eventCFG.get('parameters',{}))
                
                self.events[eventName].updateCallers(eventCFG.get('callers',{}))
            else:
                LOG.error("can't find event name %s in deviceID %s"%(eventName,self.deviceID))
        except:
            eventError("can't update event %s for device ID:%s"%(eventName,self.deviceID),True) 
      
    def getEventConfiguration(self):
        '''
        get the device event configuration as dict Back
        
        return_ dict
        '''
        try:
            eventCFG={}
            for eventName in self.events:
                eventCFG[eventName]=self.events[eventName].getConfiguration()
            return eventCFG
        except:
            eventError("some error to get device Event configuration for deviceID %s"%(self.deviceID))