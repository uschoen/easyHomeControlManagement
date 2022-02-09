'''
Created on 01.01.2021

@author: uschoen
'''
# Standard library imports
import logging
import os
import time
import sys
# Local apllication constant
from core.manager import manager as coreManager
from core.exception import defaultEXC
from core.events.eventManager import eventManager


__version__="8.0"
__author__="ullrich schoen"

DEFAULT_CONFIGURATION_FILE = lambda channelPckage, channelType : {'parameter':{},
                            'events':{},
                            'CFGVersion':__version__,
                            'date':int(time.time()),
                            'channelPackage': channelPckage,
                            'channelType': channelType,
                            'name':"unkown",
                            "parameter": {}
                            }


DEVICE_BASE_PATH="modul"

LOG=logging.getLogger(__name__)

class defaultChannel(eventManager,object):
    
    channel_package="hmc"             #default device packgae
    channel_type="defaultChannel"     #default device type
     
    
    def __init__(self,deviceID,channelCFG={},restore=False):
        '''
        deviceID       the device ID how is bound
        channelName    name of the channel
        channelCFG     channel Configuration:
                        channelCFG={
                            'parameter': ...
                            'attribute': ...
                            'events': ...
                            }
        restore          default=False, if ture only restore data
        
        
        '''
        self.deviceID=deviceID
        self.channelName=channelCFG.get('name','unkown')
        self.core=coreManager()
        '''
        absoloute path
        '''
        self.rootPath=("%s/%s"%(os.getcwd(),os.path.dirname(sys.argv[0])))
        '''
        confonfiuration file
        '''
        self.configFile=os.path.normpath("%s/%s/%s/devices/channels/%s.json"%(self.rootPath,DEVICE_BASE_PATH,self.channel_package.replace(".","/"),self.channel_type))
        
        self.__ifConfigLoad=False
        self.__currentCFG={}
        
        '''
        default device parameter
        '''
        self.parameter={
            'name':("%s.%s"%(self.channelName,self.deviceID)),
            'enable':False,
            'value':"",
            'channelPackage':self.channel_package,
            'channelType':self.channel_type,
            'CFGVersion':__version__
            }
        
        '''
        LOAD Chanel parameter
        #####################
        load json parameter
        '''
        self.parameter.update(self.loadConfiguration().get("parameter",{}))
        '''
        update custommer parameter
        '''
        self.parameter.update(channelCFG.get('parameter',{}))
        
        '''
        overwrite the parameter
        '''
        self.parameter['CFGVersion']=__version__
        self.parameter['channelPackage']=self.channel_package
        self.parameter['channelType']=self.channel_type
        ''' 
        LOAD Events
        '''
        eventManager.__init__(self,channelCFG.get('events',{}),restore)    
        
        
        LOG.info("init defaultChannel %s finish, version %s, deviceID:%s"%(self.channelName,__version__,self.deviceID))
    
    
    def updateChannel(self,channelCFG={}):
        
        try:
            '''
            update custommer parameter
            '''
            self.parameter.update(channelCFG.get('parameter',{}))
            '''
            overwrite the parameter
            '''
            self.parameter['CFGVersion']=__version__
            self.parameter['channelPackage']=self.channel_package
            self.parameter['channelType']=self.channel_type
            ''' 
            LOAD Events
            '''
            self.updateEvents(channelCFG.get('events',{}))    
        except (Exception) as e:
            raise defaultEXC("unkown error in updateChannel: %s"(e)) 
        
    def loadConfiguration(self,refresh=False):
        '''
        loading configuration file
        
        refresh= if true reload the file configuration
                 if fals use old configuration
                 default false
        
        return a Dictionary
        
        exception: baseDevice
        '''
        try:
            if not self.__ifConfigLoad or refresh:
                if not self.core.ifPathExists(os.path.dirname(self.configFile)):
                    self.core.makeDir(os.path.dirname(self.configFile))
                if not self.core.ifFileExists(self.configFile):
                    self.core.writeJSON(self.configFile,DEFAULT_CONFIGURATION_FILE(self.channel_package,self.channel_type))
                LOG.debug("load device configuration file %s"%(self.configFile))
                self.__currentCFG = self.core.loadJSON(self.configFile)
            self.__ifConfigLoad=True
            return self.__currentCFG
        except IOError:
            raise defaultEXC("can not find file: %s "%(self.configFile))
        except ValueError:
            raise defaultEXC("error in json file: %s "%(self.configFile))
        except:
            raise defaultEXC("unkown error to read json file %s"%(self.configFile)) 
           
    def getParameter(self,parameterName=None):
        """
        get one or all parameter back
        
        @var parameterName: string name of the parameter
        
        @return: dic/string return one[string] or all[dic] parameter
        """
        if parameterName==None:
            return self.parameter
        else:
            if parameterName not in self.parameter:
                raise defaultEXC("can't find parameter name %s in device:%s channel:%s"%(parameterName,self.deviceID,self.channelName))
            return self.parameter.get(parameterName,{})
    
    def getChannelConfiguration(self):
        try:
            channelCFG={"channelPackage": self.channel_package,
                        "channelType": self.channel_type,
                        "events": self.getEventConfiguration(),
                        "parameter": self.getParameter()
                        }
            return channelCFG
        except:
            raise defaultEXC("unkown error in getChannelConfiguration",True)       
        
    def getValue(self):
        return self.parameter['value']
    
    def callEvent(self,eventName):
        '''
            call a event from the channel
            
            eventName: event name to call
            
            exception: defaultEXC
        '''
        if eventName not in self.events:
            raise defaultEXC("event %s unkown to call"%(eventName))
        try:
            self.events[eventName].callCallers(self)
        except:
            raise defaultEXC("some unkown error in %s"%(self.core.thisMethode()),True)
    
    def setValue(self,
                 value):
        try:
            if value!=self.parameter['value']:
                self.parameter['value']=value
                self.events['onchange'].callCallers(self)
                self.events['onrefresh'].callCallers(self)
            else:
                self.parameter['value']=value
                self.events['onrefresh'].callCallers(self) 
        except:
            raise defaultEXC("unkown error in setValue",True)     
    
    def ifEnable(self):
        '''
        check if the channel enable
        
        enable=true
        disable=false
        
        '''
        try:
            return self.parameter['enable']
        except:
            raise defaultEXC("unkown error ifChannelEnable")
    