'''
Created on 01.12.2018

@author: uschoen
'''

'''
configuration file
"enable": false,
"objectID": "onewire@rasp-heizung",
"package": "raspberry.onewire",
"class": "ds1820",
        "config": {
            "autoInterval": true,
            "blockConnector": 30,
            "busmaster": "w1_bus_master1",
            "devicePackage": "raspberry.onewire",
            "deviceType": "ds1820",
            "enable": true,
            "gatewayName": "onewire.rasp-heizung",
            "interval": 59.0,
            "name": "onewire@rasp-heizung",
            "path": "/sys/bus/w1/devices/",
            "timeout": 60,
            "tolerance": 0.2
        }
        
'''

__version__='8.0'
__author__ = 'ullrich schoen'

# Standard library imports
import os
import time
import re
import copy
import logging

# Local application imports
from modul.defaultModul import defaultModul
from core.exception import defaultEXC


LOG=logging.getLogger(__name__)
DEFAULT_CFG={
                        "interval": 60, 
                        "devicePackage": "raspberry.onewire", 
                        "class": "ds1820",
                        "deviceType": "ds1820",
                        "path": "/sys/bus/w1/devices/", 
                        "busmaster":"w1_bus_master1",
                        "tolerance": 1, 
                        "blockConnector":30,
                        "autoInterval":True,
                        'gatewayName':"unkown",
                        'enable':False
                        }

DEFAULT_CHANNEL_NAME="temperature"
DEFAULT_CHANNEL_PACKAGE="raspberry.onewire"
DEFAULT_CHANNEL_TYP="temperature"

class ds1820(defaultModul):
    '''
    classdocs
    '''
    def __init__(self,objectID,modulCFG):
        # confiuration 
        defaultCFG=DEFAULT_CFG
                        
        defaultCFG.update(modulCFG)
        defaultModul.__init__(self,objectID,defaultCFG)
        
        # all connected ds1820 sensors
        self.__connectedSensors={}
        # if error, block modul for x sec
        self.__modulBlockTime=0
        # last time read ds1820 sensors
        self.__LastReadSenors=0
        # have any sensor change
        self.SensorsHaveChange=False
        #
        self.__orginalIntervall=self.config["interval"]
        LOG.info("build ds1820 modul, %s instance"%(__name__))               

    '''
    run
    '''    
    def run(self):
        try:
            LOG.debug("ds1820 modul up")
            while self.ifShutdown:
                LOG.debug("ds1820 modul is running")
                while self.running:
                    try:
                        if self.__LastReadSenors<time.time():
                            if self.__checkOneWire():
                                self.__checkConnectedSensors()
                                for sensorID in self.__connectedSensors:
                                    try:
                                        if not self.running:
                                            break
                                        self.__readSensors(sensorID)
                                    except (defaultEXC,Exception) as e:
                                        LOG.error("some error in read ds1820 sensors:%s: %s"%(sensorID,format(e)))
                                
                                self.__calcAutoIntervall()
                                self.__LastReadSenors=int(time.time())+self.config["interval"]
                        time.sleep(0.5)
                    except:
                        LOG.critical("some error in ds1820")
                        self.__blockConnector()
                time.sleep(0.5)
            LOG.warning("modul %s is now shutdown"%(self.config["gatewayName"]))
        except:
            LOG.error("some error in raspberry onewire modul. modul stop")
    
    def __calcAutoIntervall(self):
        '''
        calculate the intervalto read the sensor
        
        use 
            self.config["autoInterval" false/return, true/calc new interval
            self.SensorsHaveChange fals add +0.5 true/calc new value 
            self.__orginalIntervall    store the orginal intervall
            self.config["interval"]    actual Interval
        
        exception: none catch all errors
        
        return :
        
        '''
        
        try:
            if not self.config["autoInterval"]:
                return
            if self.SensorsHaveChange:
                '''
                one of the sensors are change
                '''
                if self.config["interval"]>self.__orginalIntervall:
                    '''
                    some change and actual interfall is grader then orginal interval
                    '''
                    self.config["interval"]=self.__orginalIntervall
                else:
                    '''
                    some change and aktual inerval is lower then orginal interval
                    '''
                    if self.SensorsHaveChange and self.config["interval"]>1:
                        self.config["interval"]=self.config["interval"]-0.5     
            else:
                '''
                no change of one of the sensors
                '''
                self.config["interval"]=self.config["interval"]+0.5
                LOG.debug("no change for a sensor set interval (+0.5) to: %ss"%(self.config["interval"]))
        
            LOG.debug("sensor is change, set interval (-0.5) to: %ss"%(self.config["interval"]))
            self.SensorsHaveChange=False    
        except (Exception) as e:
            self.SensorsHaveChange=False
            LOG.error("can't calculate autointervall %s"%(e))

    def __readSensors(self,sensorID):
        try:
            deviceID=self.__deviceID(sensorID)
            '''
            check if sensor connected to onewire bus
            '''                   
            if  self.__connectedSensors[sensorID]["connected"]==False:
                LOG.info("sensor id %s is disconnected"%(sensorID))
                return
            '''
            check if sensor enable in core
            '''
            if not self.core.ifDeviceIDenable(deviceID):
                LOG.info("sensor id %s is disabled in core (%s)"%(sensorID,self.__deviceID(sensorID)))
                return 
            '''
            check if sensor channel enable
            '''
            if not self.core.ifDeviceChannelEnable(deviceID,DEFAULT_CHANNEL_NAME):
                LOG.info("channel %s for sensor id %s in core (%s) is disable"%(DEFAULT_CHANNEL_NAME,sensorID,self.__deviceID(sensorID)))
            '''
            read temperature from sensor
            '''   
            LOG.debug("read sensorID %s"%(sensorID))
            path=self.config["path"]+sensorID+"/w1_slave"
            self.__updateSensorID(sensorID,self.__readSensorValue(path))
        except (Exception) as e:
            self.__connectedSensors[sensorID]["connected"]=False
            raise defaultEXC("can not read/update sensorID %s, disable senor. MSG:%s"%(sensorID,format(e)))  
        
            
    def __readSensorValue(self,path):
        '''
        read Sensor
        '''
        try:
            f = open(path, "r")
            line = f.readline()
            if re.match(r"([0-9a-f]{2} ){9}: crc=[0-9a-f]{2} YES", line):
                line = f.readline()
                m = re.match(r"([0-9a-f]{2} ){9}t=([+-]?[0-9]+)", line)
                if m:
                    value =str(float(m.group(2)) / 1000.0)
                    f.close()
                    value=round(float(value),2)
                    return value
                else:
                    raise defaultEXC("value error at sensor path"%(path),False)    
            else:
                raise defaultEXC("crc error at sensor path"%(path),False)
        except (defaultEXC) as e:
            raise e
        except:
            raise defaultEXC("can not read sensor path %s"%(path),False)
               
    def __updateSensorID(self,sensorID,value):
        '''
        read onewire sensor and compare old & new value
        update core device
        '''
        try:
            lastValue=float(self.core.getDeviceChannelValue(self.__deviceID(sensorID),DEFAULT_CHANNEL_NAME))
            tempDiv=float(self.config["tolerance"])
            LOG.debug("sensorID:%s old value:%s new value:%s tolerance:%s"%(sensorID,lastValue,value,tempDiv))
            
            if (lastValue < (value-tempDiv)) or (lastValue >(value+tempDiv)):
                LOG.debug("temperature is change, update device channel temperature") 
                self.core.setDeviceChannelValue(self.__deviceID(sensorID),DEFAULT_CHANNEL_NAME,value)
                LOG.debug("update for deviceID %s success"%(self.__deviceID(sensorID)))  
                self.SensorsHaveChange=True                                 
            else:
                LOG.debug("temperature is not change")
        except:    
            raise defaultEXC("can not update sensorID %s"%(sensorID)) 
    
          
    def __checkConnectedSensors(self):
        '''
        check if new onewire sensor connect to bus and 
        add them to core
        '''
        try:
            LOG.debug("check connected sensors")
            self.__disableAllSensor()
            sensorList =os.listdir(self.config["path"])
            LOG.debug("read connected sensors in path %s"%(sensorList))
            for sensorID in sensorList:
                if not self.running:
                    break
                try:
                    if sensorID==self.config["busmaster"]:  continue
                    LOG.debug("found sensorID %s"%(sensorID))
                    
                    # add sensor in ds1820 modul
                    if not sensorID in self.__connectedSensors:
                        self.__connectedSensors[sensorID]={
                            "connected":False
                        }
                    ''' 
                    check ifdevice exists in core
                    '''
                    if not self.core.ifDeviceIDExists(self.__deviceID(sensorID)):
                        self.__addNewDevice(sensorID)
                    self.__connectedSensors[sensorID]["connected"]=True
                
                except (Exception) as e:
                    LOG.error("can not add new ds1820 sensor %s error:%s"%(sensorID,e))
                    self.__connectedSensors[sensorID]={
                        "connected":False
                    }
                    #raise defaultEXC("some unkown error in __checkConnectedSensors")
            self.__deleteDisconectedSensors()
        except:
            raise defaultEXC("can't not check connectedt senors")
    
    def __deviceID(self,sensorID):
        deviceID="%s@%s"%(sensorID,self.config.get("gatewayName","unknown"))
        return deviceID
    
    def __addNewChannel(self,sensorID):
        '''
        add a new channel with name temperature
        '''
        try:
            channelCFG={
                'channelType':DEFAULT_CHANNEL_TYP,
                'channelPackage':DEFAULT_CHANNEL_PACKAGE,
                'parameter':{
                    "currency":"C",
                    'name':sensorID,
                    'value':0,
                    'enable':True,
                    'channelType':DEFAULT_CHANNEL_TYP,
                    'channelPackage':DEFAULT_CHANNEL_PACKAGE}
               }
            LOG.debug("try to add new channel %s to deviceID %s"%(DEFAULT_CHANNEL_NAME,self.__deviceID(sensorID)))
            '''
            add new channel to device
            '''
            self.core.addDeviceChannel(self.__deviceID(sensorID),
                                       DEFAULT_CHANNEL_NAME,
                                       channelCFG) 
        except:
            self.__connectedSensors[sensorID]["connected"]=False
            raise defaultEXC("can not add new channel temperature for deviceID %s to core"%(self.__deviceID(sensorID)))
            
    
    def __addNewDevice(self,sensorID):
        '''
        add a new sensor to core core devices
        '''
        try:
            LOG.debug("add new sensorID %s with deviceID %s and type %s"%(sensorID,self.__deviceID(sensorID),self.config['deviceType']))
            deviceCFG={
                "parameter":{
                    'name':sensorID,
                    'deviceID':self.__deviceID(sensorID),
                    'deviceType':self.config['deviceType'],
                    'devicePackage':self.config['devicePackage'],
                    'enable':True,
                    'typ':"ds1820"
                    }
               }
            LOG.debug("try to add new deviceID %s "%(self.__deviceID(sensorID)))
            self.core.addDevice(self.__deviceID(sensorID),
                                self.config['devicePackage'],
                                self.config['deviceType'],
                                deviceCFG
                                )
            LOG.debug("check if channel %s exist in deviceID %s "%(DEFAULT_CHANNEL_NAME,self.__deviceID(sensorID)))
            if not self.core.ifDeviceChannelExist(self.__deviceID(sensorID),
                                                  DEFAULT_CHANNEL_NAME
                                                  ):
                self.__addNewChannel(sensorID)
        except (Exception) as e:
            LOG.error("%s"%(e))
            raise defaultEXC("can not add new deviceID %s to core"%(self.__deviceID(sensorID)))
    
    
    def __disableAllSensor(self):
        '''
        disable all modul ds1820 sensors 
        '''
        LOG.debug("disable all ds1820 sensor")
        for sensorID in self.__connectedSensors:
            self.__connectedSensors[sensorID]["connected"]=False
    
    def __deleteDisconectedSensors(self):
        '''
        delete disconnected sensor from modul list
        '''
        try:
            LOG.debug("clear up and delete disconnected ds1820 sensor")
            senors=copy.deepcopy(self.__connectedSensors)
            for sensorID in senors:
                if self.__connectedSensors[sensorID]["connected"]==False:
                    del self.__connectedSensors[sensorID]
                    LOG.info("delete ds1820 sensor %s"%(sensorID))
        except:
            LOG.error("can't clear disconnect ds1820 sensors",exc_info=True)
            
    def __checkOneWire(self):
        '''
        check if onewire path on host exists and one wire install
        '''
        try:
            if self.__modulBlockTime>time.time():
                return False
        
            if not os.path.isdir(self.config["path"]):
                LOG.error("no onewire installed")
                self.__blockConnector()
                return False
            return True
        except:
            raise defaultEXC("can't check OneWire",True)
           
    def __blockConnector(self):
        LOG.info("block onewire bus for % sec"%(self.config["blockConnector"]))
        self.__modulBlockTime=int(time.time())+self.config["blockConnector"]
