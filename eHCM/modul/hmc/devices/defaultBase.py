'''
Created on 14.12.2020

@author: uschoen
'''

__version__ = '8.1'
__author__ = 'ullrich schoen'

# Standard library imports
import logging
import os

# Local application imports
from core.exception import defaultEXC
from .defaultDevice import DEVICE_BASE_PATH
from .defaultDevice import DEFAULT_CONFIGURATION_FILE


LOG=logging.getLogger(__name__)
class deviceBase():
    
    def __init__(self):
        '''
        confonfiuration file
        '''
        #self.configFile=os.path.normpath("%s/%s/%s/devices/%s.json"%(self.path,DEVICEBASEPATH,devicePackage.replace(".","/"),deviceType))
        self.configFile=os.path.normpath("%s/%s/%s/devices/%s.json"%(self.core.rootPath,DEVICE_BASE_PATH,self.devicePackage.replace(".","/"),self.deviceType))
        
        
        '''
        device json configuration file ist load
        '''
        self.__ifConfigLoad=False
        self.__currentCFG={}
        
        LOG.info("init deviceBase for deviceID %s finish, version %s"%(self.deviceID,__version__))
    
    def loadConfiguration(self,refresh=False):
        '''
        loading configuration file
        
        refresh= if true reload the file configuration
                 if fals use old configuration
                 default false
        
        return a Dictionary
        
        exception: baseDevice
        '''
        try:
            if not self.__ifConfigLoad or refresh:
                if not self.core.ifPathExists(os.path.dirname(self.configFile)):
                    self.core.makeDir(os.path.dirname(self.configFile))
                if not self.core.ifFileExists(self.configFile):
                    self.core.writeJSON(self.configFile,DEFAULT_CONFIGURATION_FILE)
                LOG.debug("load device configuration file %s"%(self.configFile))
                self.__currentCFG = self.core.loadJSON(self.configFile)
                self.__ifConfigLoad=True
            return self.__currentCFG
        except IOError:
            raise defaultEXC("can not find file: %s "%(self.configFile))
        except ValueError:
            raise defaultEXC("error in json file: %s "%(self.configFile))
        except:
            raise defaultEXC("unkown error to read json file %s"%(self.configFile)) 
        
    