'''
Created on 22.05.2019

@author: uschoen
'''

__version__='9.0'
__filename__='events/defaultEvent.py'
__author__ = 'uschoen'




# Standard library imports
import logging
import time
import threading
from copy import deepcopy

# Local application imports
from core.events.exception import eventError
from core.manager import manager

LOG=logging.getLogger(__name__)


class defaultEvent(object):
    '''
    classdocs

    eventCFG={
        'parameter':{....}
        'callers':{...}
        
    
        parameter:{
            CFGVersion= int    default  __version__ from script, can't change
            eventName= var     default name from event, can't change
            timestamp= int     default time at __init__ can't change
        }   
        callers:{
        
        }
    restore= true/false    default false
    '''
    eventName="defaultEvent"
    DEFAULT_CALLER={
        "args":None,
        "callFunction":None,
        "enable":False
    }
    def __init__(self,eventCFG={},restore=False):
        
        self.callers={}
        self.parameter={}
        self.core=manager()
        
        ### Parameter ###
        ''' 
        update parameterfrom eventCFG{'parameter'}
        '''
        self.parameter.update(eventCFG.get('parameter',{}))
        '''
        fixed parameter
        '''
        self.parameter["CFGVersion"]=__version__,
        self.parameter["eventName"]=self.eventName,
        self.parameter["timestamp"]=int(time.time())
        
        self.callers.update(eventCFG.get('callers',{}))
        
        LOG.debug("init %s finish, version %s"%(self.eventName,__version__))
    
    def getParameter(self):
        '''
        return the Parameter
        
        return dic
        '''
        return self.parameter 
    
    def getCallers(self):
        '''
        return the callers
        
        return: dic
        '''
        return self.callers
    
    def updateParameter(self,eventParameter):
        '''
        update the parameter of the event
        
        update existing parameter and add new one if they not exists
        
        parameter: dic            a list of parameter
                                  {
                                  'name':"unkown",
                                  'objectID':"unkown",
                                  'lastcall':0
                                  }
        
        exception: eventError
        '''
        try:
            self.parameter.update(eventParameter)
            LOG.debug("update event %s parameter"%(self.eventName))
        except:
            raise eventError("some error in updateParameter",True)
        
    def updateCallers(self,callers):
        '''
        update one or mor caller 
        
        update one or more caller. Error for one caller was ignored
        
        callers = dic            Caller an parameters
                                 "mysql"{
                                        "caller":None,
                                        "args":None,
                                        enable":true
                                        }
        exception: eventError
        '''
        try:  
            for callerName in callers:
                try:
                    self.updateCaller(callerName, callers[callerName])
                except eventError as e:
                    LOG.error("updateCaller %s have an error : %s"%(callerName,e.msg))
        except:
            raise eventError("some error in updateCallers",True) 
            
    def updateCaller(self,callerName,callerCFG):
        '''
        update a event caller configuration
        
        if the callerName exists, overwirte the old configration
        
        callerName = string        name of the caller
                                   "mysql"
        callerCFG = dic            configurtion of the caller
                                   {
                                    "caller":None,
                                    "args":None,
                                    "enable:" true
                                   }
        
        exception: eventError
        '''
        try:
            if callerName not in self.callers:
                self.callers[callerName]=self.DEFAULT_CALLER
            self.callers[callerName].update(callerCFG)
            LOG.debug("update event %s caller: %s"%(self.eventName,callerName))
        except:
            raise eventError("some error in updateCaller",True)
    
    def ifCallerExists(self,callerName):
        '''
        check if the caller name exists
        
        modulName: the moul to check
        
        return: true/false
        
        exception: eventError
    
        '''
        try:
            if callerName in self.callers:
                return True
            return False 
        except:
            raise eventError("some error in ifModulExitst",True)
    
    def callCallers(self,callerObject={}):
        LOG.debug("event %s check callers"%(self.eventName))
        try:
            for caller in self.callers:
                try:
                    if  not self.callers[caller].get('enable',False):
                        LOG.info("caller %s is disable"%(caller))
                        continue
                    callerArgs=self.callers[caller]
                    LOG.debug("executeCaller %s with arg: %s"%(caller,callerArgs))
                    threading.Thread(target=self.executeCaller,args = (callerArgs,callerObject)).start()
        
                    #self.executeCaller(callerArgs,callerObject)
                except (Exception) as e:
                    LOG.error("can't execute caller %s :%s"%(caller,e.msg))
        except:
            raise eventError("some error in callCallers",True)    
    
    def executeCaller(self,args,callerObject={}):
        '''
        call a internal function in the core with args
        
        dict args={
                    "callFuntion":funktion name,
                    "args": arguments
                    "enable": true false
                  }
        object callerObject: the object have init the event
        
        exception eventError        
        '''
        try:
            LOG.debug("call function %s"%(args.get('callFunction',"unkown")))
            methodToCall = getattr(self.core,args['callFunction'])
        except:
            raise eventError("callfunction %s not found"%(args.get('callFunction',"unkown")))
        arguments={}
        arguments=deepcopy(args.get('args',{}))
        arguments["callerObject"]=callerObject
        
        try:
            
            methodToCall(**arguments)
            
        except (Exception) as e:
            raise eventError("can't call function %s: (%s) error: %s"%(args.get('callFunction',"unkown"),arguments,e.msg))
    
    
    def getConfiguration(self):
        '''
        return the event configuration
        
        return: dic
        '''
        cfg={
            "parameter":self.getParameter(),
            "callers":self.getCallers()
            } 
        return cfg 