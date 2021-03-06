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
from xmlrpc.server import SimpleXMLRPCServer           #@UnresolvedImport
from xmlrpc.server import SimpleXMLRPCRequestHandler   #@UnresolvedImport @UnusedImport
import threading
import random 
import string
from time import time,sleep


# Local application imports
from modul.defaultModul import defaultModul
from core.exception import defaultEXC
from modul.homematic.ccu3RPCServer import ccu3RPCServer
from modul.homematic.ccu3XML import ccu3XML
from modul.homematic.ccu3Commands import ccu3Commands

LOG=logging.getLogger(__name__)


MODUL_PACKAGE="homematic"
RPC_PORT_START=9000
                       
DEFAULT_CFG={
    "MSGtimeout":60,
    "blockRPCServer":60,
    "ccuIP":{
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

class ccu3Events(defaultModul):
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
        self.__rpcServerINST=False
        
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
        Client Interface ID
        """
        self.__interfaceID="%s%s"%(''.join(random.sample(string.ascii_letters,8)),random.randint(1,99999))
        
        """
        rpcPort
        """
        self.__rpcPort=False
        
        """
        ccu3Commands for initStart & initStop
        """
        self.__ccu3Commands=ccu3Commands(self.config["objectID"],self.config["ccuIP"])
                
        LOG.info("build ccu3 modul with Interface ID %s, version %s"%(self.__interfaceID,__version__))  
        
    def run(self):
        try:
            LOG.debug("ccu3 modul up")
            while self.ifShutdown:
                while self.running:
                    #####
                    try:
                        LOG.debug("ccu3 modul is running")
                        sleepTimer=self.__blockTime-int(time())
                        rpcIP=self.core.getLocalIP()
                        rpcPort=self.__getFreeRPCPort()
                        
                        if sleepTimer<=0:
                            sleepTimer=LOOP_SLEEP
                            """ server is not build """
                            if self.__rpcServer==False:
                                self.__startRPCServer()
                                self.__ccu3Commands.initStart(rpcIP,
                                                              rpcPort,
                                                              self.__interfaceID
                                                              )
                            
                            """ server is build but not running """
                            if not(self.__rpcServer.isAlive()):
                                self.__ccu3Commands.initStop(rpcIP,
                                                             rpcPort
                                                             )
                                self.__stopRPCServer()
                                self.__startRPCServer() 
                                self.__ccu3Commands.initStart(rpcIP,
                                                              rpcPort,
                                                              self.__interfaceID
                                                              )
                            
                            """ restart all, no events detect """
                            if self.__timerRestartRPC<int(time()):
                                self.__ccu3Commands.initStop(rpcIP,
                                                             rpcPort
                                                             )
                                self.__stopRPCServer()
                                self.__startRPCServer() 
                                self.__ccu3Commands.initStart(rpcIP,
                                                              rpcPort,
                                                              self.__interfaceID
                                                              )
                            """ no events detect send a dummy change """    
                            if self.__timerHmWakeUP<int(time()):
                                LOG.warning("message timeout, detected. no message since %s sec"%(self.config['MSGtimeout']))
                                self.__ccu3XMLWakeup(self.config)
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
            rpcIP=self.core.getLocalIP()
            rpcPort=self.__getFreeRPCPort()
            self.__ccu3Commands.initStop(rpcIP,
                                         rpcPort)
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
            xmlClient=ccu3XML(objectID,cfg["ccu3XML"])
            xmlClient.updateHMDevice(cfg["ise_ID"],cfg["value"])
            self.__resetHmMessagesTimer()
        except (defaultEXC) as e:
            LOG.error("can't send cml request, get some error %s"%(e))
            raise e  
        except:
            raise defaultEXC("unkown error in ccu3XMLWakeup %s"%(self.config["objectID"]),True)
            
    def __startRPCServer(self):
        '''
        build a RPC Server
        
        cfg={
            rpcIP:"ip from this Server",
            rpcPort:"port of the lissing server",
            }
        
        rxception: defaultEXC
        '''
        try:
            rpcIP=self.core.getLocalIP()
            rpcPort=self.__getFreeRPCPort()
            LOG.info("RPC Server %s:%s start"%(rpcIP,rpcPort))
            self.rpcServerINST = SimpleXMLRPCServer((rpcIP,int(rpcPort)))
            self.rpcServerINST.logRequests=False
            self.rpcServerINST.register_introspection_functions() 
            self.rpcServerINST.register_multicall_functions() 
            self.rpcServerINST.register_instance(ccu3RPCServer(self.config,self))
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
        except:
            LOG.critical("unkown error in stopRPCServer %s"%(self.config['objectID']),True)
        self.rpcServerINST=False
        self.__rpcServer=False
        self.__rpcPort=False
    
    def resetAllTimer(self):
        """
        stop both timer 
        
        stop timer HmMessages and restartRPC timer
        """
        self.__resetHmMessagesTimer()
        self.__resetRestartRPCTimer()
    
    def __blockServer(self):
        '''
        block the server for new connections
        '''
        try:
            LOG.error("block server %s for %s sec"%(self.config['objectID'],self.config['blockRPCServer']))
            self.__blockTime=self.config['blockRPCServer']+int(time())
        except:
            raise defaultEXC("some unkown error in block server %s"%(self.config['objectID']),True)
           
    def __resetHmMessagesTimer(self):
        self.__timerHmWakeUP=self.config['MSGtimeout']+int(time()) 
    
    def __resetRestartRPCTimer(self):
        self.__timerRestartRPC=self.config['MSGtimeout']+int(time())+5
        
    def __getFreeRPCPort(self):
        """
        
        when self_rpcPort is fals, find a new free TCP Port and
        store it to self.__rpcPort
        
        return int : free TCP port
        
        exception:defaultEXC
        """
        try:
            if not(self.__rpcPort):
                port=RPC_PORT_START
                while (not(self.core.ifPortFree(port))):
                    port=port+1
                self.__rpcPort=port
                LOG.info("finde free network port %s"%(port))
            return self.__rpcPort
        except:
            raise defaultEXC("unkown error in getFreePort",True)
        
    