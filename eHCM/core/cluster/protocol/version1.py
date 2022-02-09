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

__protocolVersion__=1

LOG=logging.getLogger(__name__)



class version1:
    
    def __init__(self,core,cfg,running):
        '''
            core protocol version 1
            
            core: core object store in self.core
            cfg: configuration {
                                "debug":    true/false if true plain data was log
                                "cryptType" plain/aes see in ENCRYPTION
                                
                               }
            running: var to stop the prortocol on shutdown
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
        self.__running=running
        
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
    
    def reciveData(self,clientSocket,remoteCoreIP):
        '''
            recive remote cor meassages 
        
            clientSocket    network client socket
            remoteCoreIP    ip from the remote core
            
            exception: protocolException,cryptException
            
            return:
        '''
        try:
            commadsArgs=self.__getCommandRequest(clientSocket,self.__crypt, self.__config['user'],self.__config['password'])
            
            if commadsArgs['callFunction'] not in ALLOWED_FUNCTIONS:
                raise protocolException("callfunction %s not allowed"%(commadsArgs['callFunction']),False)
            
            try:
                LOG.debug("call function %s"%(commadsArgs['callFunction']))
                methodToCall = getattr(self.core,commadsArgs['callFunction'])
            except:
                raise protocolException("callfunction %s not found"%(commadsArgs['callFunction']),False)
            
            args=commadsArgs['args']
            
            try:
                methodToCall(*args)
                self.__sendResult(clientSocket,self.__crypt,self.__config['user'],self.__config['password'],result="ok")   
            except (Exception) as e:
                self.__sendResult(clientSocket,self.__crypt,self.__config['user'],self.__config['password'],result="error",message="e.msg")   
                raise protocolException("can't call function %s: (%s) error: %s"%(commadsArgs['callFunction'],commadsArgs,e.msg))
             
        except (protocolException,cryptException) as e:
            raise e   
        except:
            raise protocolException("some unkown error in %s"%(self.core.thisMethode),True)
        
    def sendJob(self,clientSocket,jobQueue):
        pass
    
    
    def __readSocket(self,networkSocket):
        try:
            rawData=self.__lastMSG
            readData=b''
            while self.__running:
                try:
                    networkSocket.settimeout(0.1)
                    readData=networkSocket.recv(BUFFER)
                    if readData==b'':
                        raise protocolException("network socket closed",False)
                except (protocolException) as e:
                    raise e
                except socket.timeout:
                    pass
                networkSocket.settimeout(None)
                if not readData==b'':
                    rawData=b''.join((rawData,readData))
                    if ENDMARKER in rawData:
                        ''' endmarker found '''
                        (readData,self.__lastMSG)=rawData.split(ENDMARKER)
                        break                
            if self._debug:
                LOG.debug("get data %s"%(readData))
                LOG.debug("rest data %s"%(self.__lastMSG))
            return readData
        except (protocolException) as e:
            raise e
        except:
            raise protocolException("unkown error at reading network Socket",True)
    
    def __writeSocket(self,clientSocket,rawData):
        '''
            send data to the network socket
           
            clientSocket:    client network socket
            rawData:    data so send
            
            exception:  protocolException
        '''
        try:
            data=b''.join((rawData,ENDMARKER))
            if self._debug:
                LOG.debug("send data: %s"%(data))
            clientSocket.sendall(data)
        except:
            raise protocolException("unkown err in writeSocket",True)
        
    def __getCommandRequest(self,clientSocket,encryption,user,password):
        '''
            get a command request
        
            cleintSocket: network socket
            encryption:   encryption object
            user:         user name
            password:     password
            
            return: var as dict with body var
            
            exception: protocolException,cryptException
        '''
        try:
            ''' read network socket '''
            LOG.debug("waiting for next command request")
            readData=self.__readSocket(clientSocket)
            LOG.debug("get Command Request")
         
            ''' check resived data '''
            readVars=encryption.unSerialData(readData)
            self.__checkHeader(readVars.get("header",{}),user)
            decryptBodyVars=self.__decryptBody(readVars.get("body",{}),encryption,password)
            if decryptBodyVars.get('objectID',None)==None:
                raise protocolException("protocol error, no objectID",False)
            if decryptBodyVars.get('callFunction',None)==None:
                raise protocolException("protocol error, no callFunction",False)
            if decryptBodyVars.get('args',None)==None:
                raise protocolException("protocol error, no args",False)
            return (decryptBodyVars)
        except (cryptException) as e:
            raise cryptException("encrption error:%s"%(e.msg))
        except (protocolException) as e:
            raise protocolException("protocol error:%s"%(e.msg))
        except :
            raise protocolException("unkown error in getCommandRequest",True)
    
    def __buildBody(self,encryption,body,password):
        '''
        build the body and return as string
        
        encryption: encryption Object
        body: as dict body:{
                            'result':"...",
                            'meassage':"..."
                            }
        pasword: password
        
        return: string (crypt body)
        
        exception:protocolException,cryptException
        '''
        try:
            cryptBody=encryption.encrypt(body,password)
            return cryptBody
        except (cryptException) as e:
            raise e
        except:
            raise protocolException("unkown error in build body",True)
    
    def __decryptBody(self,body,encryption,password):
        '''
        decrypt body
        
        return body as var
        
        exception cryptException,protocolException
        '''
        try:
            encryptionBody=encryption.decrypt(body,password)
            return encryptionBody
        except (protocolException,cryptException) as e:
            raise e
        except:
            raise protocolException("unkown error in body %s"%(body),True)
    
    def __buildHeader(self,encryption,user,body):
        '''
            build the header and return as string
            
            encryption: encryption Object
            user: user name
            body: body as string
            
            return : string with data
            
            exception:protocolException,cryptException
        '''
        try:
            header={
                'header':{
                    'user':user,
                    'protocol':__protocolVersion__},
                'body':body
                }
            header=encryption.serialData(header)
            return header
        except (cryptException) as e:
            raise e
        except:
            raise protocolException("unkown error in buildheader",True)
    
    def __checkHeader(self,header,user):
        '''
            check protocol header
            header:{
                    "protocol": __protocolVersion__,
                    "user": self.__config['user']
                    }
            user: username       
        '''
        try:
            if not header.get('protocol',0)==__protocolVersion__:
                raise protocolException("error no or wrong protokol version. header is:%s"%(header))
            if not header.get('user',"unkown")==user:
                raise protocolException("error no or wrong user. header:%s"%(header))
        except (protocolException) as e:
            raise e
        except:
            raise protocolException("unkown error in checkHeader. header:%s"%(header),True)    
    
    def __sendResult(self,clientSocket,encryption,user,password,result="error",message=""):   
        '''
        send a result meassages to core
        
        clientSocket: networkSocket object
        encryption: encryption object
        user: user
        password: password
        result: ok or error    (default=error)
        message: string with message (optional)
        
        exception: protocolException
        '''
        try:
            body={
                'result':result,
                'message':message
                }
            body=self.__buildBody(encryption, body, password)
            autorisationString=self.__buildHeader(encryption, user, body)
            LOG.debug("send result %s"%(result))
            self.__writeSocket(clientSocket,autorisationString)
        except (cryptException,protocolException) as e:
            raise e
        except:
            raise protocolException("can't send result")     
    
   