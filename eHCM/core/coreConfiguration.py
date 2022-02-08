'''
Created on 01.12.2021

@author: uschoen
@TODO: ueberpruefen der load configuartion 
'''

__version__='0.9'
__author__ = 'ullrich schoen'

# Standard library imports
import logging
import os
import time
from datetime import datetime

# Local application imports
from .exception import defaultEXC

LOG=logging.getLogger(__name__)

class coreConfiguration():
    '''
    core events function
    '''
    def __init__(self,*args):
        LOG.info("init core configuration finish, version %s"%(__version__))
        
    def _writeAllConfiguration(self):
        '''
        internal function to save alle configuration to the filesystem
        
        exception: configurationException
        '''
        try:
            path=self.__getConfigurationPath()
            ##########
            # core
            ##########
            try:
                fileNameABS="%s/%s"%(path,self.args['configuration']['files']['core'])
                self._writeCoreConfiguration(fileNameABS)
            except:
                LOG.error("can't write core configuration file %s"%(fileNameABS),exc_info=False)
            ##########
            # logger
            ##########
            try:
                fileNameABS="%s/%s"%(path,self.args['configuration']['files']['logger'])
                self._writeLoggerConfiguration(fileNameABS)
            except:
                LOG.error("can't write logger configuration file %s"%(fileNameABS),exc_info=False)
            #########
            # devices
            #########
            try:
                fileNameABS="%s/%s"%(path,self.args['configuration']['files']['devices'])
                self._writeDeviceConfiguration(fileNameABS)
            except:
                LOG.error("can't write device configuration file %s"%(fileNameABS),exc_info=False)  
            #########
            # connector
            #########
            try:
                fileNameABS="%s/%s"%(path,self.args['configuration']['files']['module'])
                self._writeModulConfiguration(fileNameABS)
            except:
                LOG.error("can't write modul configuration file %s"%(fileNameABS),exc_info=False)
            #########
            # script
            #########
            try:
                fileNameABS="%s/%s"%(path,self.args['configuration']['files']['script'])
                self._writeScriptConfiguration(fileNameABS)
            except:
                LOG.error("can't write script configuration file %s"%(fileNameABS),exc_info=False)
                
            #########
            # cluster
            #########
            try:
                fileNameABS="%s/%s"%(path,self.args['configuration']['files']['cluster'])
                self._writeClusterConfiguration(fileNameABS)
            except:
                LOG.error("can't write cluster configuration file %s"%(fileNameABS),exc_info=True)         
        except:
            raise defaultEXC("some error, can't saveAllConfiguration to filesystem")
        
    def _loadAllConfiguration(self):
        '''
        internal function to load all configuration files
        
        exception: configurationException
        '''
        try:
            path=self.__getConfigurationPath()
            #########
            # core
            #########
            try:
                fileNameABS="%s/%s"%(path,self.args['configuration']['files']['core'])
                self._loadCoreConfiguration(fileNameABS)
            except:
                LOG.error("can't load core file %s"%(fileNameABS),exc_info=False)
            ##########
            # logging
            ##########
            try:
                fileNameABS="%s/%s"%(path,self.args['configuration']['files']['logger'])
                self._loadLoggerConfiguration(fileNameABS)
            except:
                LOG.error("can't load logger file %s"%(fileNameABS),exc_info=False)
            ##########
            # scripts
            ##########
            try:
                fileNameABS="%s/%s"%(path,self.args['configuration']['files']['script'])
                self._loadScriptConfiguration(fileNameABS)
            except:
                LOG.error("can't load script file %s"%(fileNameABS),exc_info=False)
            ##########
            # devices
            ##########
            try:
                fileNameABS="%s/%s"%(path,self.args['configuration']['files']['devices'])
                self._loadDeviceConfiguration(fileNameABS)
            except:
                LOG.error("can't load device file %s"%(fileNameABS),exc_info=False)
            ##########
            # cluster
            ##########
            try:
                fileNameABS="%s/%s"%(path,self.args['configuration']['files']['cluster'])
                self._loadClusterConfiguration(fileNameABS)
            except:
                LOG.error("can't load cluster configuration file %s"%(fileNameABS),exc_info=False)
            ##########
            # module
            ##########
            try:
                fileNameABS="%s/%s"%(path,self.args['configuration']['files']['module'])
                self._loadModulConfiguration(fileNameABS)
            except:
                LOG.error("can't load module file %s"%(fileNameABS),exc_info=False)
        except:
            raise defaultEXC("some error, can't loadAllConfiguration from filesystem")
    
    
    def _writeCoreConfiguration(self,fileNameABS):
        '''
        internal function to write the device configuration 
        
        fileNameABS=None    if none fileNameABS use deafult configuration
        
        if 0 devices in core configuration, no file written 
        '''
        try:
            ''' if no items exists skip '''
            if len(self.args)==0:
                LOG.info("can't write core configuration, lenght is 0")
                return
            
            ''' if path for file not exists, create '''
            if not self.ifPathExists(os.path.dirname(fileNameABS)):
                self.makeDir(os.path.dirname(fileNameABS))
            
            ''' save configuration '''
            CFGfile={
                "version":__version__,
                "from":int(time.time()),
                "config":self.args}
            LOG.info("save core configuration file %s"%(fileNameABS))
            self.writeJSON(fileNameABS,CFGfile)
        except:
            raise defaultEXC("can't write core configuration")
        
    def _loadCoreConfiguration(self,fileNameABS):
        '''
        internal function to load the cor configuration 
        
        fileNameABS=None    
        
        exception:
        
        if none fileNameABS raise exception
        if fileNameABS file not exist rasie exception
        '''
        try:
            ''' if file not exists and/or path create default file'''
            if not self.ifFileExists(fileNameABS):
                if not self.ifPathExists(os.path.dirname(fileNameABS)):
                    self.makeDir(os.path.dirname(fileNameABS))
                LOG.info("create new file %s"%(fileNameABS))
                self.writeJSON(fileNameABS,self.getCoreDefaults())
            
            ''' load json configuration file '''
            LOG.info("load core configuration file %s"%(fileNameABS))
            CFGFile={
                "version":"UNKOWN",
                "from":0,
                "config":{}}
            CFGFile.update(self.loadJSON(fileNameABS=fileNameABS))
            LOG.info("core configuration has version: %s from %s"%(CFGFile['version'],datetime.fromtimestamp(CFGFile['from'])))
            
            ''' check if core file empty, end skyp import '''
            if len(CFGFile['config'])==0:
                LOG.info("core configuration file is empty")
                return
            
            ''' save lokal parameters '''
            self.args=CFGFile['config']
        except:
            raise defaultEXC("can't read core configuration")
    
    def __getConfigurationPath(self):
        try:
            path="%s%s/%s"%(self.rootPath,self.args['configuration']['basePath'],self.args['configuration']['filePath'])
            return path
        except:
            raise defaultEXC("can't return configuration path")  