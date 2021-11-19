'''
Created on 01.12.2018

@author: uschoen
'''


__version__="8.0"
__author__="ullrich schoen"

# Standard library imports
import logging
import time

# Local apllication constant
DEVICE_BASE_PATH="modul"      #device base path

DEFAULT_CONFIGURATION_FILE={'parameter':{},
                            'channels':{},
                            'CFGVersion':__version__,
                            'date':int(time.time()),
                            'events':{}
                            }

# Local library imports
from core.manager import manager as coreManager
from core.exception import defaultEXC
from .defaultBase import deviceBase
from .channelManager import channelManager
from core.events.eventManager import eventManager

LOG=logging.getLogger(__name__)



class defaultDevice(deviceBase,channelManager,eventManager):
    '''
    defaut device
    default object for devices
    '''
    deviceType="defaultDevice"
    devicePackage="hmc"
    
    def __init__(self,
                 deviceID,
                 deviceCFG={},
                 restore=False
                 ):
        
        
        '''
        core instance
        '''
        self.core=coreManager()
        
        '''
        device ID
        '''
        self.deviceID=deviceID
        
        '''
        deviceBase 
        '''      
        deviceBase.__init__(self)
        
        '''
        device parameter
        '''
        self.parameter={
            'name':deviceID,
            'deviceID':deviceID,
            'enable':False,
            'deviceType':self.deviceType,
            'devicePackage':self.devicePackage,
            'CFGVersion':__version__
        }
        ''' 
        LOAD DEVICE PARAMETER
        #####################
        load json parameter
        '''
        self.parameter.update(self.loadConfiguration().get("parameter",{})) 
        '''
        import customer parameter from deviceCFG
        '''
        self.parameter.update(deviceCFG.get('parameter',{}))
        self.parameter['CFGVersion']=__version__
        
        '''
        LOAD CHANNELS 
        '''
        channelManager.__init__(self,deviceCFG.get('channels',{}),restore)
               
        ''' 
        LOAD Events
        '''
        eventManager.__init__(self,deviceCFG.get('events',{}),restore)
        
    def getParameter(self):
        try:
            return self.parameter
        except (Exception) as e:
            raise defaultEXC("some error in getParameter MSG:%s"%(format(e)))
    
    def ifDeviceEnable(self):
        '''
            check if device enable
            
            return: 
                true if device enable
                false if no device disable
            
            exception:
                deviceException
        '''
        try:
            return self.parameter['enable']
        except (Exception) as e:
            raise defaultEXC("some error in ifDeviceEnable MSG:%s"%(format(e)))
    
    def getConfiguration(self):
        '''
        get the hole  device & channel & event configuration back
        '''
        try:
            conf={
                'parameter':self.getParameter(),
                'events':self.getEventConfiguration(),
                'channels':self.getChannelsConfiguration(),
                'deviceType':self.getParameter()["deviceType"],
                'devicePackage':self.getParameter()["devicePackage"]
            }
            return conf
        except (Exception) as e:
            raise defaultEXC("some error in getConfiguration MSG:%s"%(format(e)))