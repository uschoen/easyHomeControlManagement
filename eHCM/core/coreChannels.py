'''
Created on 01.12.2021

@author: uschoen
'''
from core.exception import defaultEXC


__version__='0.9'
__author__ = 'ullrich schoen'

# Standard library imports
import logging
import threading
# Local application imports
from .exception import defaultEXC

DEVICE_BASE_PATH="modul"      #device base path
DEFAULT_DEVICE_PACKGAE="hmc"             #default device packgae
DEFAULT_DEVICE_TYPE="defaultDevice"      #default device type
LOG=logging.getLogger(__name__)

class coreChannels():
    '''
    core events function
    '''
    def __init__(self,*args):
        
        LOG.info("init core channels finish, version %s"%(__version__))
        
    def addDeviceChannel(self,
                         objectID,
                         channelName,
                         channelCFG={},
                         forceUpdate=False
                         ):
        '''
            add a new device channel to the device
            
            objectID    deviceID how to add the channel
            channelName channel name 
            channelCFG  channel config as dic={}
            forceUpdate true/false(default), update remote core even is device not on this host
            
            exception: defaultEXC
            
        '''
        if not self.ifDeviceIDExists(objectID):
            raise defaultEXC("deviceID %s is not exist"%(objectID),False)
        if self.devices[objectID].ifDeviceChannelExist(channelName):
            raise defaultEXC("channel name %s in deviceID %s is  exist"%(channelName,objectID),True)
        try:
            restore=False
            self.devices[objectID].addChannel(channelName,channelCFG,restore)
            '''
                update remote core
            '''
            self.updateRemoteCore(forceUpdate,objectID,self.thisMethode(),objectID,channelName,channelCFG)
        except (Exception) as e:
            raise Exception("can't add channel %s msg:%s"%(channelName,e))   
    
    def ifDeviceChannelExist(self,
                                 objectID,
                                 channelName
                                 ):
        '''
            check if a channel exists for this device 
            
            objectID: the device id to check if enable
            channelName: Channel Name
            
            return: 
                true if device enable
                false if no device disable
            
            exception:
                coreDeviceExecption
        '''
            
        if not self.ifDeviceIDExists(objectID):
            raise defaultEXC("deviceID %s is not exist"%(objectID),False)
        try: 
            return self.devices[objectID].ifDeviceChannelExist(channelName)
        except:
            raise defaultEXC("some errer in ifDeviceChannelExist for deviceID %s"%(objectID))
    
    def ifDeviceChannelEnable(self,
                           objectID,
                           channelName
                           ):
        if not self.ifDeviceIDExists(objectID):
            raise defaultEXC("deviceID %s is not exist"%(objectID),False)
        try: 
            return self.devices[objectID].ifChannelEnable(channelName)
        except:
            raise defaultEXC("error in ifDeviceChannelEnable  deviceID %s channel name:%s"%(objectID,channelName))
    
    def setDeviceChannelValue(self,
                              objectID,
                              channelName,
                              value,
                              forceUpdate=False):
        if not self.ifDeviceIDExists(objectID):
            raise defaultEXC("deviceID %s is not exist"%(objectID),False)
        try: 
            threading.Thread(target=self.devices[objectID].setChannelValue,args = (channelName,value)).start()
            #self.devices[objectID].setChannelValue(channelName,value)
            '''
                update remote core
            '''
            self.updateRemoteCore(forceUpdate,objectID,self.thisMethode(),objectID,channelName,value)
        except:
            raise defaultEXC("can't setDeviceChannelValue  deviceID %s"%(objectID))
    
    def getDeviceChannelValue(self,
                              objectID,
                              channelName):
        if not self.ifDeviceIDExists(objectID):
            raise defaultEXC("deviceID %s is not exist"%(objectID),False)
        try: 
            return self.devices[objectID].getChannelValue(channelName)
        except:
            raise defaultEXC("can't getDeviceChannelValue  deviceID %s"%(objectID))
    
    def getDeviceChannelParameter(self,
                           objectID,
                           channelName
                           ):
        if not self.ifDeviceIDExists(objectID):
            raise defaultEXC("deviceID %s is not exist"%(objectID),False)
        try: 
            return self.devices[objectID].getChannelParameter(channelName)
        except:
            raise defaultEXC("error in getDeviceChannelParameter  deviceID %s channel name:%s"%(objectID,channelName))
    
    def getAllDeviceChannelAttribute(self,
                                     objectID,
                                     channelName):
        if not self.ifDeviceIDExists(objectID):
            raise defaultEXC("deviceID %s is not exist"%(objectID),False)
        try:
            return self.devices[objectID].getAllChannelAttribute(channelName)
        except:
            raise defaultEXC("can not getDeviceChannelAttribute for channel:%s for deviceID:%s"%(channelName,objectID),True)  
    
    def getDeviceChannelAttributValue(self,objectID,channelName,attribut):
        
        if not self.ifDeviceIDExists(objectID):
            raise defaultEXC("deviceID %s is not exist"%(objectID),False)
        try:
            return self.devices[objectID].getAllChannelAttributeValue(channelName,attribut)
        except:
            raise defaultEXC("can not getDeviceChannelAttributValue %s:%s for deviceID %s"%(channelName,attribut,objectID),True)  
        