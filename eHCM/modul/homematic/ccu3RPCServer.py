"""
Created on 01.12.2021

@author: uschoen

install python package ????
use:

Homematic CCU3 ports



"""
__version__='0.9'
__author__ = 'ullrich schoen'

# Standard library imports
import logging
import os

# Local application imports
from modul.defaultModul import defaultModul
from core.manager import manager
from .ccu3EXC import ccu3RPCserverEXC

LOG=logging.getLogger(__name__)

class ccu3RPCServer(defaultModul):
    '''
    classdocs
    '''
    def __init__(self,cfg,ccu3):
        """
        init
        """
        self.core=manager()
        
        """
        class configuration
        """
        self.config={
                        "name":"unknown"                       
                      }
        self.config.update(cfg)
        
        ''' reset timer function '''
        self.__ccu3=ccu3
        
        

        LOG.debug("init new ccu3RPCrequest version %s"%(__version__))
        
        
    def event(self,interfaceID,channelName,ChannelType,value):
        """
        event methode
        """
        try:
            LOG.debug("event methode")
            fileData="%s %s %s \r"%(channelName,ChannelType,value)
            fileNameABS="log/deviceCCUEvents.txt"
            pythonFile = open(os.path.normpath(fileNameABS),"a") 
            pythonFile.write(fileData)
            pythonFile.close()
            self.__ccu3.resetAllTimer()
        except:
            raise ccu3RPCserverEXC("unkown error in %s"%(self.thisMethode()),True)
    
    def listMethods(self,*args):
        """
        listMethods methode
        """
        try:
            LOG.debug("listMethods methode")
            self.__ccu3.resetAllTimer()
            return True
        except:
            raise ccu3RPCserverEXC("unkown error in %s"%(self.thisMethode()),True)
    
    def listDevices(self,*args):
        """
        listDevices methode
        """
        try:
            LOG.debug("listDevices methode")
            print("listdevices %s"%(args))
            
        except:
            raise ccu3RPCserverEXC("unkown error in %s"%(self.thisMethode()),True)
    
    def newDevices(self,interfaceID,allDevices):
        """
        newDevices methode
        """
        try:
            LOG.debug("newDevices methode")
            self.__ccu3.resetAllTimer()
            return True
        except:
            raise ccu3RPCserverEXC("unkown error in %s"%(self.thisMethode()),True)
         
    def getVersion(self,version):
            LOG.debug("getVersion methode %s"%(version))
            return True
            
    def deleteDevices(self, interface_id, addresses):
        """
        deleteDevices methode
        """
        try:
            LOG.debug("deleteDevices methode")
            self.__ccu3.resetAllTimer()
            return True
        except:
            raise ccu3RPCserverEXC("unkown error in %s"%(self.thisMethode()),True)
        
    def updateDevice(self, interface_id, address, hint):
        """
        newDevices methode
        """
        try:
            LOG.debug("updateDevice methode")
            self.__ccu3.resetAllTimer()
            return True
        except:
            raise ccu3RPCserverEXC("unkown error in %s"%(self.thisMethode()),True) 
         
    def replaceDevice(self, interface_id, oldDeviceAddress, newDeviceAddress):
        """
        readdedDevice methode
        """
        try:
            LOG.debug("readdedDevice methode")
            self.__ccu3.resetAllTimer()
            return True
        except:
            raise ccu3RPCserverEXC("unkown error in %s"%(self.thisMethode()),True) 
        
    def readdedDevice(self, interface_id, addresses):
        """
        readdedDevice methode
        """
        try:
            LOG.debug("readdedDevice methode")
            self.__ccu3.resetAllTimer()
            return True
        except:
            raise ccu3RPCserverEXC("unkown error in %s"%(self.thisMethode()),True)