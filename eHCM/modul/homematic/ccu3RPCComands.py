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
from .ccu3EXC import ccu3RPCEXC
from modul.defaultModul import defaultModul


LOG=logging.getLogger(__name__)

DEVICE_IGNORE_FIELD=["CHILDREN"]           
DEVICE_MAPPING_FIELDS={"TYPE":"deviceType"}

CHANNEL_IGNORE_FIELD=[]          
CHANNEL_MAPPING_FIELDS={"TYPE":"channelType"}



MODUL_PACKAGE="homematic"

class ccu3RPCComands(defaultModul):
    '''
    classdocs
    '''
    def __init__(self,objectID=False,modulCFG={},serverName=False):
        """
        
        ccu3 RPC commands, 
        
        only some extra Modul for the ccu3 Class
        cfg={
            "ccu3IP":"127.0.0.1",
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
        defaultCFG={"ccu3IP":"127.0.0.1",
                    "rpc":{}
                   }
        '''
            rpc Server to handel
        '''
        self.__serverName=serverName
        
        if not hasattr(self, "config"):
            defaultCFG.update(modulCFG)
            defaultModul.__init__(self,objectID,defaultCFG)                
               
        """
        xml Proxy container
        """
        self.__xmlProxy=False
        
        LOG.info("build ccu3RPCCommands modul for server %s, version %s"%(serverName,__version__))  
      
    
      
          
    def rpcInitStart(self,
                      ccu3IP,
                      ccu3Port,
                      interface_id,
                      remoteIP,
                      remotePort,xmlProxy
                      ):
        '''
        send a init Request to get data from the CCU3
        
        rpcIP: 127.0.0.01  RPC server to revice Homematic data
        rpcPort: xxxx      RPC server port
        interfacID:        RPC server client ID
            
        
        exception: defaultEXC
        '''
        try:
            url="http://%s:%s"%(remoteIP,remotePort)
            LOG.info("send a  INIT start request to ccu3 %s:%s for rpc callback %s ID:%s" %(ccu3IP,ccu3Port,url,interface_id))
            #xmlProxy=xmlrpc.client.ServerProxy("http://%s:%s" %(ccu3IP,ccu3Port))
            #self.__getXMLProxy(ccu3IP,ccu3Port).init(url,interface_id)
            r=xmlProxy.init(url,interface_id)
            LOG.debug("send a RPC INIT strat request finish %s"%(r))
        except xmlrpc.client.Fault as err:
            LOG.critical("xmlrpc: Exception: %s" % str(err))
            LOG.critical("xmlrpc request Fault code: %d" % err.faultCode)
            LOG.critical("xmlrpc request Fault string: %s" % err.faultString)
            raise ccu3RPCEXC("can't send rpc start request %s"%(self.config["objectID"]))
        except:
            raise ccu3RPCEXC("can't send a start INIT start request %s"%(self.config["objectID"]),True)
    
    def rpcInitStop(self,
                 ccu3IP,
                 ccu3Port,
                 remoteIP,
                 remotePort,xmlProxy):
        '''
        send a init Request to stop data from the CCU3
        
        rpcIP: 127.0.0.01  RPC server to revice Homematic data
        rpcPort: xxxx      RPC server port
        
        exception: defaultEXC
        '''
        try:
            url="http://%s:%s"%(remoteIP,remotePort)
            LOG.info("send  INIT stop for RPC ccu3 %s:%s to for remote: %s" %(ccu3IP,ccu3Port,url))
            #xmlProxy=xmlrpc.client.ServerProxy("http://%s:%s" %(ccu3IP,ccu3Port))
            #self.__getXMLProxy(ccu3IP,ccu3Port).init(url)
            r=xmlProxy.init(url)
            LOG.debug("send a RPC INIT stop request finish %s"%(r))
        except xmlrpc.client.Fault as err:
            LOG.critical("xmlrpc: Exception: %s" % str(err))
            LOG.critical("xmlrpc request Fault code: %d" % err.faultCode)
            LOG.critical("xmlrpc request Fault string: %s" % err.faultString)
        except:
            LOG.critical("can't send a INIT stop request %s"%(self.config["objectID"]),exc_info=True)   
    
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
            raise ccu3RPCEXC("unkon error in getdevices",True)   
    
    def getDeviceDescription(self,address,typ,rpcIP,rpcPort):
        return self.__getParamset(address,typ,rpcIP,rpcPort)
    
    def __getParamset(self,address,parmType,rpcIP,rpcPort):
        """
        
        ????
        
        address: string    ccu3 device address
        parmtype, MASTR|VALUES|LINK
        
        return: dic 
        
        exception: defaultEXC
        """
        try:
            LOG.info("get device description for devices %s from the ccu for %s" %(address,self.config["objectID"]))
            device=self.__getXMLProxy(rpcIP,rpcPort).getParamset(address,parmType)
            return device
        except xmlrpc.client.Fault as e:
            LOG.warning("error in getParmset %s"%(e))
            return {}
        except:
            raise ccu3RPCEXC("unkon error in getParamset",True)   
        
    
    def __getParamsetDescription(self,address,parmType,rpcIP,rpcPort):
        """
        
        get the device parameter description back
        
        address: string    ccu3 device address
        parmtype, MASTR|VALUES|LINK
        
        return: dic 
        
        exception: defaultEXC
        """
        try:
            LOG.info("get device description for devices %s from the ccu for %s" %(address,self.config["objectID"]))
            device=self.__getXMLProxy(rpcIP,rpcPort).getParamsetDescription(address,parmType)
            return device
        except:
            raise ccu3RPCEXC("unkon error in getParamsetDescription",True)   
        
    def __getDeviceDescription(self,address,rpcIP,rpcPort):
        """
        
        get the device description back
        
        address: string    ccu3 device address
        
        return: dic 
        
        exception: defaultEXC
        """
        try:
            LOG.info("get device description for devices %s from the ccu for %s" %(address,self.config["objectID"]))
            device=self.__getXMLProxy(rpcIP,rpcPort).getDeviceDescription(address)
            return device
        except:
            raise ccu3RPCEXC("unkon error in getDeviceDescription",True)         
              
    def __ccu3ListDevices(self,
                          rpcIP,
                          rpcPort):
        """
        list all devices from the ccu
        
        return RAW data from CCU
        
        exception: defaultEXC
        """
        try:
            LOG.info("list all devices from the ccu for %s" %(self.config["objectID"]))
            devices=self.__getXMLProxy(rpcIP,rpcPort).listDevices()
            return devices
        except:
            raise ccu3RPCEXC("unkown errer in listdevices for %s"%(self.config["objectID"]),True) 
    
    def __getXMLProxy(self,
                      rpcIP,
                      rpcPort):
        """
        build a Proxy
    
        return a xmlProxy
        
        exception: defualtEXC
        """
        try:
            LOG.info("build xmlProxy at:http://%s:%s" %(rpcIP,rpcPort))
            xmlProxy=xmlrpc.client.ServerProxy("http://%s:%s" %(rpcIP,rpcPort))
            return xmlProxy
        except:
            del(xmlProxy)
            raise ccu3RPCEXC("unkown errer getXMLProxy",True)   
    
