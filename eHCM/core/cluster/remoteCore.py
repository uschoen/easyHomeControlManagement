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

DEFAULT_CFG={"blocked":60,
             "enable":False,
             "port":9000}

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
            core queue, for core jobs
        '''
        self.__coreQueue=queue.Queue()
        
        LOG.info("init new remote core server %s version %s"%(self.coreName,__version__))

    def run(self):
        try:
            LOG.info("%s start"%(self.coreName))
            while not self.ifShutdown:
                ''' running or stop '''
                while self.running:
                    try:
                        pass
                    except:
                        pass
                        self.stop()
                    time.sleep(0.5)
                else:
                    ''' shutdown '''  
                    LOG.info("remote core connector %s is stop"%(self.coreName))
                time.sleep(1)
            else:
                LOG.info("remote core connector %s is shutdown"%(self.coreName))
        except:
            LOG.critical("remote core connector %s is shutdown with error"%(self.coreName))
            
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
            if self.__blockTime<int(time.time()):
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
        self.__clientBlocked=0
            