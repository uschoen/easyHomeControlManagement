"""
Created on 01.12.2021

@author: uschoen

install python package ????
use:

PORT_WIRED = 2000
PORT_WIRED_TLS = 42000
PORT_RF = 2001
PORT_RF_TLS = 42001
PORT_IP = 2010
PORT_IP_TLS = 42010
PORT_GROUPS = 9292
PORT_GROUPS_TLS = 49292

BidCos-Wired = 2000, BidCos-RF = 2001, Internal = 2002 hm-ip=2020 ???
"""
__version__='0.9'
__author__ = 'ullrich schoen'

# Standard library imports
import logging
import xmlrpc.client 


# Local application imports
from core.exception import defaultEXC
from modul.defaultModul import defaultModul
LOG=logging.getLogger(__name__)


DEVICE_IGNORE_FIELD=["PARAMSETS","CHILDREN"]            

DEVICE_MAPPING_FIELDS={"TYPE":"deviceType",
                "RF_ADDRESS":"rfAddress"}

CHANNEL_IGNORE_FIELD=["ADDRESS","PARAMSETS","PARENT","PARENT_TYPE"]            

CHANNEL_MAPPING_FIELDS={"AES_ACTIVE":"aesActive",
                        "TYPE":"channelType"}
DEFAULT_CFG={
             "ccu3IP":"127.0.0.1",
             "ccu3Port":"2000"
            }

MODUL_PACKAGE="homematic"

class ccu3Comands(defaultModul):
    '''
    classdocs
    '''
    def __init__(self,objectID,modulCFG):
        """
        
        ccu3 RPC commands, 
        
        only some extra Modul for the ccu3 Class
        cfg={
            "ccu3IP":"127.0.0.1",
            "ccu3Port":"2000"
            }
        """
        defaultCFG=DEFAULT_CFG
                        
        defaultCFG.update(modulCFG)
        defaultModul.__init__(self,objectID,defaultCFG)
        
        """
        xml Proxy container
        """
        self.__xmlProxy=False
        
        LOG.info("build ccu3Commands modul, version %s"%(__version__))  
      
    
    def __getXMLProxy(self):
        """
        build a Proxy
    
        return a xmlProxy
        
        exception: defualtEXE
        """
        try:
            if not (self.__xmlProxy):
                LOG.info("build xmlProxy at:http://%s:%s" %(self.config["ccu3IP"],self.config["ccu3Port"]))
                self.__xmlrpcProxy=xmlrpc.client.ServerProxy("http://%s:%s" %(self.config["ccu3IP"], self.config["ccu3Port"]))
            return self.__xmlProxy
        except:
            self.__xmlProxy=False
            raise defaultEXC("unkown errer getXMLProxy",True)   
          
    def __ccu3InitStart(self,
                        rpcIP,
                        rpcPort,
                        interface_id
                              ):
        '''
        send a init Request to get data from the CCU3
        
        rpcIP
        rpcPort
        interfacID
            
        
        exception: defaultEXC
        '''
        try:
            url="http://%s:%s"%(rpcIP,rpcPort)
            LOG.info("send a RPC  INIT request to RPC Server %s ID:%s" %(url,interface_id))
            print("init")
            print(self.__getXMLProxy().init(url,interface_id))
            
            LOG.debug("send a RPC INIT Request finish")
        except xmlrpc.client.Fault as err:
            LOG.critical("xmlrpc: Exception: %s" % str(err))
            LOG.critical("xmlrpc request Fault code: %d" % err.faultCode)
            LOG.critical("xmlrpc request Fault string: %s" % err.faultString)
            raise defaultEXC("can't send rpc start request %s"%(self.config["objectID"]))
        except:
            raise defaultEXC("can't send a start INIT request %s"%(self.config["objectID"]),True)
    
    def __ccu3InitStop(self,
                       rpcIP,
                       rpcPort
                       ):
        '''
        send a init Request to stop data from the CCU3
        
        rpcIP
        rpcPort
            
        
        exception: defaultEXC
        '''
        try:
            LOG.info("send a RPC stop  INIT for RPC Server %s:%s" %(rpcIP,rpcPort))
            print("init")
            print(self.__getXMLProxy().init("http://%s:%s"%(rpcIP,int(rpcPort))))
        except xmlrpc.client.Fault as err:
            LOG.critical("xmlrpc: Exception: %s" % str(err))
            LOG.critical("xmlrpc request Fault code: %d" % err.faultCode)
            LOG.critical("xmlrpc request Fault string: %s" % err.faultString)
        except:
            LOG.critical("can't send a stop INIT request %s"%(self.config["objectID"]),exc_info=True)   
            
    def __ccuListDevices(self):
        """
        list all devices from the ccu
        """
        try:
            LOG.info("list all devices from the ccu for %s" %(self.config["objectID"]))
            devices=self.__getXMLProxy().listDevices()
            deviceID=""
            for device in devices:
                if device["PARENT"]:
                    #channel
                    channelName=device['ADDRESS'].lower()
                    if channelName in self.device[deviceID]['channels']:
                        print("channel kenn ich schon %s"%(channelName))
                    else:
                        #new channel
                        self.device[deviceID]['channels'][channelName]={"parameters":{"channelPackage":MODUL_PACKAGE}
                                                                        }
                        for attribute in device:
                            if attribute in CHANNEL_IGNORE_FIELD:
                                continue 
                            eHMCattribut="unkown"
                            if attribute in CHANNEL_MAPPING_FIELDS:
                                eHMCattribut=CHANNEL_MAPPING_FIELDS[attribute]
                            else:
                                eHMCattribut=attribute.lower()
                            self.device[deviceID]['channels'][channelName]['parameters'][eHMCattribut]=device[attribute]
                else:
                    #device
                    deviceID=device['ADDRESS']
                    if device['ADDRESS'] in self.device:
                        #device vorhanden
                        pass
                    else:
                        #neues device
                        self.device[deviceID]={"channels":{},
                                               "parameters":{"devicePackage":MODUL_PACKAGE}                                                       
                                              }
                        
                        for attribute in device:
                            if attribute in DEVICE_IGNORE_FIELD:
                                continue 
                            eHMCattribut="unkown"
                            if attribute in DEVICE_MAPPING_FIELDS:
                                eHMCattribut=DEVICE_MAPPING_FIELDS[attribute]
                            else:
                                eHMCattribut=attribute.lower()
                                
                            self.device[deviceID]['parameters'][eHMCattribut]=device[attribute]
        except:
            raise defaultEXC("unkoqn errer in listdevices for %s"%(self.config["objectID"],True))   
    
