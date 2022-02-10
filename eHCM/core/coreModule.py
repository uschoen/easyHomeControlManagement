'''
Created on 01.12.2021

@author: uschoen
'''

DEFAULT_MODUL_PATH="modul"

__version__='0.9'
__author__ = 'ullrich schoen'

# Standard library imports
import logging
import os
from datetime import datetime
import time


# Local application imports
from .exception import defaultEXC

LOG=logging.getLogger(__name__)


class coreModule():
    '''
    core modul function
    '''
    def __init__(self,*args):
        
        '''
            self.module to store the module intance
        '''
        self.module={}
        
        LOG.info("init core module finish, version %s"%(__version__))
    
    def _writeModulConfiguration(self,fileNameABS):
        try:
            if len(self.module)==0:
                LOG.warning("can't write modul configuration, is empty")
                return
            if not self.ifFileExists(fileNameABS):
                if not self.ifPathExists(os.path.dirname(fileNameABS)):
                    self.makeDir(os.path.dirname(fileNameABS))
            LOG.info("save connector configuration %s"%(fileNameABS))
            modulCFG={
                "version":__version__,
                "from":int(time.time())
            }
            for modulName in self.module:
                '''
                @todo: if modul loading faild you can not retrive the Configuartion of the modul
                via getConfiguration, because no intance is avaibel.
                change this 
                '''
                modulCFG[modulName]={
                            "startable":self.module[modulName].get('startable',False),
                            "enable":self.module[modulName].get('enable',False),
                            "modulPackage":self.module[modulName].get('modulPackage',False),
                            "modulClass":self.module[modulName].get('modulClass',False)
                            }
                if self.ifonThisHost(modulName):
                    modulCFG[modulName]['config']=self.module[modulName]['instance'].getConfiguration()
                else:
                    modulCFG[modulName]['config']=self.module[modulName]['config']
                    
            self.writeJSON(fileNameABS,modulCFG)
        except (Exception) as e:
            raise defaultEXC("can't _writeModulConfiguration: %s"%(e)) 
    
    def _loadModulConfiguration(self,fileNameABS):
        '''
        internal function to load the device configuration 
        
        fileNameABS: the absolut path of the file
        
        exception: deviceException
        
        '''
        try:
            if not self.ifFileExists(fileNameABS):
                if not self.ifPathExists(os.path.dirname(fileNameABS)):
                    self.makeDir(os.path.dirname(fileNameABS))
                LOG.info("create new file %s"%(fileNameABS))
                self.writeJSON(fileNameABS,{"version": __version__,"from":int(time.time())})
            LOG.info("load modul configuration %s"%(fileNameABS))
            CFGFile={
                "version":"UNKOWN",
                "from":0
                }
            CFGFile.update(self.loadJSON(fileNameABS))
            LOG.info("modul configuration file has version: %s from %s"%(CFGFile['version'],datetime.fromtimestamp(CFGFile['from'])))
            if len(CFGFile)==0:
                LOG.info("moul configuration file is empty")
                return
            for objectID in CFGFile:
                try:
                    if objectID=="version" or objectID=="from":
                        continue
                    self.__restoreModul(objectID, CFGFile[objectID])
                except (defaultEXC) as e:
                    LOG.error("some error at restoreModul objectID %s"%(e.msg))
                except (Exception) as e:
                    LOG.error("unkown error _loadModulConfiguration %s"%(e))
        except (Exception) as e:
            raise defaultEXC("can't read modul configuration: %s"%(e),True)
        
    def __startModul(self,objectID):
        '''
        start a modul
         
        objectID: connector obectID
        
        exception: connectorException
        '''
        if not self.module[objectID]['enable']:
                LOG.error("can't start modul %s, is disable"%(objectID))
                return
        if not self.module[objectID]['startable']:
                LOG.error("modul %s is not startable"%(objectID))
                return
        try:
            LOG.debug("try to start modul %s"%(objectID))
            self.module[objectID]['instance'].startModul()
            self.module[objectID]['instance'].start() 
            self.module[objectID]['running']=True
            self.module[objectID]['shutdown']=False
        except:
            self.module[objectID]['enable']=False
            self.module[objectID]['running']=False
            self.module[objectID]['shutdown']=True
            raise defaultEXC("can not start modul %s"%(objectID),True)
    
    def __stopModul(self,objectID):
        try:
            LOG.warning("stop modul %s"%(objectID))
            self.module[objectID]['running']=False
            self.module[objectID]['instance'].stopModul()
        except:
            raise defaultEXC("some errer _stopModul modul %s"%(objectID),True) 
    
    def __shutDownModul(self,objectID):
        try:
            if (self.module[objectID]['running']):
                self.__stopModul(objectID)
            LOG.warning("shutdown modul %s "%(objectID))
            if not self.module[objectID]['shutdown']:
                self.module[objectID]['instance'].shutDownModul()
            self.module[objectID]['shutdown']=True
        except:
            raise defaultEXC("some error __shutdownModul modul %s"%(objectID),True) 
    
    def __deleteModul(self,objectID):
        '''
        delete a remote connector. If the connector running it will be stop.
        
        objectID:    objectID from the connector
        
        exception: connectorException
        '''
        try:
            LOG.info("delete connector %s"%(objectID)) 
            if objectID in self.module:
                if self.module[objectID]['running']==True:
                    self.__stopModul(objectID)
                if self.module[objectID]['shutdown']==False:
                    self.__shutdownModul(objectID)
                del self.module[objectID]
            else:
                LOG.error("can't find modul %s to stop"%(objectID))
        except:
            del self.module[objectID]
            raise defaultEXC("unkown error delete modul %s hard"%(objectID),True)
    
    def getAllModulNames(self):
        '''
            get all modul names back
            
            return: list with modul name
            
            exception: defaultEXC
        '''
        try:
            return self.module.keys()
        except:
            raise defaultEXC("some unkown error in %s"%(self.thisMethode()),True)
        
    def getModulConfiguration(self,objectID):
        '''
            update a Core connectorget the configuration from a modul back
            
            objectID:      core objectID
            
            return: dict
            
            exception: clusterException
        '''
        if objectID not in self.module:
            raise defaultEXC("can't find modul: %s"%(objectID))
        try:
            cfg={"startable":self.module[objectID].get('startable',False),
                 "enable":self.module[objectID].get('enable',False),
                 "modulPackage":self.module[objectID].get('modulPackage',False),
                 "modulClass":self.module[objectID].get('modulClass',False),
                 "config":self.module[objectID]['instance'].getConfiguration()
            }
            return cfg
        except:
            raise defaultEXC("some unkown error in %s"%(self.thisMethode()),True)
        
    def restoreModul(self,objectID,modulCFG={},forceUpdate=False):
        '''
                internale funtion to restore a Module
            
                objectID: Module ID
                modulfCFG    dict, modul configuration
                            modulCFG={  "config": {},
                                        "enable": false,
                                        "modulClass": "xml_api",
                                        "modulPackage": "homematic",
                                        "startable": false
                                    }
                exception: defaultEXC
        '''
        try:
            self.__restoreModul(objectID, modulCFG)
            self.updateRemoteCore(forceUpdate,objectID,self.thisMethode,objectID,modulCFG)
        except:
            raise defaultEXC("some unkown error in %s"%(self.thisMethode()),True)
        
    def __restoreModul(self,objectID,modulCFG={}):
            '''
                internale funtion to restore a Module
            
                objectID: Module ID
            
                exception: defaultEXC
            '''
            try:
                LOG.info("try to restore Module %s"%(objectID))
                if objectID in self.module:
                    self.__deleteModul(objectID )
                self.__buildModul(objectID,modulCFG)
                if self.ifonThisHost(objectID):
                    if (self.module[objectID]['startable']):
                        self.__startModul(objectID)
            except:
                raise defaultEXC("unkown error in %s"%(self.thisMethode()),True)
    
    
    def shutDownAllModule(self,hostID=None,forceUpdate=False):
        '''
        shutdown all module for the host ID
        '''
        try:
            if (hostID==None):
                hostID="core@%s"%(self.host)
            
            if self.ifonThisHost(hostID):
                LOG.warning("shutdown all module for core %s"%(hostID))
                for moduleName in self.module:
                    self.__shutDownModul(moduleName)
            else:
                self.updateRemoteCore(forceUpdate,hostID,'shutDownAllModule',hostID)
        except:
            raise defaultEXC("unkown error in %s"%(self.thisMethode()),True)
    
    def __buildModul(self,  
                      objectID,
                      modulCFG={}
                      ):
        '''
        add a core connector as server or client
        objectID:    the core name of the client (name@hostname)
        modulCFG:    Configuration of the modul
        syncStatus true/false if true it set the status to the core to is sync
        
        Exception: clusterException
        '''
        if objectID in self.module:
            raise defaultEXC("modul %s exists"%(objectID),False)
        try:
            LOG.info("try to build modul %s"%(objectID))
            self.module[objectID]={
                "startable":False,
                "enable":False,
                "modulPackage":False,
                "modulClass":False,
                "config":{},
                "instance":False,
                "running":False,
                "shutdown":True
                }
            self.module[objectID].update(modulCFG)
            self.module[objectID]['config']['gatewayName']=objectID.replace("@", ".")
            self.module[objectID]['config']['enable']=modulCFG.get('enable',False)
            
            if self.ifonThisHost(objectID):
                '''
                build local module
                '''
                classCFG={
                "objectID":objectID,
                "modulCFG":self.module[objectID]['config'],
                }
                LOG.info("connector is build for %s"%(objectID))
                package="%s.%s"%(DEFAULT_MODUL_PATH,self.module[objectID]['modulPackage'])
                self.module[objectID]['instance']=self.loadModul(objectID,package,self.module[objectID]['modulClass'],classCFG)
                self.module[objectID]['instance'].daemon=True   
        except:
            self.module[objectID]['enable']=False
            self.module[objectID]['instance']=False
            self.module[objectID]['running']=False
            self.module[objectID]['shutdown']=True
            raise defaultEXC("unkown error in %s"%(self.thisMethode()),True)
        