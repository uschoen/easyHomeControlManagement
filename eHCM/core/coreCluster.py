'''
Created on 01.12.2021

@author: uschoen
'''
__version__='0.9'
__author__ = 'ullrich schoen'

# Standard library imports
import logging
import os
from datetime import datetime
import time
import copy
import threading

# Local application imports
from .exception import defaultEXC
from .cluster.localCore import localCore
from .cluster.remoteCore import remoteCore

LOG=logging.getLogger(__name__)

class coreCluster():
    '''
    core events function
    '''
    def __init__(self,*args):
        
        
        self.coreCluster={}
        
        LOG.info("init core cluster finish, version %s"%(__version__))
    
    def updateRemoteCore(self,forceUpdate,objectID,calling,*args):
        '''
            update remote core
            
            forceUpdate true/false , if true update even is job not from this host
            objectID: opjectID like xbvhd@hosname.de
            calliing: remote function to call
            *args: dic for function vars
            
            exception: none, only LOG entry
        '''
        try:
            if not forceUpdate:
                '''
                if forceUpdate False check if device on this host
                if forceUpdtae True send to all remote host
                '''
                if not self.ifonThisHost(objectID):
                    '''
                    if device not on this host do nothing
                    '''
                    return 
                     
            for coreName in self.coreCluster:
                try:
                    if not self.ifonThisHost(coreName): 
                        ''' remote Core '''
                        if self.coreCluster[coreName]['enable']==False:
                            continue
                        self.coreCluster[coreName]['instance'].updateRemoteCore(objectID,calling,args)
                except:
                    LOG.error("can not update remote core queue: %s"%(coreName),exc_info=True)
        except:
            LOG.error("can not update any core",exc_info=True)
    
    def updateCoreConnector(self,objectID,connectorCFG,forceUpdate=False):
        '''
        update a Core connector
        
        objectID:        core objectID
        connectorCFG:    configuration
        
        exception: defaultEXC
        '''
        try:
            LOG.info("try to update core cluster %s"%(objectID))
            if objectID in self.coreCluster:
                if self.coreCluster[objectID]['config']==connectorCFG:
                    LOG.info("core cluster %s has the same configuration, nothing to update"%(objectID))
                    return
                self.__deleteCoreConnector(objectID )
            self.__buildCoreConnector(objectID,connectorCFG)
            self.__startCoreConnector(objectID)
            self.updateRemoteCore(forceUpdate,objectID,self.thisMethode(),objectID,connectorCFG)
        except:
            raise defaultEXC("some unkown error in %s"%(self.thisMethode()))
    
    def ifKnownCoreClient(self,clientIP):
        '''
            check if the ip a known client for a client connection
            
            clientIP= ip adress to check
            
            return: true if known / fals if unkown
            
            exception: defaultEXC
        '''    
        try:
            for clusterName in self.coreCluster:
                if clientIP == self.coreCluster[clusterName]["clientIP"]:
                    return True
            return False
            
        except:
            raise defaultEXC("some unknown error in ifKnownCoreClient",True)
            
            
    def _writeClusterConfiguration(self,fileNameABS):
        '''
        
        internal funtion to write the cluster configuration on the file system
         
        fileNameABS: the absolut path of the file
        
        exception: deviceException,defaultEXC
        '''
        try:
            if len(self.coreCluster)==0:
                LOG.info("can't write core cluster configuration, is empty")
                return
            if not self.ifFileExists(fileNameABS):
                if not self.ifPathExists(os.path.dirname(fileNameABS)):
                    self.makeDir(os.path.dirname(fileNameABS))
            LOG.info("save cluster configuration %s"%(fileNameABS))
           
            CFGfile={"version":__version__,
                    "from":int(time.time())
                    }
            for objectID in self.coreCluster:
                CFGfile[objectID]=self.coreCluster[objectID]['config']
            self.writeJSON(fileNameABS,CFGfile)
        except:
            raise defaultEXC("can't write core cluster configuration")
    
    def __stopClusterConnector(self,objectID):
        '''
        stop a cluster connection    
        
        objectID: objectID from the cluster
        
        exception: defaultEXC
        '''
        if self.coreCluster[objectID]['running']==False:
            return
        try:
            LOG.warning("stop cluster connection %s"%(objectID))
            self.coreCluster[objectID]['instance'].stop() 
            self.coreCluster[objectID]['running']=False
        except:
            raise defaultEXC("can not stop cluster connection %s"%(objectID))
    
    def _shutdownAllCluster(self):
        '''
        internal function to stop all Core Cluster
        
        exception: defaultEXC
         
        ''' 
        try:
            LOG.warning("core %s is shutdown all cluster connections"%(self.host))
            for clusterName in self.coreCluster:   
                try:
                    threading.Thread(target=self.__shutdownCluster,args=(clusterName,)).start()
                except:
                    LOG.error("can't shutdown cluster connection %s"%(clusterName))
            
            
        except:
            raise defaultEXC("some unkown error in %s"%(self.thisMethode()))
        
    def __shutdownCluster(self,objectID):
        '''
            shutdown a cluster connection
            
            objectID: objectID from the connector
            
            exception: defaultEXC
        '''   
        if self.coreCluster[objectID]['shutdown']==True:
            return
        try:
            if self.coreCluster[objectID]['running']:
                self.__stopClusterConnector(objectID)
            LOG.warning("start to shutdown cluster connection %s"%(objectID))
            if self.coreCluster[objectID]['instance']:
                if self.coreCluster[objectID]['instance'].isAlive():
                    self.coreCluster[objectID]['instance'].shutdown() 
                    self.coreCluster[objectID]['instance'].join(5)
            self.coreCluster[objectID]['shutdown']=True
        except:
            raise defaultEXC("can't shutdown cluster connection %s"%(objectID))
    
    def __deleteCoreConnector(self,objectID):
        '''
            delete a remote core connection. If the connector running it will be stop.
            
            objectID:    objectID from the connector
            
            exception: clusterException
        '''
        try:
            LOG.info("delete remote core connector %s"%(objectID)) 
            if objectID in self.coreCluster:
                if self.coreCluster[objectID]['running']==True:
                    self.__stopClusterConnector(objectID)
                if self.coreCluster[objectID]['shutdown']==False:
                    self.__shutdownCluster(objectID)
                del self.coreCluster[objectID]
            else:
                LOG.error("can't find core connection %s to stop"%(objectID))
        except:
            raise defaultEXC("can't delete remote core %s"%(objectID))
           
    def __restoreCoreConnector(self,objectID,connectorCFG):
        '''
            restor a core connector
            
            objectID:      core objectID
            connectorCFG : configuration
            
            exception: clusterException
        '''
        try:
            LOG.info("try to restore core cluster %s"%(objectID))
            if objectID in self.coreCluster:
                self.__deleteCoreConnector(objectID )
            self.__buildCoreConnector(objectID,connectorCFG)
            self.__startCoreConnector(objectID)
        except:
            raise defaultEXC("some unkown error in %s"%(self.thisMethode()))
    
    def __startCoreConnector(self,objectID):
        '''
            start a core connection
             
            objectID: core obectID
            
            exception: defaultEXC
        '''
        if not self.coreCluster[objectID]['enable']:
                LOG.warning("can't start core connection %s, core connector is disable"%(objectID))
                return
        try:
            LOG.info("start core connection %s"%(objectID))
            self.coreCluster[objectID]['instance'].start() 
            self.coreCluster[objectID]['running']=True
            self.coreCluster[objectID]['shutdown']=False
        except:
            raise defaultEXC("can't start core connection %s"%(objectID))
    
        
    def _loadClusterConfiguration(self,fileNameABS=None):
        '''
            load the cluster configuaion from a file
            
            fileNameABS: the absolut path of the filename to load
            
            Exception: defaultEXC
        '''
        try:
            if not self.ifFileExists(fileNameABS):
                if not self.ifPathExists(os.path.dirname(fileNameABS)):
                    self.makeDir(os.path.dirname(fileNameABS))
                LOG.info("create new file %s"%(fileNameABS))
                self.writeJSON(fileNameABS,{"version": __version__,"from":int(time.time())})
            LOG.info("load cluster configuration %s"%(fileNameABS))
            CFGFile={
                "version":"UNKOWN",
                "from":0
                }
            CFGFile.update(self.loadJSON(fileNameABS))
            LOG.info("cluster configuration file has version: %s from %s"%(CFGFile['version'],datetime.fromtimestamp(CFGFile['from'])))
            del(CFGFile['version'])
            del(CFGFile['from'])
            if len(CFGFile)==0:
                LOG.info("cluster configuration file is empty")
                return
            
            for coreName in CFGFile:
                try:
                    self.__restoreCoreConnector(coreName, CFGFile[coreName])
                except:
                    LOG.error("can't restore cluster  configuration %s"%(coreName),exc_info=True)
        except:
            raise defaultEXC ("can't loadClusterConfiguration")
        
    def __buildCoreConnector(self,objectID,connectionCFG={},syncStatus=False):
        '''
            add a core connector as server or client
            
            objectID:  the core name of the client (name@hostname)
            coreCFG:   Configuration of the core connector
            syncStatus true/false if true it set the status to the core to is sync
            
            Exception: clusterException
        '''
        if objectID in self.coreCluster:
            raise defaultEXC("core connection%s exists"%(objectID),False)
        
        try:
            LOG.info("try to build remote/local core connection %s"%(objectID))
            defaultConfig={ 
                        "enable":False,
                        "hostName": objectID, 
                        "config":{}
                    }
            defaultConfig.update(copy.deepcopy(connectionCFG))
            ''' 
            cor connection container 
            '''
            defaultConfig['config']['enable']=defaultConfig['enable']
            self.coreCluster[objectID]={
                        'config':defaultConfig,
                        'instance':False,
                        'enable':defaultConfig['enable'],
                        'running':False,
                        'shutdown':True,
                        'clientIP':connectionCFG['config'].get("ip", "127.0.0.1")        
                }
            if self.ifonThisHost(objectID):
                '''
                build local core connection
                '''
                LOG.info("local core connection is build for %s"%(objectID))
                self.coreCluster[objectID]['instance']=localCore(self,objectID,defaultConfig['config'])
                self.coreCluster[objectID]['instance'].daemon=True   
            else:
                '''
                build core Client
                '''
                LOG.info("remote core connection is build for %s"%(objectID))
                self.coreCluster[objectID]['instance']=remoteCore(self,objectID,defaultConfig['config'])
                self.coreCluster[objectID]['instance'].daemon=True
                
        except:
            self.coreCluster[objectID]['enable']=False
            self.coreCluster[objectID]['instance']=False
            self.coreCluster[objectID]['running']=False
            self.coreCluster[objectID]['shutdown']=True
            raise defaultEXC("can not core connection %s"%(objectID))