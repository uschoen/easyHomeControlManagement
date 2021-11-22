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
import socket

# Local application imports
from modul.defaultModul import defaultModul
from core.exception import defaultEXC
from modul.homematic.ccu3RPCrequest import ccu3RPCrequest
from modul.homematic.xml_api import xml_api

LOG=logging.getLogger(__name__)

DEFAULT_CFG={
    "MSGtimeout":60,
    "blockRPCServer":60,
    "server":{
            "rpcIP":"127.0.0.1",
            "rpcPort":"9999",
            "ccu3IP":"127.0.0.1",
            "ccu3Port":"2000",
            "interfaceID":"some string"
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
        
        config:={
        
        }
        """
        defaultCFG=DEFAULT_CFG
                        
        defaultCFG.update(modulCFG)
        defaultModul.__init__(self,objectID,defaultCFG)
        """
        interface id
        """
        self.config["server"]["interfaceID"]=randint(1,99999)
        self.config["server"]["rpcIP"]= self.__get_local_ip()
        # @todo loeschen nach ende der test
        self.config["server"]["interfaceID"]="1234"
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
        
        LOG.info("build ccu3 modul, version %s"%(__version__))  
        
    def run(self):
        try:
            LOG.debug("ccu3 modul up")
            while self.ifShutdown:
                while self.running:
                    #####
                    try:
                        sleepTimer=self.__blockTime-int(time())
                        LOG.debug("ccu3 modul is running, sleepTimer:%s" %(sleepTimer))
                        if sleepTimer<=0:
                            sleepTimer=LOOP_SLEEP
                            if self.__rpcServer==False:
                                self.__startRPCServer(self.config["server"])
                                self.__sendStartRPCrequest(self.config['server'])
                            if not(self.__rpcServer.isAlive()):
                                self.__sendStopRPCrequest(self.config['server'])
                                self.__stopRPCServer()
                                self.__startRPCServer(self.config["server"]) 
                                self.__sendStartRPCrequest(self.config['server'])
                            if self.__timerRestartRPC<int(time()):
                                self.__sendStopRPCrequest(self.config['server'])
                                self.__stopRPCServer()
                                self.__startRPCServer(self.config["server"]) 
                                self.__sendStartRPCrequest(self.config['server'])
                            if self.__timerHmWakeUP<int(time()):
                                LOG.warning("message timeout, detected. no message since %s sec"%(self.config['MSGtimeout']))
                                self.__ccu3XMLWakeup(self.config)  
                        sleep(sleepTimer)
                    except (defaultEXC) as e:
                        LOG.critical("error in rpc server  %s msg: %s"%(self.config['objectID'],e))
                        self.__blockServer() 
                        self.__sendStopRPCrequest(self.config['server'])
                        self.__stopRPCServer()             
                    except:
                        LOG.critical("unkown error in rpc server %s"%(self.config['objectID']), exc_info=True)  
                        self.__blockServer() 
                        self.__sendStopRPCrequest(self.config['server'])
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
            self.__sendStopRPCrequest(self.config["server"])
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
            
    def __startRPCServer(self,cfg={}):
        '''
        build a RPC Server
        
        cfg={
            rpcIP:"ip from this Server",
            rpcPort:"port of the lissing server",
            }
        
        rxception: defaultEXC
        '''
        try:
           
            LOG.info("RPC Server %s:%s start"%(cfg["rpcIP"],cfg["rpcPort"]))
            self.rpcServerINST = SimpleXMLRPCServer((cfg["rpcIP"],int(cfg["rpcPort"])))
            self.rpcServerINST.logRequests=False
            self.rpcServerINST.register_introspection_functions() 
            self.rpcServerINST.register_multicall_functions() 
            self.rpcServerINST.register_instance(ccu3RPCrequest(self.config,self.__resetAllTimer))
            self.__rpcServer = threading.Thread(target=self.rpcServerINST.serve_forever)
            self.__rpcServer.start()
            self.__resetAllTimer()
            LOG.info("RPC Server is start %s:%s"%(cfg["rpcIP"],cfg["rpcPort"]))
            return True
        except:
            raise defaultEXC("unkown error in startRPCServer %s"%(self.config["objectID"]),True)
    
    def __get_local_ip(self):

    # From http://stackoverflow.com/a/7335145

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        try:
            s.connect(('8.8.8.8', 9))
            ip = s.getsockname()[0]
        except socket.error:
            raise
        finally:
            del s

        return ip

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
    
    def __resetAllTimer(self):
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
        
    def __sendStartRPCrequest(self,cfg={}):
        '''
        send a init Request to get data from the CCU3
        
        cfg={
            rpcIP:"ip from this Server",
            rpcPort:"port of the lissing server",
            ccu3IP:"ip from the CCU3",
            ccu3Port:"port from the CCU3",
            interfaceID:"client ID at the ccu3"
            }
            
        
        exception: defaultEXC
        '''
        try:
            LOG.info("send a RPC start INIT request at:http://%s:%s ID:%s" %(cfg["ccu3IP"],cfg["ccu3Port"],cfg["interfaceID"]))
            proxy=xmlrpc.client.ServerProxy("http://%s:%i" %(cfg["ccu3IP"], int(cfg["ccu3Port"])))
            proxy.init("http://%s:%i" %(cfg["rpcIP"],int(cfg["rpcPort"])), cfg["interfaceID"])
            LOG.debug("send a RPC INIT Request finish")
        except xmlrpc.client.Fault as err:
            LOG.critical("xmlrpc: Exception: %s" % str(err))
            LOG.critical("xmlrpc request Fault code: %d" % err.faultCode)
            LOG.critical("xmlrpc request Fault string: %s" % err.faultString)
            raise defaultEXC("can'T send rpc start request %s"%(cfg))
        except:
            raise defaultEXC("can't send a start INIT request %s"%(cfg),True)
    
    def __sendStopRPCrequest(self,cfg={}):
        '''
        send a init Request to stop data from the CCU3
        
        cfg={
            rpcIP:"ip from this Server",
            rpcPort:"port of the lissing server",
            ccu3IP:"ip from the CCU3",
            ccu3Port:"port from the CCU3",
            interfaceID:"client ID at the ccu3"
            }
            
        
        exception: defaultEXC
        '''
        try:
            LOG.info("send a RPC stop  INIT request at:http://%s:%s" %(cfg["ccu3IP"],cfg["ccu3Port"]))
            proxy=xmlrpc.client.ServerProxy("http://%s:%i" %(cfg["ccu3IP"],int(cfg["ccu3Port"])))
            proxy.init("http://%s:%s"%(cfg["rpcIP"],int(cfg["rpcPort"])))
        except xmlrpc.client.Fault as err:
            LOG.critical("xmlrpc: Exception: %s" % str(err))
            LOG.critical("xmlrpc request Fault code: %d" % err.faultCode)
            LOG.critical("xmlrpc request Fault string: %s" % err.faultString)
        except:
            LOG.critical("can't send a stop INIT request %s"%(cfg),exc_info=True)   