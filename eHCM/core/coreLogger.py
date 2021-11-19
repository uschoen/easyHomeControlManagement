'''
Created on 01.12.2021

@author: uschoen
'''

__version__='0.9'
__author__ = 'ullrich schoen'

# Standard library imports
import logging
import os

# Local application imports
from .exception import defaultEXC

LOG=logging.getLogger(__name__)


class coreLogger():
    '''
    core events function
    '''
    def __init__(self,*args):
        self.loggerConf={}
        LOG.info("init core logger modul version: %s"%(__version__))
    
    
    def writeLoggerConfiguration(self,objectID=None,fileNameABS=None,forceUpdate=False):
        '''
        internal function to write the logger configuration 
        
        objectID= host id to save
        fileNameABS=None
        
        exception: defaultEXC,defaultEXC
        '''
        try:
            if fileNameABS==None:
                raise defaultEXC("no filename given to write logger file")
            if objectID==None:
                objectID="logger@%s"%(self.host)
            if self.ifonThisHost(objectID):
                self._writeLoggerConfiguration(fileNameABS)
            else:
                self.updateRemoteCore(forceUpdate,objectID,'writeLoggerConfiguration',objectID,fileNameABS)
        except:
            raise defaultEXC("can't write logging configuration",True)
    
    def _writeLoggerConfiguration(self,fileNameABS):
        '''
        internal function to write the logger configuration 
        
        fileNameABS: the absolut path of the file
        
        exception: defaultEXC,defaultEXC
        
        '''
        try:
            if len(self.loggerConf)==0:
                LOG.info("can't write logger configuration, is empty")
                return
            if not self.ifFileExists(fileNameABS):
                if not self.ifPathExists(os.path.dirname(fileNameABS)):
                    self.makeDir(os.path.dirname(fileNameABS))
            LOG.info("save logger configuration %s"%(fileNameABS))
            self.writeJSON(fileNameABS,self.loggerConf)
        except:
            raise defaultEXC("can't write logging configuration",True)
    
    def loadLoggerConfiguration(self,objectID=None,fileNameABS=None,forceUpdate=False):
        '''
        internal function to load the logger configuration 
        
        fileNameABS=None
        
        exception:
        
        if none fileNameABS raise exception
        if fileNameABS file not exist rasie exception
        '''
        try:
            if fileNameABS==None:
                raise defaultEXC("no filename given to load core file")
            if objectID==None:
                objectID="logger@%s"%(self.host)
            if self.ifonThisHost(objectID):
                self._loadLoggerConfiguration(fileNameABS)
            else:
                self.updateRemoteCore(forceUpdate,objectID,'loadLoggerConfiguration',objectID,fileNameABS)
        except:
            raise defaultEXC("can't read logging configuration",True)
    
    def _loadLoggerConfiguration(self,fileNameABS):
        '''
        internal function to load the logger configuration 
        
        fileNameABS: the absolut path of the file
        
        exception: defaultEXC,defaultEXC
        
        '''
        try:
            if not self.ifFileExists(fileNameABS):
                if not self.ifPathExists(os.path.dirname(fileNameABS)):
                    LOG.info("create new directory %s"%(os.path.dirname(fileNameABS)))
                    self.makeDir(os.path.dirname(fileNameABS))
                    
                LOG.info("create new file %s"%(fileNameABS))
                self.writeJSON(fileNameABS,self.getLoggerDefaults())
                
            LOG.info("load logger configuration %s"%(fileNameABS))
            loggerCFG=self.loadJSON(fileNameABS)
            if len(loggerCFG)==0:
                LOG.info("logger configuration file is empty")
                return
            self.__applyLoggerConfiguration(loggerCFG,self.debugType)
            self.loggerConf=loggerCFG
        except (Exception) as e:
            raise defaultEXC("can't read logging configuration: %s"%(format(e)),True)
    
    def __applyLoggerConfiguration(self,loggerConf,logTyp="simple"):
        try:
            LOG.info("apply new logger configuration typ: %s"%(logTyp))
            if logTyp=="colored":
                import coloredlogs
                conf=loggerConf.get("colored")
                coloredlogs.DEFAULT_FIELD_STYLES = conf.get("FIELD_STYLES")
                coloredlogs.DEFAULT_LEVEL_STYLES = conf.get("LEVEL_STYLES")
                coloredlogs.DEFAULT_LOG_FORMAT='%s'%(conf.get("fmt"))
                coloredlogs.DEFAULT_LOG_LEVEL=conf.get("level","DEBUG")
                coloredlogs.install(milliseconds=conf.get("milliseconds",True))
            else:
                logging.config.dictConfig(loggerConf.get("simple",{}))
        except:
            raise defaultEXC("unkown error in __applyLoggerConfiguration",True)
