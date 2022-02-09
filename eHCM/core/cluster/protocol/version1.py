'''
Created on 01.12.2018

@author: uschoen
'''



__version__='9.0'
__author__ = 'ullrich schoen'

# Standard library imports
import logging
import socket

# Local application imports
from .encryption.aes import aes
from .encryption.plain import plain
from .encryption.cryptException import cryptException
from .protocolException import protocolException

'''
encryption
'''
ENCRYPTION={
            "aes":aes,
            "plain":plain
            }
ALLOWED_FUNCTIONS={
                    'updateCoreConnector'
                }

DEFAULT_CFG={"debug":True,
             "cryptType":"plain",
             "user":"unkown",
             "password":"secret"
             }

ENDMARKER=b'<<stop>>!!!'
BUFFER=512

__protokolVersion__=1

LOG=logging.getLogger(__name__)



class version1:
    
    def __init__(self,core,cfg):
        '''
            core protocol version 1
            
            core: core object store in self.core
            cfg: configuration {
                                "debug":    true/false if true plain data was log
                                "cryptType" plain/aes see in ENCRYPTION
                                
                               }
        '''   
        
        
        '''
            core object
        '''
        self.__core=core
        
        ''' 
            configuration 
        '''
        self.__config=DEFAULT_CFG 
        self.__config.update(cfg)
        
        ''' 
            is running 
        '''
        self.__running=True
        
        ''' 
            debug msg on 
        '''
        self._debug=self.__config["debug"]
        
    
        ''' 
            store defragment mesagge 
        '''
        self.__lastMSG=b''
        
        '''
            check if the right encryption modul in configuration (cryptType). 
            default set to plain. Build encryption object in self.__crypt
        '''
        if not self.__config["cryptType"] in ENCRYPTION:
            LOG.error("%s is not avaible option for encoding, use plain now"%(self.__config["cryptType"]))
            self.__config["cryptType"]="plain"
        self.__crypt=ENCRYPTION[self.__config["cryptType"]]()
        
        LOG.info("init protokol version 1 finish, version %s"%(__version__))
    
    def stop(self):
        '''
            stop the communication and drop network socket
        '''
        self.__running=False
        LOG.info("core protocol version %s was stop"%(__protokolVersion__))
        
    
    def reciveData(self,clientSocket,remoteCoreIP):
        '''
            recive remote cor meassages 
        
            clientSocket    network client socket
            remoteCoreIP    ip from the remote core
            
            exception: protocolException,cryptException
            
            return:
        '''
        try:
            commadsArgs=self.__getCommandRequest(clientSocket,self.__crypt, user,password)
            
            
        except:
            raise protocolException("some unkown error in %s"%(self.core.thisMethode),True)
        
    def sendJob(self,clientSocket,jobQueue):
        pass
    
    def __getCommandRequest(self,clientCocket,encryption,user,password):
        '''
        get a command request
        '''
        try:
            ''' read network socket '''
            LOG.debug("waiting for next command request")
            readData=self.__readSocket(networkSocket)
            LOG.debug("get Command Request")
            ''' check resived data '''
            readVars=encryption.unSerialData(readData)
            self.__checkHeader(readVars.get("header",{}),user) 
            decryptBodyVars=self.__decryptBody(readVars.get("body",{}),encryption,password)
            if decryptBodyVars.get('objectID',None)==None:
                raise protocolException("some error in command, no objectID",False)
            if decryptBodyVars.get('callFunction',None)==None:
                raise protocolException("some error in command, no callFunction",False)
            if decryptBodyVars.get('args',None)==None:
                raise protocolException("some error in command, no args",False)
            return (decryptBodyVars)
        except :
            raise protocolException("some error im get command request")
    