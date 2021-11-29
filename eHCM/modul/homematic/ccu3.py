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

BidCos-Wired = 2000, BidCos-RF = 2001, Internal = 2002 hm-ip=2020 ???
"""
__version__='0.9'
__author__ = 'ullrich schoen'

# Standard library imports
import logging
import xmlrpc.client 
from xmlrpc.server import SimpleXMLRPCServer           #@UnresolvedImport
from xmlrpc.server import SimpleXMLRPCRequestHandler   #@UnresolvedImport @UnusedImport
import threading
from random import randint
from time import time,sleep


# Local application imports
from modul.defaultModul import defaultModul
from core.exception import defaultEXC
from modul.homematic.ccu3RPCrequest import ccu3RPCrequest
from modul.homematic.xml_api import xml_api

LOG=logging.getLogger(__name__)
DEVICE_IGNORE_FIELD=["PARAMSETS","CHILDREN"]            

DEVICE_MAPPING_FIELDS={"TYPE":"deviceType",
                "RF_ADDRESS":"rfAddress"}

CHANNEL_IGNORE_FIELD=["ADDRESS","PARAMSETS","PARENT","PARENT_TYPE"]            

CHANNEL_MAPPING_FIELDS={"AES_ACTIVE":"aesActive",
                        "TYPE":"channelType"}


MODUL_PACKAGE="homematic"
                       
DEFAULT_CFG={
    "MSGtimeout":60,
    "blockRPCServer":60,
    "server":{
            "rpcPort":"9999",
            "ccu3IP":"127.0.0.1",
            "ccu3Port":"2000"
            },
    "ccu3XML":{
            "hmHost":"http://127.0.0.1",            
            "https":False,                          
            "url":"/config/xmlapi/statechange.cgi"
            },
    "ise_ID":"0",
    "value":"0"
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
            "server":{
                    "rpcPort":"9999",
                    "ccu3IP":"127.0.0.1",
                    "ccu3Port":"2000"
                    },
            "ccu3XML":{
                    "hmHost":"http://127.0.0.1",            
                    "https":False,                          
                    "url":"/config/xmlapi/statechange.cgi"
                    },
            "ise_ID":"0",
            "value":"0"
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
        store the device
        """
        self.device={}
        """
        RPC Proxy
        """
        self.rpcProxy=False
        
        LOG.info("build ccu3 modul, version %s"%(__version__))  
        
    def run(self):
        try:
            LOG.debug("ccu3 modul up")
            while self.ifShutdown:
                # load config from self.config
                rpcIP=self.core.getLocalIP()
                rpcPort=self.config["server"]["rpcPort"]
                interfaceID="test_%s"%(randint(1,99999))
                update=False
                while self.running:
                    #####
                    try:
                        
                        LOG.debug("ccu3 modul is running")
                        sleepTimer=self.__blockTime-int(time())
                        if sleepTimer<=0:
                            sleepTimer=LOOP_SLEEP
                            if self.__rpcServer==False:
                                self.__startRPCServer(rpcIP,
                                                      rpcPort
                                                      )
                                self.__sendStartRPCrequest(rpcIP,
                                                           rpcPort,
                                                           interfaceID
                                                           )
                            if not(self.__rpcServer.isAlive()):
                                self.__sendStopRPCrequest(rpcIP,
                                                          rpcPort
                                                          ) 
                                self.__stopRPCServer()
                                self.__startRPCServer(rpcIP,
                                                      rpcPort
                                                      ) 
                                self.__sendStartRPCrequest(rpcIP,
                                                           rpcPort,
                                                           interfaceID
                                                           )
                            if self.__timerRestartRPC<int(time()):
                                self.__sendStopRPCrequest(rpcIP,
                                                          rpcPort
                                                          )
                                self.__stopRPCServer()
                                self.__startRPCServer(rpcIP,
                                                      rpcPort
                                                      ) 
                                self.__sendStartRPCrequest(rpcIP,
                                                           rpcPort,
                                                           interfaceID
                                                           )
                            if self.__timerHmWakeUP<int(time()):
                                LOG.warning("message timeout, detected. no message since %s sec"%(self.config['MSGtimeout']))
                                self.__ccu3XMLWakeup(self.config)  
                            if not(update):
                                update=True
                                self.__CCUlistDevices()
                        sleep(sleepTimer)
                    except (defaultEXC) as e:
                        LOG.critical("error in rpc server  %s msg: %s"%(self.config['objectID'],e))
                        self.__blockServer() 
                        self.__sendStopRPCrequest(rpcIP,
                                                  rpcPort)
                        self.__stopRPCServer()             
                    except:
                        LOG.critical("unkown error in rpc server %s"%(self.config['objectID']), exc_info=True)  
                        self.__blockServer() 
                        self.__sendStopRPCrequest(rpcIP,
                                                  rpcPort)
                        self.__stopRPCServer()
                    ####
                LOG.warning("ccu3 modul is stop")
                    #self.stopModul()
                sleep(1)
            else:
                LOG.critical("ccu3 modul is shutdown")
                #self.stopModul()
        except:
            #self.stopModul()
            raise defaultEXC("unkown error in ccu3 modul %s"%(self.config['objectID']),True)
            
    def stopModul(self):
        """
        stop modul
        
        exceptione: defaultEXC
        """
        try:
            self.__sendStopRPCrequest(self.core.getLocalIP(),self.config['server']['rpcPort'])
            self.__stopRPCServer()
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
     
    def __ccu3XMLWakeup(self,cfg={}):
        """
        send a xml request to CCU3 
        
        "cfg":{
            "ccu3XML":{
                       "hmHost":"http://127.0.0.1",            
                       "https":False,                          
                       "url":"/config/xmlapi/statechange.cgi"
                      },
            "ise_ID":"CCU3 id of the device",
            "value":"value to set"
        """
        try:
            objectID="ccu3_%s"%(self.config["objectID"])
            xmlClient=xml_api(objectID,cfg["ccu3XML"])
            xmlClient.updateHMDevice(cfg["ise_ID"],cfg["value"])
            self.__resetHmMessagesTimer()
        except (defaultEXC) as e:
            LOG.error("can't send cml request, get some error %s"%(e))
            raise e  
        except:
            raise defaultEXC("unkown error in ccu3XMLWakeup %s"%(self.config["objectID"]),True)
            
    def __startRPCServer(self,
                         rpcIP,
                         rpcPort
                         ):
        '''
        build a RPC Server
        
        cfg={
            rpcIP:"ip from this Server",
            rpcPort:"port of the lissing server",
            }
        
        rxception: defaultEXC
        '''
        try:
           
            LOG.info("RPC Server %s:%s start"%(rpcIP,rpcPort))
            self.rpcServerINST = SimpleXMLRPCServer((rpcIP,int(rpcPort)))
            self.rpcServerINST.logRequests=False
            self.rpcServerINST.register_introspection_functions() 
            self.rpcServerINST.register_multicall_functions() 
            self.rpcServerINST.register_instance(ccu3RPCrequest(self.config,self))
            self.__rpcServer = threading.Thread(target=self.rpcServerINST.serve_forever)
            self.__rpcServer.start()
            self.resetAllTimer()
            LOG.info("RPC Server is start %s:%s"%(rpcIP,rpcPort))
            return True
        except:
            raise defaultEXC("unkown error in startRPCServer %s"%(self.config["objectID"]),True)    

    def __stopRPCServer(self):
        try:
            LOG.warning("stop RPC Server %s"%(self.config['objectID']))
            if self.__rpcServer:
                self.rpcServerINST.shutdown()
                self.rpcServerINST.server_close()
            self.rpcServerINST=False
            self.__rpcServer=False
        except:
            self.rpcServerINST=False
            self.__rpcServer=False
            LOG.critical("unkown error in stopRPCServer %s"%(self.config['objectID']),True)
    
   
    def __newDevice(self,hmcSerial,deviceType,parameters={}):
        """ 
        add a ne device to cor
        
        vars:
        hmcSerial,deviceType,parameters={}
        """
        pass
         
        
            