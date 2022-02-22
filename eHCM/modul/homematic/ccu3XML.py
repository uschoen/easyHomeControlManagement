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
            "hmHost":"http://127.0.0.1",            #url CCU3
            "https":False,                          #use https ?
            "url":"/config/xmlapi/statechange.cgi", #url path
            "blockConnector":30                     #block time if error
         }
xml_api.updateHMDevice(iseID,value)

iseID="ise_id from the device"
value="valu to set"

return: nothing
exception: all errors defaultEXC

'''

__version__='0.91'
__author__ = 'ullrich schoen'

# Standard library imports
import urllib3                                       #@UnresolvedImport,@UnusedImport
import logging

# Local application imports
from modul.defaultModul import defaultModul
from core.exception import defaultEXC


LOG=logging.getLogger(__name__)

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
        # confiuration 
        defaultCFG={
                "hmHost":"http://127.0.0.1",
                "https":False,
                "path":{
                    "statechange":"/addons/xmlapi/statechange.cgi",
                    "devicelist":"/addons/xmlapi/devicelist.cgi"
                }, 
                "blockConnector":30,
            }

        self.__default_arg=["iseID","value"]                
        defaultCFG.update(modulCFG)
        
        defaultModul.__init__(self,objectID,defaultCFG)
        
        LOG.info("build xml.API modul, %s instance"%(__name__))               
    
    def XMLdevicelist(self):
        '''
            list the HM devices with the data from the XML API
            
            return: dict
            
            exception: defaultEXC
        '''
        try:
            LOG.debug("get all device from HM %s"%(self.config['hmHost']))
            url=("%s%s?"%(self.config['hmHost'],self.config['path']['devicelist']))
            response=False
            if self.config['https']:
                response=self.__sendHttps(url)
            else:
                response=self.__sendHttp(url)
            HMresponse=xmltodict.parse(response.data)
            return HMresponse
        except:
            raise defaultEXC("unkown error in %s"%(self.core.thisMethode()),True)
        
    def XMLstatechange(self,iseID,value):
        '''
            update a hm device via xml APL
            
            iseID: the iseID from the Device channel
            value: the vlaue from the channel
            
            exception: defaultEXC
        '''
        try:
            LOG.info("update iseID %s with value %s"%(iseID,value)) 
                     
            response=False
            url=("%s%s?ise_id=%s&new_value=%s"%(self.config['hmHost'],self.config['path']['statechange'],iseID,value))
                
            if self.config['https']:
                response=self.__sendHttps(url)
            else:
                response=self.__sendHttp(url)
            if self.__checkresponse(response):
                return
            else:
                LOG.error("update iseID %s with value %s not succesful"%(iseID,value))      
        except (defaultEXC) as e:
            raise e            
        except:
            raise defaultEXC("unkown error in %s"%(self.core.thisMethode()),True)
        
    def __checkresponse(self,response):
        '''
            check the respone from the homematic
            
            response: urllib3 object
            
            return: true/false
            
            exception: defaultEXC
        '''
        try:
            HMresponse=xmltodict.parse(response.data)
            if "result" in HMresponse:
                if "changed" in HMresponse['result']: 
                    LOG.debug("value successful change")
                    return True
                elif "not_found" in HMresponse['result']: 
                    LOG.error("can not found iseID ")
                    return False
                else:
                    LOG.error("get some unkown answer %s"%(response.data))
                    return False
            else:
                LOG.error("no result in data %s"%(response.data))
                return False
        except:
            raise defaultEXC("unkown error in %s"%(self.core.thisMethode()),True)
        
    def __sendHttps(self,url):
        '''
        ' @todo: write HTTPS
        '''
        try:
            LOG.warning("__sendHttps not implemnt")
        except:
            raise defaultEXC("can't not check connectedt senors")     
    
    def __sendHttp(self,url):
        try:
            LOG.debug("url is %s "%(url))
            http = urllib3.PoolManager()
            response = http.request('GET', url)
            if  response.status != 200:
                raise defaultEXC("gethttp error back:%s"%(response.status))
            return response
        except (defaultEXC) as e:
            raise e
        except (Exception) as e:
            raise defaultEXC("get error from  url %s"%(e)) 
        except:
            raise defaultEXC("some error in __SendHTTP",True)                   
