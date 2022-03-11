"""
Created on 01.12.2021

@author: uschoen

install python package ????
use:

Homematic Ports [ccu3Port]
PORT_WIRED = 2000
PORT_WIRED_TLS = 42000
PORT_RF = 2001
PORT_RF_TLS = 42001
PORT_IP = 2010
PORT_IP_TLS = 42010
PORT_GROUPS = 9292
PORT_GROUPS_TLS = 49292

BidCos-Wired = 2000, BidCos-RF = 2001, Internal = 2002 hm-ip=2020 ???


ccu3Command(objectID,modulCFG)

objectID="name"
modulCFG:{
             "ccu3IP":"127.0.0.1",
             "ccu3Port":"2000"                  #Homematic Ports
         }

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

DEVICE_IGNORE_FIELD=["CHILDREN"]           
DEVICE_MAPPING_FIELDS={"TYPE":"deviceType"}

CHANNEL_IGNORE_FIELD=[]          
CHANNEL_MAPPING_FIELDS={"TYPE":"channelType"}

DEFAULT_CFG={"ccu3IP":"127.0.0.1",
             "ccu3Port":"2000"}

MODUL_PACKAGE="homematic"

class ccu3RPCComands(defaultModul):
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
      
    
      
          
    def initStart(self,
                      rpcIP,
                      rpcPort,
                      interface_id
                      ):
        '''
        send a init Request to get data from the CCU3
        
        rpcIP: 127.0.0.01  RPC server to revice Homematic data
        rpcPort: xxxx      RPC server port
        interfacID:        RPC server client ID
            
        
        exception: defaultEXC
        '''
        try:
            url="http://%s:%s"%(rpcIP,rpcPort)
            LOG.info("send a RPC  INIT request to RPC Server %s ID:%s" %(url,interface_id))
            self.__getXMLProxy().init(url,interface_id)
            LOG.debug("send a RPC INIT Request finish")
        except xmlrpc.client.Fault as err:
            LOG.critical("xmlrpc: Exception: %s" % str(err))
            LOG.critical("xmlrpc request Fault code: %d" % err.faultCode)
            LOG.critical("xmlrpc request Fault string: %s" % err.faultString)
            raise defaultEXC("can't send rpc start request %s"%(self.config["objectID"]))
        except:
            raise defaultEXC("can't send a start INIT request %s"%(self.config["objectID"]),True)
    
    def initStop(self,
                 rpcIP,
                 rpcPort):
        '''
        send a init Request to stop data from the CCU3
        
        rpcIP: 127.0.0.01  RPC server to revice Homematic data
        rpcPort: xxxx      RPC server port
        
        exception: defaultEXC
        '''
        try:
            LOG.info("send a RPC stop  INIT for RPC Server %s:%s" %(rpcIP,rpcPort))
            self.__getXMLProxy().init("http://%s:%s"%(rpcIP,int(rpcPort)))
        except xmlrpc.client.Fault as err:
            LOG.critical("xmlrpc: Exception: %s" % str(err))
            LOG.critical("xmlrpc request Fault code: %d" % err.faultCode)
            LOG.critical("xmlrpc request Fault string: %s" % err.faultString)
        except:
            LOG.critical("can't send a stop INIT request %s"%(self.config["objectID"]),exc_info=True)   
    
    def getDevices(self):   
        """
        return all hmcDevices
        
        return: dic
        
        exception: defaultEXC
        """
        try:
            return self.__ccu3ListDevices()
            #return self.__formatOutput(self.__ccu3ListDevices())
        except:
            raise defaultEXC("unkon error in getdevices",True)   
    
    def getDeviceDescription(self,address,typ):
        return self.__getParamset(address,typ)
    
    def __getParamset(self,address,parmType):
        """
        
        ????
        
        address: string    ccu3 device address
        parmtype, MASTR|VALUES|LINK
        
        return: dic 
        
        exception: defaultEXC
        """
        try:
            LOG.info("get device description for devices %s from the ccu for %s" %(address,self.config["objectID"]))
            device=self.__getXMLProxy().getParamset(address,parmType)
            return device
        except xmlrpc.client.Fault as e:
            LOG.warning("error in getParmset %s"%(e))
            return {}
        except:
            raise defaultEXC("unkon error in getParamset",True)   
        
    
    def __getParamsetDescription(self,address,parmType):
        """
        
        get the device parameter description back
        
        address: string    ccu3 device address
        parmtype, MASTR|VALUES|LINK
        
        return: dic 
        
        exception: defaultEXC
        """
        try:
            LOG.info("get device description for devices %s from the ccu for %s" %(address,self.config["objectID"]))
            device=self.__getXMLProxy().getParamsetDescription(address,parmType)
            return device
        except:
            raise defaultEXC("unkon error in getParamsetDescription",True)   
        
    def __getDeviceDescription(self,address):
        """
        
        get the device description back
        
        address: string    ccu3 device address
        
        return: dic 
        
        exception: defaultEXC
        """
        try:
            LOG.info("get device description for devices %s from the ccu for %s" %(address,self.config["objectID"]))
            device=self.__getXMLProxy().getDeviceDescription(address)
            return device
        except:
            raise defaultEXC("unkon error in getDeviceDescription",True)         
              
    def __ccu3ListDevices(self):
        """
        list all devices from the ccu
        
        return RAW data from CCU
        
        exception: defaultEXC
        """
        try:
            LOG.info("list all devices from the ccu for %s" %(self.config["objectID"]))
            devices=self.__getXMLProxy().listDevices()
            return devices
        except:
            raise defaultEXC("unkown errer in listdevices for %s"%(self.config["objectID"]),True) 
    
    def __getXMLProxy(self):
        """
        build a Proxy
    
        return a xmlProxy
        
        exception: defualtEXC
        """
        try:
            if not (self.__xmlProxy):
                LOG.info("build xmlProxy at:http://%s:%s" %(self.config["ccu3IP"],self.config["ccu3Port"]))
                self.__xmlProxy=xmlrpc.client.ServerProxy("http://%s:%s" %(self.config["ccu3IP"], self.config["ccu3Port"]))
            return self.__xmlProxy
        except:
            self.__xmlProxy=False
            raise defaultEXC("unkown errer getXMLProxy",True)   
    
