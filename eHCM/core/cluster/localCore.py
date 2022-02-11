'''
Created on 08.02.2022

@author: uschoen
'''
from copy import deepcopy


__version__='9.0'
__author__ = 'ullrich schoen'

# Standard library imports
import logging
import threading
import time
import socket


# local library imports
from core.exception import defaultEXC


from .protocol.version1  import version1

from .protocol.protocolException import protocolException
from .protocol.encryption.cryptException import cryptException


LOG=logging.getLogger(__name__) 


class localCore(threading.Thread):
    
    def __init__(self,core,coreName,cfg):
        '''
        init local core connector
        
        coreName= "cluster@hostname"
        cfg= {
        
        }
        '''
        threading.Thread.__init__(self)
        '''
            core object
        '''
        self.core=core        
        '''
            core name
        '''
        self.coreName=coreName
                
        ''' 
            connector shutdown
        '''
        self.ifShutdown=False
        
        '''
            connector cfg
        '''
        self.__config={ "blocked":60,
                        "enable":False,
                        "port":9000,
                        "protocol":{"version":1}
                    }
        self.__config.update(deepcopy(cfg))
        
        ''' core block for x sec'''
        self.__blockTime=0
        
        '''
            connector running
        '''
        self.running=self.__config['enable']
        
        '''
            add coreprotocoll version
            default or wrong value, 1
        '''
        self.__coreProtocol={
                        1:version1
                      }
        if not self.__config['protocol']['version'] in self.__coreProtocol:
            LOG.error("protocolVersion %s is not avaible option, set to verion 1"%(self.__config['protocol']['version']))
            self.__config['protocol']['version']=1 
        
        
        LOG.info("init new local core server %s version %s"%(self.coreName,__version__))

    def run(self):
        try:
            LOG.info("%s start"%(self.coreName))
            while not self.ifShutdown:
                ''' running or stop '''
                networkSocket=False
                while self.running:
                    try:
                        if self.__blockTime<int(time.time()):
                            '''
                                 server is not blocked
                            '''
                            try:
                                ClientIP="unkown"
                                if not networkSocket:
                                    networkSocket=self.__buildSocket(self.core.getLocalIP(),self.__config['port'])
                                networkSocket.settimeout(0.1)
                                (clientSocket, ipAddr) = networkSocket.accept() 
                                ClientIP=ipAddr[0]
                                networkSocket.settimeout(None)
                                if not self.core.ifKnownCoreClient(ClientIP):
                                    raise defaultEXC("unkown client was try to connect from %s"%(ClientIP))
                                LOG.debug("get connection from %s on local core server %s"%(ClientIP,self.coreName))
                                remoteCoreprotocol=version1(self.core,self.__config['protocol'],self.running)
                                threading.Thread(target=self.__clientRequest,args = (clientSocket,ClientIP,remoteCoreprotocol)).start()
                            except (socket.timeout):
                                pass
                            except Exception as e:
                                LOG.critical("some error in local core connection: %s"%(e))
                                self.__closeSocket(networkSocket,ClientIP)
                                networkSocket=False
                                self.__blockServer()
                                LOG.error("error in local core server %s"%(self.coreName))
                    except:
                        LOG.critical("some error in local core connector %s"%(self.coreName))
                        self.__blockServer()
                        self.stop()
                    time.sleep(0.5)
                else:
                    ''' shutdown '''  
                    LOG.debug("local core connector %s is stop %s"%(self.coreName,self.running))
                time.sleep(1)
            else:
                LOG.info("local core connector %s is shutdown"%(self.coreName))
        except:
            LOG.critical("local core connector %s is shutdown with error"%(self.coreName))
            
    def stop(self):
        '''
        stop the local Core client
        
        exception: localCoreException
        '''
        try:
            LOG.critical("stop local core connection %s"%(self.coreName))
            self.running=False
        except:
            raise defaultEXC("can't shutdown remote core connection %s"%(self.coreName))
        
    def shutdown(self):
        '''
        shutdown the local Core client
        
        exception: localCoreException
        '''
        try:
            if self.running:
                self.stop()
            LOG.critical("shutdown local core connection %s"%(self.coreName))
            self.ifShutdown=True
        except:
            raise defaultEXC("can't shutdown local core connection %s"%(self.coreName))     
    
    def __blockServer(self):
        '''
            block the server for new connections
            
            exception: none
        '''
        LOG.error("block remote core server %s for %i sec"%(self.coreName,self.__config['blocked']))
        self.__blockTime=self.__config['blocked']+int(time.time())   
    
    def __unblockClient(self):
        '''
            unblock connection to client
        
            exception: none
        ''' 
        LOG.info("unblock core connector %s"%(self.coreName))
        self.__blockTime=0
    
    def __closeSocket(self,networkSocket,clientIP):
        ''' 
            close the server socket 
            
            networkSocket: intance of the network socket
            clientIP: remote client IP
        '''
        try:
            if not networkSocket:
                return
            networkSocket.close()
        except:                             
            LOG.info("can't close socket on local core %s for remote client %s"%(self.coreName,clientIP))
        
        LOG.warning("close local core socket %s from %s ip"%(self.coreName,clientIP))
    
    def __clientRequest(self,clientSocket,remoteCoreIP,remoteCoreprotocol):
        '''
            get a client request from remote core
            
            clientCocket: instance of the client socket
            remoteCoreIP: IP adress from the client
            
            exception: defaultEXC
        '''
        try:
            LOG.debug("get new client request from %s on %s"%(remoteCoreIP,self.coreName))
            while self.running and not self.ifShutdown:
                remoteCoreprotocol.reciveData(clientSocket,remoteCoreIP)
        
        except (protocolException,cryptException) as e:
            LOG.warning("protocol or cryption error: on local core %s from remote ip %s : %s"%(self.coreName,remoteCoreIP,e.msg))
        except:
            LOG.warning("unkown error  on local core %s from remote ip %s "%(self.coreName,remoteCoreIP),exc_info=True)
        LOG.debug("close client request from %s on %s"%(remoteCoreIP,self.coreName))
        self.__closeSocket(clientSocket,remoteCoreIP)     
    
    def __buildSocket(self,ip,port):
        '''
        build a socket connection
        
        fetch exception
        '''
        try:
            networkSocket=socket.socket (socket.AF_INET, socket.SOCK_STREAM)
            networkSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            networkSocket.bind((ip,port))
            networkSocket.setblocking(0)
            networkSocket.listen(20)
            LOG.debug("local core lissen on interface %s, port %s on local core server %s"%(ip,port,self.coreName))
            return networkSocket
        except :
            raise defaultEXC("can not build socket ip:%s:%s on remote server %s"%(ip,port,self.coreName),True)        