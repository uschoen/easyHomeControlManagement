"""
Created on 20.01.2021

@author: uschoen
"""

__version__ = 0.91

# Standard library imports
import logging
import time
import datetime

# Local application imports
from core.script.exception import defaultError,testError,cmdError

from core.exception import defaultEXC


#@var Global Logging intance
LOG=logging.getLogger(__name__)




class praraphser():
    
    """
    classdocs
    @todo: finish dokumentation
    @todo: delete old function
    @todo: clean up the exception    
    """
                   
    def __init__(self,core,callerObject={},callerVars={},cfg={}):
        self.__command={
        "string":self.__string,
        "callModul":self.__callModul,
        "getCallerObject":self.__getCallerObject,
        "arguments":self.__arguments,
        "timeStampNow":self.__timeStampNow,
        "secSinceDay":self.__secSinceDay
        }

        self.__allowedCMD={
             "arguments":["string","getCallerObject","timeStampNow","arguments"],
             "callModul":["string","arguments","getCallerObject"],
             "getCallerObject":["string","arguments"],
             "root":["callModul","getCallerObjet"]
             }                    

        self.__requiertARGS={  
              "callModul":["modulName","function"],
              "getCallerObject":["function"]
             }    
        
        """
        global configuration of the class
        
        @var cfg: HASH value
        """ 
        self.cfg={
            'maxProgramDeep':10,    
            'test':False
            }
        self.cfg.update(cfg)
        
        """
        Caller Vars
        """
        self.__callerValues=callerVars
        
        """
        Caller object
        """
        self.__callerObject=callerObject
        
        """
        core instance
        @var self.core: Instance of the core class of hmc
        """
        self.core=core
    
        LOG.debug("prarapser init finish, Version:%s"%(__version__))
        
    def runScript(self,script,programDeep=0): 
        """
        Run a script.
        
            script: dict or list
            callerObject: object has call the script
            callerVars: dict    default: 0    
                                ={'var1':...,
                                  'var2':...,
                                  ...
                                  'varX':...}
            programmDeep: int    default 0   
        @raise: core.script.exception.defaultError,core.script.exception.testError
        @Return: True/False
        """
        
        if programDeep>self.cfg['maxProgramDeep']:
            raise defaultError("maximum of programm deep reach : %s"%(programDeep ))
        try:
            self.__loop(script)
        except (testError) as e:
            LOG.critical("test of the script failed")
            return False
        except (defaultError) as e:
            LOG.critical("error in Script: %s"%(e))
        except: 
            raise defaultError("unkown error in runscript",True)
        
    def __loop(self,script,cmd="root"):
        """
        Script loop
        
        "some string"
        or
        {"cmd1":"Value1"} 
        or 
        {"cmd1":"Value1",
        "cmd2":"Value1"}
        or
        [ {"cmd1":"Value1"},
          {"cmd1":"Value1"}..-
        ]
                
        return: "some string" or results from other
        """
        try:
            value=""
            ### type is dic
            if (type(script)== dict):
                # only one entry in dic
                if len(script)==1:
                    (command,value)=(*script.keys(),*script.values())
                    if command not in self.__allowedCMD[cmd]:
                        raise cmdError ("command %s is not supported in %s"%(command,cmd))
                    LOG.debug("call command: %s value:%s"%(command,value))
                    value=self.__command[command](value)
                # more then one entry in dic
                else:
                    for keyEntry in script:
                        scriptPart=script[keyEntry]
                        (command,value)=(*scriptPart.keys(),*scriptPart.values())
                        if command not in self.__allowedCMD[cmd]:
                            raise cmdError ("command %s is not supported in %s"%(command,cmd))
                        LOG.debug("call command: %s value:%s"%(command,value))
                        value="%s%s"%(value,self.__command[command](value))
            
            # type is list            
            elif (type(script)== list):
                for part in script:
                    value="%s%s"%(value,self.__loop(part,cmd))
            
            # type is string
            elif (type(script)== str):
                LOG.debug("find type srcipt in loop, return value:%s"%(script))
                value=script
            
            # type is unkown
            #TODO: raise error ?
            else:
                LOG.error("wrong type at script: %s"%(script))
            return value    
        except (testError) as e:
            LOG.critical("test for script have some error: %s"%(e))
        except (cmdError) as e:
            LOG.critical("script error in script: %s"%(e))
        except (Exception) as e:
            raise defaultError("unkoun errer in loop %s"%(e),True) 
    
    def __callModul(self,strg={},cmd="callModul"):
        """
        call a Modul from Core modul self.modul
        
        {"callModul": {
            "modulName": {...},
            "function": {...},
            "arguments": {"arg1":{...},
                          "arg2":{...}...
                         }
            ... = other script command like "string"
            
            self.core[modulName]['intance'].callback(arg1:...,arg2:...,)
            @todo: change self.core to a methode in coreModul like "callModul(modulName,args) ...
        """
        try:
            if not set(self.__requiertARGS[cmd]) <= set(strg):
                raise cmdError("%s function miss some atribute must have: %s have: %s"%(cmd,self.__requiertARGS[cmd],strg))
            
            # modulname
            modulName=self.__loop(strg['modulName'],cmd)
            
            # callback
            callerFunction=self.__loop(strg['function'], cmd)
            
            if not modulName in self.core.module:
                raise cmdError("modul %s is not existing"%(modulName))
            
            if "arguments" in strg:
                # agruments [optional]
                arguments={'arguments':strg.get('arguments')}
                arguments=self.__loop(arguments,cmd)
                if (self.cfg['test']):
                    LOG.debug("test enable, call core modul:%s function:%s args:%s"%(modulName,callerFunction,arguments))
                else:
                    LOG.debug("call core modul:%s function:%s args:%s"%(modulName,callerFunction,arguments))
                    value=getattr(self.core.module[modulName]['instance'], callerFunction)(**arguments)
            else:
                if (self.cfg['test']):
                    LOG.debug("test enable, call core modul:%s function:%s args:%s"%(modulName,callerFunction,arguments))
                else:
                    LOG.debug("call core modul:%s function:%s"%(modulName,callerFunction))
                    value=getattr(self.core.module[modulName]['instance'], callerFunction)()
            return value
        except (defaultEXC) as e:
            raise defaultError("can't run modul:%s"%(e))
        except (defaultError,cmdError) as e:
            raise e
        except:
            if (self.cfg['test']):
                raise testError("callModul of the script failed")
            raise defaultError("callModul function has error with arg: %s"%(strg),True)
            
    def __isTrueFalse(self,strg,cmd="truefalse"):
        """
        is true ore false {dic}
        """ 
        try:
            LOG.debug("call %s function"%(cmd))
            for job in strg:
                (field,value)=(job.keys()[0],job.values()[0])
                if field not in self.__allowedCMD[cmd]:
                    raise defaultError("function %s is not supported in %s"%(field,cmd))
                LOG.debug("call function: %s value: %s"%(field,value))
                value=self.__command[field](value)
                return value
        except defaultError as e:
            raise e
        except:
            LOG.error("%s function has error: %s"%(cmd,strg))
                
    
    def __condition(self,strg,cmd='comparison'):
        try:       
            LOG.debug("call %s function"%(cmd)) 
            if not set(self.__allowedCMD[cmd]) <= set(strg):
                raise defaultError("%s function miss some atribute %s"%(cmd,strg.keys()))
            if strg.get('comparison') not in self.__allowedCMD['comparison']:
                raise defaultError("comparison: %s not allowed"%(strg.get(cmd)))
            valueA=self.__sourceAB(strg['sourceA'])
            valueB=self.__sourceAB(strg['sourceB'])
            LOG.debug("A is: %s B is: %s"%(valueA,valueB))
            value=self.__command[strg['comparison']](valueA,valueB)
            LOG.debug("comparison A and B is: %s"%(value))
            if value:
                strg=strg['true'] 
            else:
                strg=strg['false'] 
            value=self.__isTrueFalse(strg)
            return value
        except defaultError as e:
            raise e
        except:
            LOG.error("%s function has error: %s"%(cmd,strg))
        
    def __sourceAB(self,strg): 
        """
        source AB Function
        """   
        LOG.debug("call sourceA/B function")
        (field,value)=(strg.keys()[0],strg.values()[0])
        if field not in self.__allowedCMD['sourceAB']:
            raise defaultError("function %s is not supported in sourceAB"%(field)) 
        value=self.__command[field](value)
        return value 
            
    def __isLessOrEqual(self,valueA,valueB):
        """
                check if <=
                
        return true or false
        """        
        LOG.debug("call isLessOrEqual function")
        try:
            if valueA<=valueB:
                return True
            return False
        except:
            raise defaultError("can't compare isLessOrEqual")
    
    def __isGraderOrEqual(self,valueA,valueB):
        """
                check if >=
                
        return true or false
        """
        LOG.debug("call isGraderOrEqual function")
        try:
            if valueA>=valueB:
                return True
            return False
        except:
            raise defaultError("can't compare isGraderOrEqual")
    
    def __isEqual(self,valueA,valueB):
        """
                check if =
                
        return true or false
        """
        LOG.debug("call isEqual function")
        try:
            if valueA==valueB:
                return True
            return False
        except:
            raise defaultError("can't compare isEqual")
        
    def __isGrater(self,valueA,valueB):
        """
                check if >
                
        return true or false
        """
        LOG.debug("call isGrater function")
        try:
            if valueA>valueB:
                return True
            return False
        except:
            raise defaultError("can't compare isGrater")
        
    def __isLess(self,valueA,valueB):
        """
                check if <
                
        return true or false
        """
        LOG.debug("call isLess function")
        try:
            if valueA<valueB:
                return True
            return False
        except:
            raise defaultError("can't compare isLess")
        
    def __isUnequal(self,valueA,valueB):
        """
                check if <>
                
        return true or false
        """
        LOG.debug("call isUnequal function")
        try:
            if valueA!=valueB:
                return True
            return False
        except:
            raise defaultError("can't compare isUnequal")
    
    def __or(self,valueA,valueB):
        """
                check if or
                
        return true or false
        """
        LOG.debug("call isUnequal function")
        try:
            if valueA or valueB:
                return True
            return False
        except:
            raise defaultError("can't compare isUnequal")

    
    def __and(self,valueA,valueB):
        """
                check if and
                
        return true or false
        """
        LOG.debug("call isUnequal function")
        try:
            if valueA and valueB:
                return True
            return False
        except:
            raise defaultError("can't compare isUnequal")
    
    def __xor(self,valueA,valueB):
        """
                check if xor
              
        return true or false
        """
        LOG.debug("call isUnequal function")
        try:
            if valueA != valueB:
                return True
            return False
        except:
            raise defaultError("can't compare isUnequal")

           
    def __string(self,strg):
        """
        return a value
        
        {"string": "some text"}
        
        strg: string 
        
        return: "some text"
        
        """
        LOG.debug("call string function :%s"%(strg)) 
        return strg
    
    def __changeDeviceChannel(self,strg):
        """
        set a device Channel
        02.11
        """
        LOG.debug("call changeDeviceChannel function")
        if not set(self.__allowedCMD['changeDeviceChannel']) <= set(strg):
            raise defaultError("changeDeviceChannel function miss some atribute %s"%(strg.keys()))

        (deviceID,channelName,value)=(strg.get('deviceID'),strg.get('channelName'),strg.get('value'))
        
        try:
            if (self.core.ifDeviceIDExists(deviceID)):
                if (self.core.ifDeviceChannelExist(deviceID,channelName)):
                    if (self.cfg['test']):
                        raise testError("can't find deviceID %s or device channel %s"%(deviceID,channelName))
                    else:
                        LOG.debug("call function changeDeviceChannel %s and channelName %s to value: %s"%(deviceID,channelName,value))
                        self.core.changeDeviceChannelValue(deviceID,channelName,value)
                raise defaultError("can't find deviceID %s or channelName %s"%(deviceID,channelName))
        except:
            raise defaultError("can't change deviceID %s and channelName %s to value: %s"%(deviceID,channelName,value))

        
    def __getCallerValue(self,strg):
        """
        get the Caller Vars back
              
        @var var: strg Caller field
         
        @return:  strg give the text auf the caller Value back
        02.11
        """
        if strg not in self.__callerValues:
            raise cmdError("%s is not a caller variable"%(strg))
        try:
            LOG.debug("call callerValue value:%s"%(strg))
            return self.__callerValues.get(strg,"unknown")
        except:
            raise defaultError("unkown error in getCallerValue",True)
    
    def __arguments(self,strg={},cmd="arguments"):
        """
        get back some arguments key,value pairs fur funktions
        
        {"key1":[....],
         "key2":[....]
        }
        
        return: dic
        """
        try:
            print (strg)
            arguments={}
            for argsKeys in strg:
                arguments[argsKeys]=self.__loop(strg[argsKeys], "arguments")
            return arguments
        except (defaultError,testError,cmdError) as e:
            raise e
        except:
            raise defaultError("unkon error in arguments",True)
    
    def __getCallerObject(self,strg={},cmd="getCallerObject"):
        """
        get a value from the the Caller object back
        
        "getCallerObject":{
            "function":"SOME FUNCTION",
            "arguments": {"key1":"value1","key2":"value2"...} [optional]
        }
              
        @var: strg function field
         
        @return:  strg give the text auf the caller Value back
        02.11
        """
        if not set(self.__requiertARGS[cmd]) <= set(strg):
                raise cmdError("%s function miss some atribute must have: %s have: %s"%(cmd,self.__requiertARGS[cmd],strg))
        try:
            LOG.debug("call getCallerObject value:%s"%(strg))
            
            # function 
            callerFunction=strg.get("function","unkown")
           
            if "arguments" in strg:
                # agruments [optional]
                arguments={'arguments':strg.get('arguments')}
                arguments=self.__loop(arguments,cmd)
                value=getattr(self.__callerObject, callerFunction)(**arguments)
            else:
                value=getattr(self.__callerObject, callerFunction)()
            LOG.debug("function %s return value:%s"%(callerFunction,value))
            return value
        except (defaultError,testError,cmdError) as e:
            raise e
        except:
            raise defaultError("unkown error in getCallerObject",True)
        
    def __getDeviceChannel(self,strg):
        """
        Return a value for a device Channel.
        
        Raise exception on error
        """
        LOG.debug("call getDeviceChannel function")
        if not set(self.__allowedCMD['getDeviceChannel']) <= set(strg):
            raise cmdError("getDeviceChannel function miss some atribute %s"%(strg.keys()))
        (deviceID,channelName)=(strg.get('deviceID'),strg.get('channelName'))
        LOG.debug("get value of deviceID %s and channelName:%s"%(deviceID,channelName))
        try:
            value= self.core.getDeviceChannelValue(deviceID,channelName)
            return value
        except:
            raise defaultError("unkown error in get DeviceChannel",True)

    def __timeStampNow(self,strg=False):
        """
        Return a time stamp.
        
        Return: int
        """
        return int(time.time())

    def __secSinceDay(self,strg=False):
        """
        Return secound since midnight.
        
        Return: int 
        """
        now = datetime.datetime.now()
        midnight = datetime.datetime.combine(now.date(), datetime.time())
        return (now - midnight).seconds