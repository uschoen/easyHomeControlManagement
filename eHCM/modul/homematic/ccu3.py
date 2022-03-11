"""
Created on 01.12.2021

@author: uschoen

install python package ????
use:

devicelist:
https://10.90.12.90/addons/xmlapi/devicelist.cgi

<channel name="HMIP Virtuelle Taster:0" type="30" address="HmIP-RCV-1:0" ise_id="35183" direction="UNKNOWN" parent_device="35182" index="0" group_partner="" aes_available="false"

PORT_WIRED = 2000
PORT_WIRED_TLS = 42000
PORT_RF = 2001
PORT_RF_TLS = 42001
PORT_IP = 2010
PORT_IP_TLS = 42010
PORT_GROUPS = 9292
PORT_GROUPS_TLS = 49292

"""
__version__='0.9'
__author__ = 'ullrich schoen'

# Standard library imports
import logging
import threading
import time 
import copy

# Local application imports
from modul.defaultModul import defaultModul
from .ccu3XML import ccu3XML
from .ccu3EXC import ccu3xmlEXC
from core.exception import defaultEXC


LOG=logging.getLogger(__name__)

MODUL_PACKAGE="homematic"
                       

LOOP_SLEEP=1

class ccu3(ccu3XML,defaultModul):
    '''
    classdocs
    
    '''
    def __init__(self,objectID,modulCFG):
        """
        
        connector for ccu3 with RPC Interface
        
        establish a rpc Server to recive messages from the ccu3
        
        cfg={"MSGtimeout":60,
            "blockRPCServer":60,
            "blockModul":60,
            "ccu3IP":"127.0.0.1",
            "gatewayName":"unkown@unkown",
            "xml":{},
            "rpc":{
                "PORT_WIRED" : 2000,
                "PORT_WIRED_TLS" : 42000,
                "PORT_RF" : 2001,
                "PORT_RF_TLS" : 42001,
                "PORT_IP" : 2010,
                "PORT_IP_TLS" : 42010,
                "PORT_GROUPS" : 9292,
                "PORT_GROUPS_TLS" : 49292
                }
            }
        """
        defaultCFG={
            "MSGtimeout":60,
            "blockRPCServer":60,
            "blockModul":60,
            "gatewayName":"unkown@unkown",
            "ccu3IP":"127.0.0.1",
            "rpc":{},
            "xml":{}
            }
        defaultCFG.update(modulCFG)   
        
        defaultModul.__init__(self,objectID,defaultCFG)            
        """
            ccu3XML Modul
        """
        
        ccu3XML.__init__(self, objectID, defaultCFG)
        
        
        
        print(self.config)
        
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
        
        
        """
        block modul
        """
        self.__modulBlockTime=0
        
        #TODO brauchen ich das noch
        self.running=True
              
        LOG.info("build ccu3 modul, version %s"%(__version__))  
        
    def run(self):
        try:
            LOG.debug("ccu3 modul up")
            while self.ifShutdown:
                while self.running:
                    try:
                        self.__updateCoreDevices()
                        LOG.debug("ccu3 modul is running")
                        time.sleep(10)
                    
                    
                    except:
                        self.__blockModul()
                        LOG.critical("unkown error in rpc server %s"%(self.config['objectID']), exc_info=True)  
                       
                  
                LOG.warning("ccu3 modul is stop")
                    
                time.sleep(4)
            else:
                LOG.critical("ccu3 modul is shutdown")
                
        except:
            
            raise defaultEXC("unkown error in ccu3 modul %s"%(self.config['objectID']),True)
    
    def __blockModul(self):
        LOG.info("block ccu3 modul % sec"%(self.config["blockModul"]))
        self.__modulBlockTime=int(time.time())+self.config["blockModul"]
        
    def __updateCoreDevices(self):
        '''
        
        '''
        print (self.config)
        try:
            HMDevices=self.XMLDeviceList()
            for HMDevicesID in HMDevices:
                objectID="%s@%s"%(HMDevicesID,self.config["gatewayName"])
                try:
                    if self.core.ifDeviceIDExists(objectID):
                        ''' update device ID '''
                        LOG.error("Device %s exitsnot implement"%(objectID))
                    else:
                        ''' add new device '''
                        devicePackage=HMDevices[HMDevicesID]['parameter']['devicePackage']
                        deviceType=HMDevices[HMDevicesID]['parameter']['deviceType']
                        self.core.addDevice(objectID, devicePackage, deviceType, HMDevices[HMDevicesID])
                except:
                    LOG.critical("can't add HMDevice:%s"%(HMDevicesID))
        except (ccu3xmlEXC) as e:
            LOG.critical("some error in ccu3XML %s"%(e))
        except:
            raise defaultEXC("unkown error in %s"%(self.core.thisMethode()),True)
           
    def stopModul(self):
        """
        stop modul
        
        exceptione: defaultEXC
        """
        try:
            defaultModul.stopModul(self)
        except:
            raise defaultEXC("unkown error in ccu3 at stopModul",True)
            
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
         
        
            