'''
Created on 18.03.2018

@author: uschoen
'''

__version__ = '9.0'

# Standard library imports
import logging
import os
from datetime import datetime
import time

# Local library imports
from core.script.exception import defaultError,cmdError,testError
from core.script.praraphser import praraphser

# defaults
#@var Global Logging intance
LOG=logging.getLogger(__name__)

class scriptManager():
    """
    script Manager to manage Scripts
    
       
    """
    def __init__(self,*args):
        
        self.scripts={}
        LOG.info("init core scriptmanager finish, version %s"%(__version__))
        
    def addScript(self,scriptName,script,forceUpdate=False):
        '''
            add a Script to core
            
            scriptName: strg  name of the script (name@host.de)
            script:     strg json string
            forceUpdate:    true/false(default) force update remote core
            
            exception: defaultError
        '''  
        try:
            self.__addScript(scriptName, script)
            self.updateRemoteCore(forceUpdate,scriptName,self.thisMethode(),scriptName,script)
        except:
            raise defaultError("unkown error in %s"%(self.thisMethode()),True)
    
    def __addScript(self,scriptName,script,test=False):
        try:
            LOG.debug("add script  %s"%(scriptName))
            self.scripts[scriptName]=script
        except:
            raise defaultError("unkown error in %s"%(self.thisMethode()),True)
    
    def updateScript(self,scriptName,script,forecUpdate=False):
        '''
        update a script
        '''
        try:
            pass
            self.updateRemoteCore(forecUpdate,scriptName,'updateScript',scriptName,script)
        except:
            raise defaultError("unkown error in %s"%(self.thisMethode()),True)
    
    def __restoreScript(self,scriptName,script):
        '''
        restore a program, only for restart/start
        '''
        try:
            LOG.debug("restore script %s"%(scriptName))
            if scriptName in self.scripts:
                self.__deleteScript(scriptName)
            self.__addScript(scriptName,script)
        except:
            raise defaultError("unkown error in %s"%(self.thisMethode()),True)
        
    def restoreScript(self,scriptName,script,forceUpdate=False):
        '''
        restore a script
        '''
        try:
            self.__restoreScript(scriptName, script)
            self.updateRemoteCore(forceUpdate,scriptName,'restoreScript',scriptName,script)
        except:
            raise defaultError("unkown error in %s"%(self.thisMethode()),True)
        
    def _writeScriptConfiguration(self,fileNameABS):
        '''
        internal function to write the devices configuration 
        
        fileNameABS: the absolut path of the file
        
        exception: deviceException,defaultEXC
        
        '''
        try:
            if len(self.scripts)==0:
                LOG.warning("can't write script configuration, scripts are empty")
                return
            if not self.ifFileExists(fileNameABS):
                if not self.ifPathExists(os.path.dirname(fileNameABS)):
                    self.makeDir(os.path.dirname(fileNameABS))
            LOG.info("save script configuration %s"%(fileNameABS))
            scriptCFG={
                "version":__version__,
                "from":int(time.time())
            }
            for scriptID in self.scripts:
                scriptCFG[scriptID]=self.scripts[scriptID]
            self.writeJSON(fileNameABS,scriptCFG)
        except:
            raise defaultError("unkown error in %s"%(self.thisMethode()),True)
    
    def _loadScriptConfiguration(self,fileNameABS):
        '''
        internal function to load the script configuration 
        
        fileNameABS: the absolut path of the file
        
        exception: deviceException,defaultEXC
        
        '''
        try:
            if not self.ifFileExists(fileNameABS):
                if not self.ifPathExists(os.path.dirname(fileNameABS)):
                    self.makeDir(os.path.dirname(fileNameABS))
                LOG.info("create new file %s"%(fileNameABS))
                self.writeJSON(fileNameABS,{"version": __version__,"from":int(time.time())})
            LOG.info("load script configuration %s"%(fileNameABS))
            CFGFile={
                "version":"UNKOWN",
                "from":0
                }
            CFGFile.update(self.loadJSON(fileNameABS))
            LOG.info("script configuration file has version: %s from %s"%(CFGFile['version'],datetime.fromtimestamp(CFGFile['from'])))
            
            if len(CFGFile)==0:
                LOG.info("script configuration file is empty")
                return
            for scriptName in CFGFile:
                try:
                    if scriptName=="version" or scriptName=="from":
                        continue
                    self.__restoreScript(scriptName,CFGFile[scriptName])
                except (defaultError) as e:
                    LOG.error("some error at restoreScript: %s"%(e.msg))
                except:
                    LOG.critical("unkown error at restoreScript",exc_info=True)
        except:
            raise defaultError("unkown error in %s"%(self.thisMethode()),True)
        
    def runScript(self,scriptName,script=None,callerObject=None,callerVars={},programDeep=0,forceUpdate=False):
        try:
            if self.ifonThisHost(scriptName):
                LOG.debug("run script name: %s , with script: %s"%(scriptName,script))
                if script==None:
                    LOG.debug("no script was given, load script %s"%(scriptName))
                    if scriptName in self.scripts:
                        script=self.scripts[scriptName]
                    else:
                        LOG.error("can't not find script %s"%(scriptName))
                        raise defaultError("can't not find script %s"%(scriptName), False)
                
                p=praraphser(core=self,
                             callerObject=callerObject,
                             callerVars=callerVars)
                
                p.runScript(script=script,
                            programDeep=programDeep)
                return p
            else:
                LOG.debug("script %s is not at this host %s"%(scriptName.self.host))
                '''
                update remote core
                '''
                self.updateRemoteCore(forceUpdate,scriptName,self.thisMethode,scriptName,script,callerObject,callerVars,programDeep)

        except (defaultError,cmdError,testError) as e:
            raise e
        except:
            raise defaultError("unkown error in %s"%(self.thisMethode()),True)
   
    def deleteScript(self,scriptName,forecUpdate=False):
        try:
            self.__deleteScript(scriptName)
            self.updateRemoteCore(forecUpdate,scriptName,'deleteScript',scriptName)
        except:
            raise defaultError("unkown error in %s"%(self.thisMethode()),True)
    
    def __deleteScript(self,scriptName):
        try:
            if not scriptName in self.scripts:
                return
            LOG.info("delete script %s"%(scriptName))
            del self.scripts[scriptName]
        except:
            raise defaultError("unkown error in %s"%(self.thisMethode()),True)

    
    