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
import queue

# Local apllication constant
from .syncException import remoteCoreException,protocolException
from .protocol.encryption.cryptException import cryptException

'''
core protokol
'''
from .protocol.version1 import version1
from .protocol.version2 import version2
CORE_PROTOCOL={
             1:version1,
             2:version2
            }



LOG=logging.getLogger(__name__) 

class remoteCore(threading.Thread):
    
    def __init__(self,core,coreID,cfg):
        threading.Thread.__init__(self)
        
        ''' 
        configuration 
        '''
        self.config={
            "remoteCore":coreID,
            "blocked": 10,
            "ip": "0.0.0.0",
            "port": 5091,
            "protocol":{
                "version":1
                }
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
        
        ''' core queue '''
        self.__coreQueue=queue.Queue()
        
        ''' sync queue '''
        self.__syncQueue=queue.Queue()
        
        ''' set cor is not sync '''
        self.coreStatusSync=False
        
        ''' check core protocol'''
        if not self.config['protocol']['version'] in CORE_PROTOCOL:
            self.logger.error("protocol version %s is not avaible option, set to 1"%(self.config['protocol']['version']))
            self.config['protocol']['version']=1 
            
        LOG.info("init new remote core server %s version: %s"%(self.coreID,__version__))
    
    def run(self):
        try:
            LOG.info("%s start as remote core"%(self.coreID))
            while not self.ifShutdown:
                ''' running or stop '''
                coreProtocol=False
                while self.running:
                    try:
                        if self.__blockTime<time.time():
                            if not coreProtocol:
                                protocolCFG={"encryption":self.config['protocol']['encryption'],
                                             "remoteCore":self.coreID,
                                             "blocked":self.config["blocked"],
                                             "ip": self.config["ip"],
                                             "port":self.config["port"]
                                             }
                                coreProtocol=CORE_PROTOCOL[self.config['protocol']['version']](protocolCFG,self.__core,self.running)
                                self.__syncClient(coreProtocol)
                    except Exception as e:
                        LOG.error("remote core connection %s is stop: %s"%(self.coreID,e))
                        self.__blockServer()
                        coreProtocol=False
                        self.__setCoreNotSync()
                        
                    time.sleep(0.5)
                ''' shutdown '''    
                time.sleep(0.5)
            LOG.info("remot core connection %s is shutdown"%(self.coreID))
        except:
            LOG.error("remote core %s is stop with error"%(self.coreID))
    
    def __clearCoreQueue(self):
        '''
        ' clear the core Queue
        ' 
        ' exception: remoteCoreException
        '
        '''
        try:
            LOG.info("clear core queue")
            self.__coreQueue.queue.clear()
        except:
            raise remoteCoreException("can't clear coreQueue to host %s"%(self.coreID),True)

    def __syncClient(self,remoteCoreProtokol):
        '''
        '
        '    sync all object to remotecore
        '
        '    exception:    remoteCoreException
        '                  
        '''
        try:
            LOG.info("try to sync for core client %s"%(self.coreID))
            self.__clearCoreQueue()          
            self.__syncQueue.queue.clear()
            '''
            sync core module
            '''
            #self.__syncCoreModule()
            #self.__syncCoreDevices()
            #self.__syncCoreGateways()
            self.__syncCoreClients()
            if not self.__syncQueue.empty():        
                self.__workingQueue(remoteCoreProtokol,self.__syncQueue)
            self.__unblockClient()
            self.__setCoreIsSync()
            LOG.info("finish with sync to core %s"%(self.coreID))
        except :
            raise remoteCoreException("can't sync client to core %s"%(self.coreID))
    
    def __syncCoreClients(self):
        '''
        sync all core clients from this host
        '''
        try:
            LOG.info("sync CoreClients to host %s"%(self.coreID))
            for coreName in self.__core.coreCluster:
                if not self.__core.ifonThisHost(coreName):
                    continue
                args=(coreName,self.__core.coreCluster[coreName]['config'])
                updateObj={
                            'objectID':coreName,
                            'callFunction':'updateCoreConnector',
                            'args':args}
                
                self.__syncQueue.put(updateObj)
        except:
            raise remoteCoreException("can't sync coreClients to host %s"%(self.coreID),True)
    
    
    def __workingQueue(self,remoteCoreProtokol,jobQueue):
        '''
        ' send all job
        '
        '    remotoCoreProtokol: object    protokol object 
        '    jobQueue:           dict     a dictnory with jobs
        '
        '    exception:   cryptException
        '                 protokolException
        '                 remoteCoreException
        '
        '''
        try:
            LOG.debug("work for queue to core %s"%(self.coreID))
            while not jobQueue.empty():
                remoteCoreProtokol.sendJob(jobQueue.get())
        except:
            raise remoteCoreException("can't work on queue for client to core %s"%(self.coreID),False)
            
    def __setCoreIsSync(self):
        '''
        '
        '   set staus sync to true
        '
        '   exception: none
        '
        '''
        LOG.info("core client to core %s is syncron"%(self.coreID))
        self.coreStatusSync=True
    
    def __setCoreNotSync(self):
        '''
        '   set staus sync to false
        '
        '   exception: none
        '
        '''
        LOG.info("core client to core %s is not syncron"%(self.coreID))
        self.coreStatusSync=False
    
    def __blockServer(self):
        '''
        block the server for new connections
        '''
        LOG.error("block remote core server %s for %i sec"%(self.coreID,self.config['blocked']))
        self.__blockTime=self.config['blocked']+int(time.time())
    
    def __unblockClient(self):
        '''
        '
        '    unblock connection to client
        '
        '    exception: none
        '
        ''' 
        LOG.info("unblock core client %s"%(self.coreID))
        self.__clientBlocked=0
        
    def stop(self):
        '''
        stop the remote Core client
        
        exception: remoteCoreException
        '''
        try:
            LOG.critical("stop remote core connection %s"%(self.coreID))
            self.running=False
        except:
            raise remoteCoreException("can't shutdown remote core connection %s"%(self.coreID))
        
    def shutdown(self):
        '''
        shutdown the remote Core client
        
        exception: remoteCoreException
        '''
        try:
            if self.running:
                self.stop()
            LOG.critical("shutdown remote core connection %s"%(self.coreID))
            self.ifShutdown=True
        except:
            raise remoteCoreException("can't shutdown remote core connection %s"%(self.coreID))