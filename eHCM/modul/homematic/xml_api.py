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
<systemVariable name="test" variable="0.000000" value="0.000000" value_list="" ise_id="44628" min="0" max="65000" unit="C" type="4" subtype="0" logged="false" visible="true" timestamp="1634145058" 
 

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

class xml_api(defaultModul):
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
                    LOG.error("can not found iseID %s"%(iseID))
                else:
                    LOG.warning("get some unkown answer %s"%(response.data))
            else:
                LOG.warning("get some unkown answer %s"%(response.data)) 
        
         
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
