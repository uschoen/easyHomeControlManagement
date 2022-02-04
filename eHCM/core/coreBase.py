'''
Created on 01.12.2021

@author: uschoen
'''
__version__ = '0.9'
__author__ = 'ullrich schoen'


# Standard library imports
import json
import os
import importlib
import logging
import sys
import re
import socket

# Local application imports
from .exception import defaultEXC

LOG=logging.getLogger(__name__)

class coreBase():
    
    def __init__(self):
        
        '''
        self.path: the absolute path of the script
        '''
        self.runPath='' if not os.path.dirname(sys.argv[0]) else '%s/'%(os.path.dirname(sys.argv[0]))
        
        '''
        script absolut root path
        '''
        self.rootPath=("%s/"%(os.path.dirname(sys.argv[0])))
        '''
        self.host: the self host name
        '''
        self.host=socket.gethostbyaddr(socket.gethostname())[0]
        
        '''
        self._ip: local ip adress 
        
        retrive with cor.getLocalIP()
        '''
        self.__localIP=None
        
        LOG.info("init core base finish, version %s"%(__version__))
    
    def thisMethode(self):
        '''
        return the actule methode
        '''
        try:
            return sys._getframe(1).f_code.co_name 
        except:
            LOG.error("some error in thisMethode")
    
    def getLocalIP(self):
        """
        get the local ip back
        
        return :string
        
        excepton: ndefaultEXC
        """
        try:
            if self.__localIP==None:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(('8.8.8.8', 9))
                self.__localIP = s.getsockname()[0]
            return self.__localIP
        except (socket.error) as e:
            raise defaultEXC("socket error in getLocalIP %e"%(e))
        except:
            raise defaultEXC("unkown error in getLocalIP",True)
        
    def loadModul(self,objectID,packageName,className,classCFG):
        '''
        load python pakage/module
        
        Keyword arguments:
        packageName -- pakage name 
        className -- the name of the gateway typ:strg
        modulCFG -- configuration of the gateway typ:direcorty as dic.
                    ['pakage'] -- pakage name
                    ['modul'] -- modul name
                    ['class'] -- class name
        
        return: class Object
        exception: yes 
        '''           
        try:
            package="%s.%s"%(packageName,className)
            LOG.debug("for %s, try to bild package: %s  with class: %s"%(objectID,package,className))
            CLASS_NAME = className
            module = self.loadPackage(package)
            self.checkModulVersion(package,module)
            return getattr(module, CLASS_NAME)(**classCFG)
        except:
            raise defaultEXC("can't no load package: %s class: %s"%(package,className))  
               
    def loadPackage(self,package):
        '''
        load a python package
        
        return: object  from the Class
        
        exception: defaultEXC
         
        '''
        try:
            classModul = importlib.import_module(package)
            LOG.info("load package %s"%(package))
            return classModul
        except:
            raise defaultEXC("can't not loadPackage %s"%(package))
    
    def writeJSON(self,fileNameABS=None,jsonData={}):
        '''
        write a file with json data
        
        fileNameABS: absolute filename to write
        fileData= data to write
        
        Exception: defaultEXC
        '''
        if fileNameABS==None:
            raise defaultEXC("no fileNameABS given")
        try:
            LOG.debug("write json file to %s"%(fileNameABS))
            with open(os.path.normpath(fileNameABS),'w') as outfile:
                json.dump(jsonData, outfile,sort_keys=True, indent=4)
                outfile.close()
        except IOError:
            raise defaultEXC("can not find file: %s "%(os.path.normpath(fileNameABS)))
        except ValueError:
            raise defaultEXC("error in json find file: %s "%(os.path.normpath(fileNameABS)))
        except:
            raise defaultEXC("unkown error in json file to write: %s"%(os.path.normpath(fileNameABS)))
                       
    def checkModulVersion(self,package,classModul,modulVersion=__version__):
        '''
        check if a load package have the right module version
        
        package:    the load package
        classModul:    the load class
        modulVersion:    min version , default=core Version
        
        return: object  from the Class
        
        exception: defaultEXC
         
        '''
        try:
            if hasattr(classModul, '__version__'):
                if classModul.__version__<modulVersion:
                    LOG.warning("version of %s is %s and can by to low"%(package,classModul.__version__))
                else:
                    LOG.debug( "version of %s is %s"%(package,classModul.__version__))
            else:
                LOG.warning("modul %s has no version Info"%(package))
        except:
            LOG.critical("can't check modul version")  
    
    def writeFile(self,fileNameABS=None,fileData=None,parm="w"):
        '''
        write a file 
        
        fileNameABS: absolute filename to write
        fileData= data to write
        
        Exception: defaultEXC
        '''
        if fileNameABS==None:
            raise defaultEXC("no fileNameABS given")
        try:
            LOG.debug("write json file to %s"%(fileNameABS))
            pythonFile = open(os.path.normpath(fileNameABS),parm) 
            pythonFile.write(fileData)
            pythonFile.close()
        except IOError:
            raise defaultEXC("can not find file: %s "%(os.path.normpath(fileNameABS)))
        except ValueError:
            raise defaultEXC("error  find file: %s "%(os.path.normpath(fileNameABS)))
        except:
            raise defaultEXC("unkown error in  file to write: %s"%(os.path.normpath(fileNameABS)))             
                       
    def loadJSON(self,fileNameABS=None):
        '''
        load a file with json data
        
        fileNameABS: absolute filename to load
        
        return: Dict 
        
        Exception: defaultEXC
        '''
        if fileNameABS==None:
            raise defaultEXC("no fileNameABS given")
        try:
            with open(os.path.normpath(fileNameABS)) as jsonDataFile:
                dateFile = json.load(jsonDataFile)
            return dateFile 
        except IOError:
            raise defaultEXC("can't find file: %s "%(os.path.normpath(fileNameABS)),False)
        except ValueError:
            raise defaultEXC("error in json file: %s "%(os.path.normpath(fileNameABS)))
        except:
            raise defaultEXC("unkown error to read json file %s"%(os.path.normpath(fileNameABS)))
    
    def ifonThisHost(self,objectID):
        '''
        check is objectID on this host
        
        check to parts of pattern
        
        1:
        *@*.*  deviceID@gateway.host
        2:
        *@*    name@host
        
        return true is host on this host, else false
        '''
        try:
            if re.match('.*@.*\..*',objectID):
                ''' device id  device@gateway.host '''
                host=objectID.split("@")[1].split(".")[1]
                if host == self.host:
                    #LOG.debug("objectID %s is on this host: %s"%(objectID,self.host))
                    return True
                else:
                    #LOG.debug("objectID %s is not on host: %s"%(objectID,self.host))
                    return False
            
            if re.match('.*@.*',objectID):
                ''' object patter test@host '''
                host=objectID.split("@")[1]
                if host == self.host:
                    #LOG.debug("objectID %s  is on host: %s"%(objectID,self.host))
                    return True
                else:
                    #LOG.debug("objectID %s is not on host: %s"%(objectID,self.host))
                    return False
            LOG.error("unkown objectID pattern:%s"%(objectID))       
            return False
        except:
            LOG.error("can't format pattern %s"%(objectID),exc_info=True)
            return False
        
    def ifPathExists(self,pathABS=None):
        '''
        check if a file Path exits
        
        pathABS: absolute file path to check
            
        Exception: defaultEXC
        '''
        if pathABS==None:
            raise defaultEXC("no path given")
        try:
            return os.path.isdir(os.path.normpath(pathABS))
        except:
            raise defaultEXC("ifPathExists have a problem")
    
    def makeDir(self,pathABS=None):
        '''
        add a direktor to the filesystem
        
        pathABS: absolute file path to add
            
        Exception: defaultEXC
        '''
        if pathABS==None:
            raise defaultEXC("no path  given")
        try:
            path=os.path.normpath(pathABS)
            LOG.debug("add directory %s"%(path))
            os.makedirs(path)
        except defaultEXC as e:
            raise e
        except:
            raise defaultEXC("can not add directory %s"%(path))
        
    def ifFileExists(self,fileNameABS=None):
        '''
        check if a file  exits
        
        fileNameABS: absolute file to check
            
        return: true if exists
        
        Exception: defaultEXC
        '''
        if fileNameABS==None:
            raise defaultEXC("no file name given")
        try:
            filename=os.path.normpath(fileNameABS)          
            return os.path.isfile(filename)
        except:
            raise defaultEXC("ifFileExists have a problem")