'''
Created on 01.12.2018

@author: uschoen
'''



__version__='7.0'
__author__ = 'ullrich schoen'
__protokolVersion__=1
ENDMARKER=b'<<stop>>!!!'
BUFFER=512

# Standard library imports
import logging
import socket

# Local application imports
from ..syncException import protocolException
from .encryption.aes import aes
from .encryption.plain import plain

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

LOG=logging.getLogger(__name__)



class version1:
    
    def __init__(self,cfg,core,running):
        self.__core=core
        ''' configuration '''
        self.__cfg={
            'remoteCore':"unkown@unkown",
            'blocked':60,
            "ip": "0.0.0.0",
            "port":5091,
            "debug":False,
            "encryption":{
                "cryptType":"plain",
                "password":"unkown",
                "user":"unkown"
                }
        }
        self.__cfg.update(cfg)
        
        ''' is running '''
        self.running=running
        
        ''' debug msg on '''
        self._debug=self.__cfg["debug"]
        
        ''' network socket '''
        self.__networkSocket=False
        
        ''' store defragment mesagge '''
        self.__lastMSG=b''
        
        if not self.__cfg["encryption"]["cryptType"] in ENCRYPTION:
            LOG.error("%s is not avaible option for encoding, use plain now"%(self.__cfg["encryption"]["cryptType"]))
            self.__cfg["encryption"]["cryptType"]="plain"
        self.__crypt=ENCRYPTION[self.__cfg["encryption"]["cryptType"]]()
        
        LOG.info("init protokol version 1 finish, version %s"%(__version__))
    
    def sendJob(self,job):
        try:
            if not self.__networkSocket:
                ''' build network connection '''
                self.__networkSocket=self.__openNetworkSocketToClient(self.__cfg["ip"],self.__cfg["port"])
            self.__sendCommandRequest(self.__networkSocket,self.__crypt,self.__cfg["encryption"]["user"],self.__cfg["encryption"]["password"],job)   
            self.__checkCommandResponse(self.__networkSocket, self.__crypt, self.__cfg["encryption"]["user"],self.__cfg["encryption"]["password"])
        except:
            self.__networkSocketClose(self.__networkSocket)
            self.__networkSocket=False
            raise protocolException("some error in protokol version1",False)
    
    def __networkSocketClose(self,networkSocket):
        ''' close the server socket '''
        try:
            networkSocket.close()
            LOG.debug("close socket from remote server %s"%(self.__cfg['remoteCore'])) 
        except:
            pass
        
        
    def __readResponse(self,networkSocket,encryption,user,password):
        '''
        check a rseult after a command action
        
        networkSocket: networ socket object
        encryption: encryption object
        user: user
        password: password
        
        raise exception: 
        '''
        try:
            ''' read network socket '''
            readData=self.__readSocket(networkSocket)
            
            return readData
        except  (protocolException) as e:
            raise e
        except:
            raise protocolException("error in response password")
        
    def __openNetworkSocketToClient(self,ip,port):
        '''
        open a network socket to a core
        
        ip:ip adress oft the server
        port: port of the server
        
        raise for all all erros and eyception: protocolException
        '''
        try:
            LOG.debug("try connect to Core %s:%s"%(ip,port))
            clientSocket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            clientSocket.connect((ip,port))
            return clientSocket
        except (socket.error,ConnectionRefusedError):
            raise protocolException ("can't open socket to remote core %s:%s"%(ip,port),False)
        except:
            raise protocolException ("can not connect to Core %s:%s"%(ip,port))
        
    def __readSocket(self,networkSocket):
        try:
            rawData=self.__lastMSG
            readData=b''
            while self.running:
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
            raise protocolException("unkown error at reading network Socket",False)
        
    def __sendCommandRequest(self,networkSocket,encryption,user,password,job):
        try:
            body=self.__buildBody(encryption,job,password)
            commandString=self.__buildHeader(encryption, user, body)
            LOG.debug("send command (objectID %s)"%(job))
            self.__writeSocket(networkSocket,commandString)
        except (protocolException) as e:
            raise e
        except:
            raise protocolException("some error in protokol")
    
    def __getCommandRequest(self,networkSocket,encryption,user,password):
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
    
    def __writeSocket(self,networkSocket,rawData):
        try:
            data=b''.join((rawData,ENDMARKER))
            if self._debug:
                LOG.debug("send data: %s"%(data))
            networkSocket.sendall(data)
        except:
            raise protocolException("can't sent data to network socket")
        
    def __buildBody(self,encryption,body,password):
        '''
        build the body and return as string
        '''
        try:
            cryptBody=encryption.encrypt(body,password)
            return cryptBody
        except:
            raise protocolException("error,can't build body")
    
    def __checkCommandResponse(self,networkSocket,encryption,user,password):
        '''
        check a rseult after a command action
        
        networkSocket: networ socket object
        encryption: encryption object
        user: user
        password: password
        
        raise exception: 
        '''
        try:
            ''' read network socket '''
            readData=self.__readSocket(networkSocket)
            ''' check resived data '''
            readVars=encryption.unSerialData(readData)
            self.__checkHeader(readVars.get("header",{}),user)            
            decryptBodyVars=self.__decryptBody(readVars.get("body",{}),encryption,password)
            self.__checkResult(decryptBodyVars)
        except:
            raise protocolException("error in response password")
    
    def __sendResult(self,networkSocket,encryption,user,password,result="error",message=""):   
        '''
        send a result meassages to core
        
        networkSocket: networkSocket object
        encryption: encryption object
        user: user
        password: password
        result: ok or error    (default=error)
        message: string with message (optional)
        '''
        try:
            body={
                'result':result,
                'message':message
                }
            body=self.__buildBody(encryption, body, password)
            autorisationString=self.__buildHeader(encryption, user, body)
            LOG.debug("send result %s"%(result))
            self.__writeSocket(networkSocket,autorisationString)
        except:
            raise protocolException("can't send result") 
        
    def __checkResult(self,decryptBodyVars):
        '''
        check result of a message
        
        if result not OK send exception: protocolException
        '''
        try:
            if not decryptBodyVars.get('result','error')=="ok":
                raise protocolException("result have error message::%s"%(decryptBodyVars.get('message',"unkown")),False)   
        except (protocolException) as e:
            raise e
        except:
            raise protocolException("error in check result. body:%s"%(decryptBodyVars))
        
    def __decryptBody(self,body,encryption,password):
        '''
        decrypt a body
        
        return body as var
        
        exception for entcryption error:encryptionException
        exception for default error:protocolException
        '''
        try:
            encryptionBody=encryption.decrypt(body,password)
            return encryptionBody
        except:
            raise protocolException("error can't entcrypt body: %s"%(body))
        
    def __checkHeader(self,header,user):
        try:
            if not header.get('protokoll',0)==__protokolVersion__:
                raise protocolException("error no or wrong protokol version. header is:%s"%(header))
            if not header.get('user',"unkown")==user:
                raise protocolException("error no or wrong user. header:%s"%(header))
        except (protocolException) as e:
            raise e
        except:
            raise protocolException("error with header in password response. header:%s"%(header))    
        
    def __buildHeader(self,encryption,user,body):
        '''
        build the header and return as string
        '''
        try:
            header={
                'header':{
                    'user':user,
                    'protokoll':__protokolVersion__},
                'body':body
                }
            header=encryption.serialData(header)
            return header
        except:
            raise protocolException("can'build Header")
        
    def reciveData(self,networkSocket,remoteCoreIP):
        try:
            user=self.__cfg["encryption"]["user"]
            password=self.__cfg["encryption"]["password"]
            commadsArgs=self.__getCommandRequest(networkSocket, self.__crypt, user,password)
            if commadsArgs['callFunction'] not in ALLOWED_FUNCTIONS:
                raise protocolException("callfunction %s not allowed"%(commadsArgs['callFunction']),False)
            
            try:
                LOG.debug("call function %s"%(commadsArgs['callFunction']))
                methodToCall = getattr(self.__core,commadsArgs['callFunction'])
            except:
                raise protocolException("callfunction %s not found"%(commadsArgs['callFunction']),False)
            
            args=commadsArgs['args']
            
            try:
                methodToCall(*args)
                self.__sendResult(networkSocket,self.__crypt,user,password,result="ok")   
            except (Exception) as e:
                raise protocolException("can't call function %s: (%s) error: %s"%(commadsArgs['callFunction'],commadsArgs,e.msg))
              
        except (Exception) as e:
            self.__sendResult(networkSocket,self.__crypt,user,password,"error",e.msg)
            raise protocolException("unkown error")