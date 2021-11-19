'''
Created on 01.12.2018

@author: uschoen
'''

__version__='7.0'
__author__ = 'ullrich schoen'

# Standard library imports
import logging
import threading
import time
import socket

# Local apllication constant
from core.cluster.syncException import localCoreException,protocolException,encryptionException

'''
core protocol
'''
from .protocol.version1 import version1
from .protocol.version2 import version2
CORE_PROTOCOL={
             1:version1,
             2:version2
            }

LOG=logging.getLogger(__name__) 

class localCore(threading.Thread):
    
    def __init__(self,core,coreID,cfg):
        threading.Thread.__init__(self)
        
        ''' 
        configuration 
        '''
        self.config={
            "blocked": 10,
            "ip": "192.168.3.70",
            "port": 5091,
            "protocol":{
                "version":1}
            }
        self.config.update(cfg)
        
        ''' running flag '''
        self.running=True
        
        ''' shutdown Flag '''
        self.ifShutdown=False
             
        ''' core instance ''' 
        self.__core=core
        
        ''' core block for x sec'''
        self.__blockTime=0
        
        ''' core name '''
        self.coreID=coreID
        
        ''' check protokol '''
        if not self.config['protocol']['version'] in CORE_PROTOCOL:
            self.logger.error("protocol version %s is not avaible option, set to 1"%(self.config['protocol']['version']))
            self.config['protocol']['version']=1 
        
        LOG.info("init new local core server %s version %s"%(self.coreID,__version__))
    
    def run(self):
        try:
            LOG.info("%s start"%(self.coreID))
            while not self.ifShutdown:
                ''' running or stop '''
                networkSocket=False
                ipAddr=False
                while self.running:
                    try:
                        if self.__blockTime<int(time.time()):
                            try:
                                if not networkSocket:
                                    networkSocket=self.__buildSocket(self.config['ip'],self.config['port'])
                                networkSocket.settimeout(0.1)
                                (clientSocket, ipAddr) = networkSocket.accept() 
                                networkSocket.settimeout(None)
                                LOG.debug("get connection from %s on local core server %s"%(ipAddr[0],self.coreID))
                                threading.Thread(target=self.__clientRequest,args = (clientSocket,ipAddr[0])).start()
                            except (socket.timeout):
                                pass
                            except:
                                if ipAddr:
                                    ClientIP=ipAddr[0]
                                else:
                                    ClientIP="unkown"
                                self.__closeSocket(networkSocket,ClientIP)
                                networkSocket=False
                                self.__blockServer()
                                LOG.error("error in local core server %s"%(self.coreID))
                        time.sleep(0.4)
                    except:
                        networkSocket=False
                        LOG.info("core connection %s is stop"%(self.coreID),True)
                    time.sleep(0.5)
                ''' shutdown '''    
                time.sleep(0.5)
            LOG.info("core connection %s is shutdown"%(self.coreID))
        except:
            LOG.error("gateway %s is stop with error"%(self.coreID))
    
    def __clientRequest(self,clientSocket,remoteCoreIP):
        try:
            LOG.debug("get new client request from %s on %s"%(remoteCoreIP,self.coreID))
            protocolCFG={"encryption":self.config['protocol']['encryption'],
                                             "remoteCore":self.coreID,
                                             "blocked":self.config["blocked"],
                                             "ip": self.config["ip"],
                                             "port":self.config["port"]
                                             }
            coreProtocol=CORE_PROTOCOL[self.config['protocol']['version']](protocolCFG,self.__core,self.running)
            while self.running and not self.ifShutdown:
                coreProtocol.reciveData(clientSocket,remoteCoreIP)
        except (protocolException,encryptionException) as e:
            LOG.warning("protocol error: on local core %s from remote ip %s : %s"%(self.coreID,remoteCoreIP,e.msg))
        except:
            LOG.warning("unkown error  on local core %s from remote ip %s "%(self.coreID,remoteCoreIP),True)
        LOG.debug("close client request from %s on %s"%(remoteCoreIP,self.coreID))
        self.__closeSocket(clientSocket,remoteCoreIP)     
    
    def __buildSocket(self,ip,port):
        '''
        build a socket connection
        
        fetch exception
        '''
        try:
            networkSocket=socket.socket (socket.AF_INET, socket.SOCK_STREAM)
            networkSocket.bind((ip,port))
            networkSocket.setblocking(0)
            networkSocket.listen(20)
            LOG.debug("lissen on interface %s, port %s on local core server %s"%(ip,port,self.coreID))
            return networkSocket
        except :
            raise localCoreException("can not build socket ip:%s:%s on remote server %s"%(ip,port,self.coreID),True)
        
    def __closeSocket(self,clientSocket,remoteCoreIP):
        ''' close the server socket '''
        try:
            if not clientSocket:
                return
            clientSocket.close()
        except:                             
            pass
        
        LOG.warning("close local core socekt %s from %s ip"%(self.coreID,remoteCoreIP))
        
    def __blockServer(self):
        '''
        block the server for new connections
        '''
        LOG.error("block local core server %s for %i sec"%(self.coreID,self.config['blocked']))
        self.__blockTime=self.config['blocked']+int(time.time())
        
    def stop(self):
        '''
        stop the local Core client
        
        exception: localCoreException
        '''
        try:
            LOG.critical("stop local core connection %s"%(self.coreID))
            self.running=False
        except:
            raise localCoreException("can't shutdown remote core connection %s"%(self.coreID))
        
    def shutdown(self):
        '''
        shutdown the local Core client
        
        exception: localCoreException
        '''
        try:
            if self.running:
                self.stop()
            LOG.critical("shutdown local core connection %s"%(self.coreID))
            self.ifShutdown=True
        except:
            raise localCoreException("can't shutdown local core connection %s"%(self.coreID))