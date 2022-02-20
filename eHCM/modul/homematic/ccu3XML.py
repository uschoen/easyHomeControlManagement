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

__version__='0.9'
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
                "url":"/config/xmlapi/statechange.cgi", 
                "blockConnector":30,
            }

        self.__default_arg=["iseID","value"]                
        defaultCFG.update(modulCFG)
        
        defaultModul.__init__(self,objectID,defaultCFG)
        
        LOG.info("build xml.API modul, %s instance"%(__name__))               
        
    def updateHMDevice(self,iseID,value):
        '''
        
        '''
        try:
            LOG.debug("update iseID %s with value %s"%(iseID,value)) 
                     
            response=False
            if self.config['https']:
                url=("%s%s?ise_id=%s&new_value=%s"%(self.config['hmHost'],self.config['url'],iseID,value))
                response=self.__sendHttps(url)
            else:
                url=("%s%s?ise_id=%s&new_value=%s"%(self.config['hmHost'],self.config['url'],iseID,value))
                response=self.__sendHttp(url)
                
            HMresponse=xmltodict.parse(response.data)
            if "result" in HMresponse:
                if "changed" in HMresponse['result']: 
                    LOG.debug("value successful change")
                elif "not_found" in HMresponse['result']: 
                    raise defaultEXC("can not found iseID %s"%(iseID))
                else:
                    raise defaultEXC("get some unkown answer %s"%(response.data))
            else:
                raise defaultEXC("get some unkown answer %s"%(response.data)) 
        
            
        except:
            LOG.critical("some error in xml_api")
            raise defaultEXC("can't update homematic, some error")
    
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
