'''
Created on 01.12.2021

@author: uschoen
'''

'''
install python package xmltodict
use:
 pip3 install xmltodict
 
to retrive the iseID from the Homematic use:

Systemvariablen:
http://IpOfTheHomematic/addons/xmlapi/sysvarlist.cgi       
Response:
<systemVariable name="test" variable="0.000000" value="0.000000" value_list="" ise_id="44628" min="0" max="65000" unit="C" type="4" subtype="0" logged="false" visible="true" timestamp="1634145058" 

xml_api(objectID,modulCFG)

objectID="name"
modulCFG:{
            "ccu3IP":"127.0.0.1",                #ccu3 ip
            "https":False,                       # use https
            "urlPath":"/addons/xmlapi/",         #urlPath
         }
xml_api.updateHMDevice(iseID,value)

iseID="ise_id from the device"
value="valu to set"

return: nothing
exception: all errors ccu3xmlEXC

'''

__version__='0.91'
__author__ = 'ullrich schoen'

# Standard library imports
import urllib3                                       #@UnresolvedImport,@UnusedImport
import logging

# Local application imports
from modul.defaultModul import defaultModul
from .ccu3EXC import ccu3xmlEXC


LOG=logging.getLogger(__name__)
__DEVICEPACKAGE__="homematic"
__CHANNELPACKAGE__="homematic"
try:
    import xmltodict                                     #@UnresolvedImport,@UnusedImport
except:
    LOG.critical("xmltodict not install. use pip3 install xmltodict",False)
    raise

class ccu3XML(defaultModul):
    '''
    classdocs
    '''
    def __init__(self,objectID,modulCFG={}):
        ''' default confiuration '''
        defaultCFG={
                "ccu3IP":"127.0.0.1",
                "xml":{
                    "https":False,
                    "urlPath":"/addons/xmlapi/"
                }
             }
            
        if not hasattr(self, "config"):
            defaultCFG.update(modulCFG)
            defaultModul.__init__(self,objectID,defaultCFG)
        
        LOG.info("build xml.API modul, %s instance verion:%s"%(__name__,__version__))               
        
    def XMLstateChange(self,iseID,value): 
        '''
            change a value in the ccu3 via xmlAPI
            
            iseID: iseID numer from the chanel in ccu3
            value: value to set in the ccu3
            
            exception: default exception
        
        '''
        try:
            LOG.debug("update iseID %s with value %s"%(iseID,value)) 
            url=("%s%s?ise_id=%s&new_value=%s"%(self.config['ccu3IP'],self.config['xml']['urlPath'],iseID,value))
            urlib3OBJ=self.__sendUrl(url)
            HMresponse=self.__converturlib3(urlib3OBJ)
            if not self.__checkResult(HMresponse):
                raise ccu3xmlEXC("some error in ccu3 response")
        except (ccu3xmlEXC) as e:
            raise e
        except:
            raise ccu3xmlEXC("unkown error in %s"%(self.core.thisMethode()),True)
            
    def XMLStateList(self):
        '''
            list alle states in the ccu3 via XML
            
            return: dict with States of alle devices and channels
            
            exceptions: ccu3xmlEXC
        '''
        try:
            url=("%s%sstatelist.cgi"%(self.config['ccu3IP'],self.config['xml']['urlPath'])) 
            urlib3OBJ=self.__sendUrl(url)
            HMresponse=self.__converturlib3(urlib3OBJ)
            return HMresponse
        except:
            raise ccu3xmlEXC("unkown error in %s"%(self.core.thisMethode()),True)
        
    def XMLDeviceList(self,show_internal=1):
        '''
            list all devices in the ccu3 via xmlAPI
            
            return: dict with devices
            
            exception: ccu3xmlEXC
        '''
        try:
            url=("%s%sdevicelist.cgi?show_internal=%s"%(self.config['ccu3IP'],self.config['xml']['urlPath'],show_internal))
            urlib3OBJ=self.__sendUrl(url)
            HMresponse=self.__converturlib3(urlib3OBJ)
            eHMCDeviceList=self.__convertDeviceList(HMresponse['deviceList']['device'])
            return eHMCDeviceList
        except (ccu3xmlEXC) as e:
            raise e
        except:
            raise ccu3xmlEXC("unkown error in %s"%(self.core.thisMethode()),True)
        
    def __convertDeviceList(self,deviceList={}):
        '''
        
        '''
        try:
            eHMCDeviceList={}
            for device in deviceList:
                deviceID=device['@address']
                deviceTyp=device['@device_type'].replace("-","_")
                
                '''
                    device container
                '''
                eHMCDeviceList[deviceID]={'parameter':{
                                                        "devicePackage": __DEVICEPACKAGE__,
                                                        "deviceType": deviceTyp},
                                          'channels':{},
                                          "devicePackage": __DEVICEPACKAGE__,
                                          "deviceType": deviceTyp,
                                          "events":{}
                                          }
                
                for deviceKey, keyValue in device.items():
                    deviceKey=deviceKey.replace("@", "")
                    if deviceKey=="channel":
                        ''' add channel to device '''
                        if isinstance(keyValue, dict):
                            ''' only on channel '''
                            keyValue=[keyValue,]
                        for deviceChannel in keyValue:
                            channelName="%s:%s"%(deviceTyp,deviceChannel['@index'])
                            '''
                                channel Container
                            '''
                            eHMCDeviceList[deviceID]['channels'][channelName]={'parameter':{
                                                                                    "channelPackage": __CHANNELPACKAGE__,
                                                                                    "channelType": "%s_%s"%(deviceTyp,deviceChannel['@index'])},
                                                                                "channelPackage": __CHANNELPACKAGE__,
                                                                                "channelType": "%s_%s"%(deviceTyp,deviceChannel['@index']),
                                                                                "events":{}  
                                                                                }
                            
                            for channelKey, channelValue in deviceChannel.items():
                                channelKey=channelKey.replace("@","")
                                eHMCDeviceList[deviceID]['channels'][channelName]['parameter'][channelKey]=channelValue
                    else:
                        ''' add paramter to device    '''
                        eHMCDeviceList[deviceID]['parameter'][deviceKey]=keyValue
            return eHMCDeviceList
        except:
            raise ccu3xmlEXC("unkown error in %s"%(self.core.thisMethode()),True)
        
            
    def __converturlib3(self,urlib3OBJ):
        '''
            convert a urlib3 object in a dict
            
            urlib3OBJ: urlib3 object
            
            return: dict
            
            exception ccu3xmlEXC
        '''
        try:
            HMresponse=xmltodict.parse(urlib3OBJ.data)
            return HMresponse
        except:
            raise ccu3xmlEXC("unkown error in %s"%(self.core.thisMethode()),True)
        
    def __checkResult(self,HMresponse):
        '''
            check the 
        '''
        try:
            if "result" in HMresponse:
                if "changed" in HMresponse['result']: 
                    LOG.debug("value successful change")
                    return True
                elif "not_found" in HMresponse['result']: 
                    LOG.error("can not found iseID")
                    return False
                else:
                    LOG.error("get some unkown answer %s"%(HMresponse))
                    return False
            else:
                LOG.error("get some unkown answer %s"%(HMresponse)) 
                return False        
        except:
            raise ccu3xmlEXC("unkown error in %s"%(self.core.thisMethode()),True)
    
    def __sendUrl(self,url):
        '''
            send the http/s request to the ccu3
            
            url: url without https://
            
            return: urlib3 object
            
            exception: ccu3xmlEXC
        '''
        try:
            if self.config['xml']['https']:
                url="https://%s"%(url)
            else:
                url="http://%s"%(url)
            LOG.info("send url:%s"%(url))
            http = urllib3.PoolManager()
            response = http.request('GET', url)
            if  response.status != 200:
                raise ccu3xmlEXC("gethttp error back:%s http"%(response.status))
            return response
        except (ccu3xmlEXC) as e:
            raise e
        except:
            raise ccu3xmlEXC("unkown error in %s"%(self.core.thisMethode()),True)                 
