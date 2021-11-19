'''
Created on 14.12.2020

@author: uschoen
'''
__version__ = '8.0'
__author__ = 'ullrich schoen'



 
# Standard library imports
import logging
import time
import os
import py_compile

# Local application imports
from core.exception import defaultEXC
from .defaultDevice import DEVICE_BASE_PATH

DEFAULT_CHANNEL_PACKAGE="hmc"
DEFAULT_CHANNEL_TYPE="defaultChannel"


LOG=logging.getLogger(__name__)

class channelManager():
    
    def __init__(self,
                 channels={},
                 restore=False
                 ):
        '''
        channels
        '''
        self.channels={}
        '''
        restore channels from configuration json file
        ''' 
        cfgChannels=self.loadConfiguration().get("channels",{})
        for channelName in cfgChannels:
            LOG.debug("restore json configuration file channel:%s"%(channelName))
            self.restoreChannel(channelName,cfgChannels[channelName])
        '''
        restore custommer channels
        '''
        for channelName in channels:
            LOG.debug("restore costummer channel:%s"%(channelName))
            self.restoreChannel(channelName,channels[channelName])
        
        
        LOG.info("init deviesChannel for deviceID %s finish, version %s"%(self.deviceID,__version__))
    
    def getChannelsConfiguration(self):
        
        try:
            channelCFG={}
            for channelName in self.channels:
                channelCFG[channelName]=self.channels[channelName].getChannelConfiguration()
            return channelCFG
        except:
            raise defaultEXC("can't getChannelsConfiguration for deviceID:%s"%(self.deviceID)) 
    
    def ifChannelEnable(self,channelName):
        if channelName not in self.channels:
            raise defaultEXC("no channel  with %s extits"%(channelName))
        try:
            return self.channels[channelName].ifEnable()
        except:
            raise defaultEXC("can't ifChannelEnable for channel %s for deviceID:%s"%(channelName,self.deviceID)) 
    
    def setChannelValue(self,
                        channelName,
                        value):
        if channelName not in self.channels:
            raise defaultEXC("no channel  with %s extits"%(channelName))
        try:
            return self.channels[channelName].setValue(value)
        except:
            raise defaultEXC("can't setValue for channel %s for deviceID:%s"%(channelName,self.deviceID)) 
    
    def getChannelValue(self,channelName):
        
        if channelName not in self.channels:
            raise defaultEXC("no channel  with %s extits"%(channelName))
        try:
            return self.channels[channelName].getValue()
        except:
            raise defaultEXC("can't getChannelValue for channel %s for deviceID:%s"%(channelName,self.deviceID)) 
      
    
    
    def ifDeviceChannelExist(self,channelName):
        '''
        check if a channel exists in this device
        
        return true/false
        '''
        try:
            if channelName in self.channels:
                return True
            return False
        except (Exception) as e:
            raise defaultEXC("some error in ifDeviceChannelExist MSG:%s"%(format(e)))
    
    def restoreChannel(self,
                       channelName,
                       channelCFG={}):
        try:
            channelCFG["channelPackage"]=channelCFG.get("channelPackage","hmc")
            channelCFG["channelType"]=channelCFG.get("channelType","defaultChannel")
            if channelName in self.channels:
                self.__updateChannel(channelName, channelCFG)
            else:
                self.__addChannel(channelName, channelCFG,True)
        except (Exception) as e:
            LOG.error("can't restore channel %s for deviceID:%s msg:%s"%(channelName,self.deviceID,e))
    
    def __updateChannel(self,
                        channelName,
                        channelCFG):
        try:
            LOG.debug("update channel %s for deviceID:%s"%(channelName,self.deviceID))
            self.channels[channelName].updateChannel(channelCFG)
        except (Exception) as e:
            LOG.error("can't update channel %s for deviceID:%s msg:%s"%(channelName,self.deviceID,e))
    
    def addChannel(self,
                     channelName,
                     channelCFG,
                     restore=False):
        if channelName in self.channels:
            raise defaultEXC("channel %s in device % exists"%(channelName,self.deviceID))
        try:
            LOG.debug("add channel %s for deviceID:%s"%(channelName,self.deviceID))
            self.__buildChannel(channelName, channelCFG["channelPackage"], channelCFG["channelType"], channelCFG,restore=False)
        except:
            LOG.error("can't add channel %s for deviceID:%s"%(channelName,self.deviceID))
       
    def __addChannel(self,
                     channelName,
                     channelCFG,
                     restore=False):
        try:
            LOG.debug("add channel %s for deviceID:%s"%(channelName,self.deviceID))
            self.__buildChannel(channelName, channelCFG["channelPackage"], channelCFG["channelType"], channelCFG,restore=False)
        except:
            LOG.error("can't add channel %s for deviceID:%s"%(channelName,self.deviceID))
    
    def __buildChannel(self,
                       channelName,
                       channelPackage,
                       channelType,
                       channelCFG={},
                       restore=False
                       ):
        
        try:
            
            ''' 
            check if channel package exists. if do not exits build this channel
            '''
            channelPackageFileName=os.path.normpath("%s/%s/%s/devices/channels/%s.py"%(self.core.rootPath,DEVICE_BASE_PATH,channelPackage.replace(".","/"),channelType))
            self.__checkIfChannelPackageExist(channelName, channelPackageFileName, channelPackage, channelType)
            
            '''
            import & build package
            '''
            channelCFG['name']=channelCFG.get('name',channelName)
            classCFG={
                "deviceID":self.deviceID,
                "channelCFG":channelCFG,
                "restore":restore
                }
            fullChannelPackage="%s.%s.devices.channels"%(DEVICE_BASE_PATH,channelPackage)
            self.channels[channelName]=self.core.loadModul(self.deviceID,fullChannelPackage,channelType,classCFG)
            
            
        except:
            raise defaultEXC("can't build channel %s for deviceID:%s"%(channelName,self.deviceID))
            
    def __checkIfChannelPackageExist(self,
                                     channelName,
                                     channelFileName,
                                     channelPackage,
                                     channelType):
        try:
            if self.core.ifFileExists(channelFileName):
                return
            fileData="\'\'\'\nCreated on %s\n"%(time.strftime("%d.%m.%Y"))
            fileData+="@author: %s\n\n"%(__author__)
            fileData+="\'\'\'\n\n"
            fileData+="__version__=\"%s\"\n"%(__version__)
            fileData+="__author__=\"%s\"\n"%(__author__)
            fileData+="\n"
            fileData+="# Standard library imports\n"
            fileData+="import logging\n"
            fileData+="# Local application imports\n"
            fileData+="from %s.%s.devices.channels.%s import %s\n\n"%(DEVICE_BASE_PATH,DEFAULT_CHANNEL_PACKAGE,DEFAULT_CHANNEL_TYPE,DEFAULT_CHANNEL_TYPE)
            fileData+="LOG=logging.getLogger(__name__)\n"
            fileData+="\n"
            fileData+="class %s(%s):\n"%(channelType,DEFAULT_CHANNEL_TYPE)
            fileData+="\n"
            fileData+="    channel_type=\"%s\"\n"%(channelType)
            fileData+="    channel_package=\"%s\"\n"%(channelPackage)
            fileData+="\n"
            fileData+="    def __init__(self,deviceID,channelCFG={},restore=False):\n"
            fileData+="\n"
            fileData+="        defaultChannel.__init__(self,deviceID,channelCFG,restore)\n"
            fileData+="\n"
            fileData+="\n"
            fileData+="\n"
            fileData+="        self.parameter['CFGVersion']=__version__\n"
            fileData+="\n"
            fileData+="        LOG.info(\"init channel %s finish, version %s, deviceID:%s\"%(self.channel_type,self.channelName,__version__))"
            self.core.writeFile(channelFileName,fileData)
            py_compile.compile(os.path.normpath(channelFileName))
            LOG.debug("create new package %s"%(channelFileName))
        except:
            raise defaultEXC("can't not checkifchannelpackageExists for channel %s, package %s, file %s"%(channelName,channelPackage,channelFileName))