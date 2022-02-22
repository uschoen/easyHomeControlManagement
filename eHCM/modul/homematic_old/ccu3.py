"""
Created on 01.12.2021

@author: uschoen

install python package ????
use:

devicelist:
https://10.90.12.90/addons/xmlapi/devicelist.cgi

<channel name="HMIP Virtuelle Taster:0" type="30" address="HmIP-RCV-1:0" ise_id="35183" direction="UNKNOWN" parent_device="35182" index="0" group_partner="" aes_available="false"



"""
__version__='0.9'
__author__ = 'ullrich schoen'

# Standard library imports
import logging
import threading
from time import time,sleep
import copy

# Local application imports
from modul.defaultModul import defaultModul
from modul.homematic.ccu3Commands import ccu3Commands
from core.exception import defaultEXC


LOG=logging.getLogger(__name__)

MODUL_PACKAGE="homematic"
                       
DEFAULT_CFG={
    "MSGtimeout":60,
    "blockRPCServer":60,
    "ccuIP":{
                "ccu3IP":"127.0.0.1",
                "ccu3Port":"2000"
            }
    }
LOOP_SLEEP=1

class ccu3(defaultModul):
    '''
    classdocs
    
    '''
    def __init__(self,objectID,modulCFG):
        """
        
        connector for ccu3 with RPC Interface
        
        establish a rpc Server to recive messages from the ccu3
        
        cfg={
            "MSGtimeout":60,
            "blockRPCServer":60,
            "ccuIP":{
                "ccu3IP":"127.0.0.1",
                "ccu3Port":"2000"
                }
            }
        """
        defaultCFG=DEFAULT_CFG
                        
        defaultCFG.update(modulCFG)
        defaultModul.__init__(self,objectID,defaultCFG)
        """
        container for the ccu3 wakup via XML-API
        """
        self.__timerHmWakeUP=0
        
        """
        Timer for restartRPC server
        """
        self.__timerRestartRPC=0
        
        """
        container for the rpc server  
        """
        self.rpcServerINST=False
        
        """
        container for the rpc server thread 
        """
        self.__rpcServer=False
        
        """
        block time if error
        """
        self.__blockTime=0
        
        #TODO brauchen ich das noch
        self.running=True
              
        """
        ccu3Commands for initStart & initStop
        """
        self.__ccu3Commands=ccu3Commands(self.config["objectID"],self.config["ccuIP"])
        
        LOG.info("build ccu3 modul, version %s"%(__version__))  
        
    def run(self):
        try:
            LOG.debug("ccu3 modul up")
            while self.ifShutdown:
                while self.running:
                    try:
                        
                        LOG.debug("ccu3 modul is running")
                        sleep(4)
                    except:
                        LOG.critical("unkown error in rpc server %s"%(self.config['objectID']), exc_info=True)  
                       
                  
                LOG.warning("ccu3 modul is stop")
                    
                sleep(4)
            else:
                LOG.critical("ccu3 modul is shutdown")
                
        except:
            
            raise defaultEXC("unkown error in ccu3 modul %s"%(self.config['objectID']),True)
            
    def stopModul(self):
        """
        stop modul
        
        exceptione: defaultEXC
        """
        try:
            defaultModul.stopModul(self)
        except:
            raise defaultEXC("unkown error in ccu3 at stopModul",True)
            
    def updateDevices(self):
        """
        
        update all devices to eHMC
        
        Exception: defaultEXC
        """
        try:
            ccu3Devices=self.__ccu3Commands.getDevices()
            for deviceID in ccu3Devices:
                """
                find channels channels
                """
                #ccu3Devices[deviceID]["channels"]={}
                
                device=copy.deepcopy(ccu3Devices[deviceID])
                device["channels"]={}
                for channelName in ccu3Devices[deviceID]["channels"]:
                    realCCUChannels=self.__ccu3Commands.getDeviceDescription(channelName,"VALUES")
                    for ccu3ChannelName in realCCUChannels:
                       
                
                        device["channels"][ccu3ChannelName]={"channelPackage": MODUL_PACKAGE,
                                                             "channelType": ccu3Devices[deviceID]["channels"][channelName]["parameter"]["channelType"],
                                                             "parameter":{"value":realCCUChannels[ccu3ChannelName]}
                                                            }
                
                #
                LOG.info("try to add new deviceID %s evicePackage:%s deviceType: %s"%(deviceID,MODUL_PACKAGE,device["parameter"]["deviceType"]))
                self.core.addDevice(deviceID,
                                MODUL_PACKAGE,
                                device["parameter"]["deviceType"],
                                device
                                )
            self.core.writeDeviceConfiguration()
        except:
            raise defaultEXC("unkown error in ccu3 at updateDevices",True)
            
    
    def shutDownModul(self):
        """
        shutdown modul
        
        exception: defaultEXC
        
        """
        try:
            self.stopModul()
            defaultModul.shutDownModul(self)
        except:
            raise defaultEXC("unkown error in ccu3 at shutDownModul",True)
     
    
            
    def __newDevice(self,hmcSerial,deviceType,parameters={}):
        """ 
        add a ne device to cor
        
        vars:
        hmcSerial,deviceType,parameters={}
        """
        pass
         
        
            