'''
Created on 08.02.2022

@author: uschoen
'''


__version__='9.0'
__author__ = 'ullrich schoen'

# Standard library imports
import logging
import threading
import time
import socket
import queue

# local library imports
from core.exception import defaultEXC
from .protocol.version1  import version1
from .protocol.protocolException import protocolException
from .protocol.encryption.cryptException import cryptException

CORE_protocol={
             1:version1
            }

DEFAULT_CFG={"blocked":60,
             "enable":False,
             "port":9000,
             "protocol":{"version":1}}

LOG=logging.getLogger(__name__) 


class remoteCore(threading.Thread):
    
    def __init__(self,core,coreName,cfg):
        '''
        init remote core connector
        
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
        self.__config=DEFAULT_CFG
        self.__config.update(cfg)
        
        '''
            connector running
        '''
        self.running=self.__config['enable']
        
        '''
            core block for x sec
        '''
        self.__blockTime=0
        
        '''
            core sync status
        '''
        self.coreStatusSync=False
        
        '''
            network socket
        '''
        self.__networkSocket=False
           
        ''' 
            core queue, for core jobs
        '''
        self.__coreQueue=queue.Queue()
        
        '''
            sync queue, for sync jobs
        '''
        self.__syncQueue=queue.Queue()
        
        '''
            add coreprotocol version
            default or wrong value, 1
        '''
        self.__coreProtocol={
                        1:version1
                      }
        if not self.__config['protocol']['version'] in self.__coreProtocol:
            LOG.error("protocolVersion %s is not avaible option, set to verion 1"%(self.__config['protocol']['version']))
            self.__config['protocol']['version']=1 
        self.__remoteCoreProtocol=False
        
        LOG.info("init new remote core server %s version %s"%(self.coreName,__version__))

    def run(self):
        try:
            LOG.info("%s start"%(self.coreName))
            while not self.ifShutdown:
                ''' running or stop '''
                while self.running:
                    try:
                        if self.__blockTime<int(time.time()):
                            if not self.__remoteCoreProtocol:
                                self.__remoteCoreProtocol=self.__coreProtocol[self.__config['protocol']['version']](self.core,self.__config['protocol'],self.running)
                                self.__networkSocket=self.__buildSocket(self.__config["ip"],self.__config['port'])
                                self.__syncRemoteCore()
                            if not self.__coreQueue.empty():
                                self.__workingQueue(self.__networkSocket,self.__coreQueue)    
                    except (defaultEXC,protocolException,cryptException):
                        self.__blockServer()
                        self.__remoteCoreProtocol=False   
                        self.__setCoreNotSync()
                        self.__closeSocket(self.__networkSocket,self.__config["ip"])
                        LOG.error("close connecion to %s and try again in %i sec"%(self.coreName,self.__config['blocked']))           
                    except:
                        self.__blockServer()
                        self.__remoteCoreProtocol=False   
                        self.__setCoreNotSync()
                        self.__closeSocket(self.__networkSocket,self.__config["ip"])
                        LOG.error("close connecion to %s and try again in %i sec"%(self.coreName,self.__config['blocked']),exc_info=True) 
                else:
                    ''' shutdown '''  
                    self.__closeSocket(self.__networkSocket,self.__config["ip"])
                    LOG.info("remote core connector %s is stop"%(self.coreName))
                time.sleep(1)
            else:
                LOG.info("remote core connector %s is shutdown"%(self.coreName))
        except:
            LOG.critical("remote core connector %s is shutdown with error"%(self.coreName))
            
    def __workingQueue(self,networkSocket,jobQueue):
        '''
        ' send all job
        '
        '    remotoCoreProtocol: object    protocol object 
        '    jobQueue:           dict     a dictnory with jobs
        '
        '    exception:   cryptException
        '                 protocolException
        '                 remoteCoreException
        '
        '''
        try:
            LOG.debug("work for queue to core %s"%(self.coreName))
            while not jobQueue.empty():
                self.__remoteCoreProtocol.sendJob(networkSocket,jobQueue.get())
        except (protocolException,cryptException) as e:
            raise e
        except:
            raise defaultEXC("unkown error in %s"%(self.core.thisMethode()),True)
    
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
    
    def __buildSocket(self,ip,port):
        '''
        open a network socket to a core
        
        ip:ip adress oft the server
        port: port of the server
        
        eyception: defaultEXC
        '''
        try:
            LOG.debug("try connect to remote core %s:%s"%(ip,port))
            clientSocket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            clientSocket.connect((ip,port))
            return clientSocket
        except (socket.error,ConnectionRefusedError):
            raise defaultEXC ("can't open socket to remote core %s:%s"%(ip,port))
        except:
            raise defaultEXC("unkown error in buildSocket ip:%s:%s on remote core %s"%(ip,port,self.coreName),True)
    
    def __syncRemoteCore(self):
        '''
        '
        '    sync all object to remote core
        '
        '    exception:    defaultEXC,protocolException,cryptException
        '                  
        '''
        try:
            LOG.info("try to sync for core client %s"%(self.coreName))
            self.__clearCoreQueue()          
            self.__clearSyncQueue()
            self.__syncCoreModule()
            self.__syncCoreDevices()
            self.__syncCoreCluster()
            while not self.coreStatusSync:
                if self.__syncQueue.empty():
                    break
                self.__workingQueue(self.__networkSocket,self.__syncQueue)
            LOG.info("finish with sync to core %s"%(self.coreName))
            self.__unblockClient()
            self.__setCoreIsSync()
        except (protocolException,cryptException) as e:
            raise e
        except:
            raise defaultEXC("unkown error in %s"%(self.core.thisMethode()),True)
        
    def __setCoreIsSync(self):
        '''
        '
        '   set staus sync to true
        '
        '   exception: none
        '
        '''
        LOG.info("core client to core %s is syncron"%(self.coreName))
        self.coreStatusSync=True
        
    def __syncCoreCluster(self):
        '''
        sync all core clients from this host
        '''
        try:
            LOG.info("sync core cluster to host %s"%(self.coreName))
            for coreName in self.core.coreCluster:
                if not self.core.ifonThisHost(coreName):
                    continue
                args=(coreName,self.core.coreCluster[coreName]['config'])
                updateObj={
                            'objectID':coreName,
                            'callFunction':'updateCoreConnector',
                            'args':args}
                self.__syncQueue.put(updateObj)
        except:
            raise defaultEXC("some unkown error in %s"%(self.core.thisMethode()),True)
    
    
    def __syncCoreModule(self):
        '''
        sync all comodulere  from this host
        
        exception: defaultEXC
        '''
        return
        try:
            LOG.info("sync module to host %s"%(self.coreName))
            for objectID in self.core.getAllModulNames():
                if not self.core.ifonThisHost(objectID):
                    continue
                updateObj={
                        'objectID':objectID,
                        'callFunction':'restoreModul',
                        'args':(objectID,self.core.getModulConfiguration(objectID))}
                self.__syncQueue.put(updateObj)
        except:
            raise defaultEXC("unkown error in %s"%(self.core.thisMethode()),True)
    
    def __syncCoreDevices(self):
        '''
        sync all devices from this host
        '''
        try:
            LOG.info("sync devices to core %s"%(self.coreName))
            for deviceID in self.core.getAllDeviceID():
                if not self.core.ifonThisHost(deviceID):
                    continue
                LOG.info("sync devicesID %s to core %s"%(deviceID,self.coreName))
                device=self.core.getDeviceConfiguration(deviceID)
                args=(deviceID,device)
                updateObj={
                        'objectID':deviceID,
                        'callFunction':'restoreDevice',
                        'args':args}
                self.__syncQueue.put(updateObj)
        except:
            raise defaultEXC("unkown error in %s"%(self.core.thisMethode()),True)
        
    def __clearCoreQueue(self):
        '''
        ' clear the core Queue
        ' 
        ' exception: remoteCoreException
        '
        '''
        try:
            LOG.info("clear core queue from %s"%(self.coreName))
            self.__coreQueue.queue.clear()
        except:
            raise defaultEXC("some unkown error in %s"%(self.core.thisMethode()),True)
    
    def __clearSyncQueue(self):
        '''
        ' clear the Sync Queue
        ' 
        ' exception: defaultEXC
        '
        '''
        try:
            LOG.info("clear sync queue from %s"%(self.coreName))
            self.__syncQueue.queue.clear()
        except:
            raise defaultEXC("some unkown error in %s"%(self.core.thisMethode()),True)
        
    def stop(self):
        '''
        stop the remote Core client
        
        exception: defaultEXC
        '''
        try:
            LOG.critical("stop remote core connection %s"%(self.coreName))
            self.running=False
        except:
            raise defaultEXC("can't shutdown remote core connection %s"%(self.coreName))
    
    def updateRemoteCore(self,objectID,callFunction,args):
        '''
        '
        '    put a job in the work queue
        '
        '    objectID:     string    ObjectID like xxx@ddd
        '    callFunktion  string    function to call
        '    args:         dic       a list of arguments
        '
        '    exception: remoteCoreException
        '''
        try:
            if self.__blockTime>int(time.time()):
                LOG.info("remote core connector %s block for %i s"%(self.coreName,self.__blockTime-int(time.time())))
                return
            LOG.debug("putting job for objectID:%s callFunction:%s into queue from %s"%(objectID,callFunction,self.coreName))
            updateObj={
                        'objectID':objectID,
                        'callFunction':callFunction,
                        'args':args
                        }
            self.__coreQueue.put(updateObj)
        except:
            raise defaultEXC("can't put update in queue for objectID %s on remote client %s"%(objectID,self.coreName))
    
        
    def shutdown(self):
        '''
        shutdown the remote Core client
        
        exception: defaultEXC
        '''
        try:
            if self.running:
                self.stop()
            LOG.critical("shutdown remote core connection %s"%(self.coreName))
            self.ifShutdown=True
        except:
            raise defaultEXC("can't shutdown remote core connection %s"%(self.coreName))     
    
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
    
    def __setCoreNotSync(self):
        '''
        '   set staus sync to false
        '
        '   exception: none
        '
        '''
        LOG.info("core client to core %s is not syncron"%(self.coreName))
        self.coreStatusSync=False