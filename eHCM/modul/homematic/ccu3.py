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
from xmlrpc.server import SimpleXMLRPCServer           #@UnresolvedImport
from xmlrpc.server import SimpleXMLRPCRequestHandler   #@UnresolvedImport @UnusedImport
import random

# Local application imports
from modul.defaultModul import defaultModul
from .ccu3XML import ccu3XML
from .ccu3RPCComands import ccu3RPCComands
from .ccu3RPCServer import ccu3RPCServer
from .ccu3EXC import ccu3xmlEXC,ccu3EXC,ccu3RPCEXC,ccu3RPCserverEXC
from core.exception import defaultEXC


LOG=logging.getLogger(__name__)

MODUL_PACKAGE="homematic"
                       
RPC_PORT_START=9000


class ccu3(ccu3XML,ccu3RPCComands,defaultModul):
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
            "updateCCU3interval":24,
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
            "updateCCU3interval":24,
            "rpc":{},
            "xml":{}
            }
        defaultCFG.update(modulCFG)   
        
        defaultModul.__init__(self,objectID,defaultCFG)            
        """
            ccu3XML Modul
        """
        
        ccu3XML.__init__(self, objectID, defaultCFG)
        
        """
        container for the ccu3 wakup via XML-API
        """
        self.__timerHmWakeUP=0
        
        """
        Timer for restartRPC server
        """
        self.__timerRestartRPC=0
        
        '''
           build rpc Server
        '''
        for serverName in self.config['rpc']:
            '''
            build server
            '''
            self.__rpcServer[serverName]={"instance":None,
                                          "blockTime":0,
                                          "interfaceID":"int%s"%(random.randint(1,9999)),
                                          "rpcPort":False
                                          }
            LOG.info("build rpc server %s"%(serverName))
     
        """
        block modul
        """
        self.__modulBlockTime=0
        
        '''
            last update ccu3 device 
        '''
        self.__lastCCU3update=0
        
        #TODO brauchen ich das noch
        self.running=True
              
        LOG.info("build ccu3 modul, version %s"%(__version__))  
        
    def run(self):
        try:
            LOG.debug("ccu3 modul up")
            while self.ifShutdown:
                while self.running:
                    try:
                        LOG.debug("ccu3 modul is running")
                        '''
                            update ccu3 devices over xml interface
                        '''
                        if self.__lastCCU3update<int(time.time()):
                            self.__updateCoreDevices()
                        '''
                            start rpc server
                        '''
                        self.__checkRPCServer()
                        
                                
                        
                        time.sleep(1)
                    
                    
                    except:
                        self.__blockModul()
                        LOG.critical("unkown error in rpc server %s"%(self.config['objectID']), exc_info=True)  
                       
                  
                LOG.warning("ccu3 modul is stop")
                    
                time.sleep(4)
            else:
                LOG.critical("ccu3 modul is shutdown")
                
        except:
            
            raise defaultEXC("unkown error in ccu3 modul %s"%(self.config['objectID']),True)
    
    def __checkRPCServer(self):
        '''
            check alle RPC server if running or block
        '''
        try:
            for serverName in self.__rpcServer:
                if not self.__rpcServer['blockTime']>int(time.time()):
                    '''
                        rpc Server not block
                    '''
                    if not self.__rpcServer['instance']:
                        '''
                            start rpc server
                        '''
                        try:
                            self.__startRPCServer(serverName)
                        except (ccu3EXC) as e:
                            LOG.critical("can't start rpc server %s, error:%s"%(serverName,e))
                            self.__blockRPCServer(serverName)
        except:
            raise ccu3EXC("unkown error in %s"%(self.core.thisMethode()),True)
            
    
    def __startRPCServer(self,serverName):
        '''
            start the RPC Server
            
            serverName: Server to start
            
            exception: ccu3EXC
        '''
        try:
            rpcIP=self.core.getLocalIP()
            rpcPort=self.__getFreeRPCPort(serverName)
            LOG.info("start rpc server %s:%s"%(rpcIP,rpcPort))
            '''
                build rpc server instance
            '''
            rpcServerInstance= SimpleXMLRPCServer((rpcIP,int(rpcPort)))
            rpcServerInstance.logRequests=False
            rpcServerInstance.register_introspection_functions() 
            rpcServerInstance.register_multicall_functions() 
            rpcServerInstance.register_instance(ccu3RPCServer(self.config,self))
            '''
                run RPC server in own thread
            '''
            self.__rpcServer[serverName]['instance'] = threading.Thread(target=rpcServerInstance.serve_forever)
            '''
                send ccu3 init request
            '''
            self.rpcInitStart(self.config['ccu3IP'],self.config['rpc'][serverName],self.__rpcServer[serverName]['interfaceID'])
        except (ccu3RPCEXC,ccu3RPCserverEXC) as e:
            raise ccu3EXC("can't send rpc start request %s"%(e))
        except:  
            raise ccu3EXC("unkown error in %s"%(self.core.thisMethode()),True)
            
    def __blockRPCServer(self,serverName):
        '''
            block a rpc server
            
            serverName: var, Server name of the RPC
            
            exception: ccu3EXC
        '''
        try:
            LOG.info("block %s for %s sec rpc server %s "%([serverName],self.config["blockRPCServer"]))
            self.__rpcServer[serverName]={ 'blockTime':int(time.time())+self.config["blockRPCServer"],
                                           'instance':None,
                                           'rpcPort':False
                                         }
            self.rpcInitStop(self.config['ccu3IP'],self.config['rpc'][serverName])
        except (ccu3RPCEXC)as e:
            raise ccu3EXC("some error in RPC connection %s"%(e))
        except:
            raise ccu3EXC("unkown error in %s"%(self.core.thisMethode()),True)
        
    def __blockModul(self):
        LOG.info("block ccu3 modul % sec"%(self.config["blockModul"]))
        self.__modulBlockTime=int(time.time())+self.config["blockModul"]
        
    def __updateCoreDevices(self):
        '''
        
        '''
        try:
            HMDevices=self.XMLDeviceList()
            for HMDevicesID in HMDevices:
                objectID="%s@%s"%(HMDevicesID,self.config["gatewayName"])
                try:
                    if self.core.ifDeviceIDExists(objectID):
                        ''' update device ID '''
                        self.core.updateDevice(objectID, HMDevices[HMDevicesID])
                    else:
                        ''' add new device '''
                        devicePackage=HMDevices[HMDevicesID]['parameter']['devicePackage']
                        deviceType=HMDevices[HMDevicesID]['parameter']['deviceType']
                        self.core.addDevice(objectID, devicePackage, deviceType, HMDevices[HMDevicesID])
                except:
                    LOG.critical("can't add HMDevice:%s"%(HMDevicesID))
            self.__lastCCU3update=int(time.time())+(self.config['updateCCU3interval']*360)
            LOG.info("next ccu3 device update in %s sec / %s h"%(self.config['updateCCU3interval']*360,self.config['updateCCU3interval']))
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
            raise defaultEXC("unkown error in %s"%(self.core.thisMethode()),True)
     
    
            
    def __newDevice(self,hmcSerial,deviceType,parameters={}):
        """ 
        add a ne device to cor
        
        vars:
        hmcSerial,deviceType,parameters={}
        """
        pass
         
    def __getFreeRPCPort(self,serverName):
        """
        
        when self_rpcPort is fals, find a new free TCP Port and
        store it to self.__rpcPort
        
        return int : free TCP port
        
        exception:defaultEXC
        """
        try:
            if not(self.__rpcServer[serverName]['rpcPort']):
                port=RPC_PORT_START
                while (not(self.core.ifPortFree(port))):
                    port=port+1
                self.__rpcServer[serverName]['rpcPort']=port
                LOG.info("finde free network port %s"%(port))
            return self.__rpcServer[serverName]['rpcPort']
        except (defaultEXC) as e:
            raise ccu3EXC("error to find free network port, error: %s"%(e))
        except:
            raise ccu3EXC("unkown error in %s"%(self.core.thisMethode()),True)
            
            