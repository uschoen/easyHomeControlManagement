"""
Created on 01.12.2021

@author: uschoen

install python package ????
use:
  
"""
__version__='0.9'
__author__ = 'ullrich schoen'

# Standard library imports
import logging
from time import sleep
import xmlrpc.client 
from xmlrpc.server import SimpleXMLRPCServer           #@UnresolvedImport
from xmlrpc.server import SimpleXMLRPCRequestHandler   #@UnresolvedImport @UnusedImport
import threading

# Local application imports
from modul.defaultModul import defaultModul
from core.exception import defaultEXC
from modul.homematic.ccu3RPCrequest import ccu3RPCrequest
from modul.homematic.xml_api import xml_api

LOG=logging.getLogger(__name__)

DEFAULT_CFG={}

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
        
        LOG.info("build ccu3 modul, version %s"%(__version__))  
        
    def run(self):
        try:
            LOG.debug("ds1820 modul up")
            while self.ifShutdown:
                LOG.debug("ds1820 modul is running")
                while self.running:
                    #####
                    pass
                    ####
                else:
                    LOG.warning("ccu3 modul is stop")
                    self.stopModul()
                sleep(1)
            else:
                LOG.critical("ccu3 modul is shutdown")
                self.startModul()
        except:
            self.stopModul()
            raise defaultEXC("unkown err in ccu3 modul %s"%(self.config['objectID']),True)
            
    def stopModul(self):
        """
        stop modul
        
        exceptione: defaultEXC
        """
        try:
            #send CCU3 stop
            #### stop rpc server
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
        
        
    def __buildRPCServer(self,ip,port,name):
        '''
        build a RPC Server
        '''
        try:
            
            if self.__rpcServer:
                if self.__rpcServer.isAlive():
                    ''' server is running '''
                    return False
                else:
                    ''' server is exciting but not running '''
                    LOG.warning("RPC Server %s:%s is stop,starting new server %s"%(ip,port,name))
                    self.__stopRpcMSG(self.config['rpc_ip'], self.config['rpc_port'], self.config['hm_ip'], self.config['hm_port'])
                    self.__stopRPCServer()
            LOG.info("RPC Server %s %s:%s start"%(name,ip,port))
            self.rpcServerINST = SimpleXMLRPCServer((ip,int(port)))
            self.rpcServerINST.logRequests=False
            self.rpcServerINST.register_introspection_functions() 
            self.rpcServerINST.register_multicall_functions() 
            self.rpcServerINST.register_instance(ccu3RPCrequest(self.config,self.core,self.__resetAllTimer))
            self.__rpcServer = threading.Thread(target=self.rpcServerINST.serve_forever)
            self.__rpcServer.start()
            self.__resetAllTimer()
            LOG.info("RPC Server %s is start"%(name))
            return True
        except:
            raise defaultEXC("unkown error in builRPCServer %"%(name))
        
        
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
            LOG.info("send a RPC start INIT request at:http://%s:%i ID:%s" %(cfg["ccu3IP"],cfg["ccu3Port"],cfg["interfaceID"]))
            proxy=xmlrpc.client.ServerProxy("http://%s:%i" %(cfg["ccu3IP"], int(cfg["ccu3Port"])))
            proxy.init("http://%s:%i" %(cfg["rpcPort"],int(cfg["rpcPort"]), cfg["interfaceID"]))
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
            LOG.info("send a RPC stop  INIT request at:http://%s:%i" %(cfg["ccu3IP"],cfg["ccu3Port"]))
            proxy=xmlrpc.client.ServerProxy("http://%s:%i" %(cfg["ccu3IP"],int(cfg["ccu3Port"])))
            proxy.init("http://%s:%s"%(cfg["rpcIP"],int(cfg["rpcPort"])))
        except xmlrpc.client.Fault as err:
            LOG.critical("xmlrpc: Exception: %s" % str(err))
            LOG.critical("xmlrpc request Fault code: %d" % err.faultCode)
            LOG.critical("xmlrpc request Fault string: %s" % err.faultString)
        except:
            LOG.critical("can't send a stop INIT request %s"%(cfg),exc_info=True)   