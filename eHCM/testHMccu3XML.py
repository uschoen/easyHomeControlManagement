'''
Created on 19.11.2021

@author: uschoen
'''

'''
Created on 06.10.2021

@author: uschoen
'''


from modul.homematic.ccu3XML import ccu3XML as testModul
import logging
import logging.config
import pprint

from time import sleep

logging.config.dictConfig(
                {
                "version": 1,
                "disable_existing_loggers": False,
                "formatters": {
                    "simple": {
                        "format": "%(asctime)s - %(name)30s - %(lineno)d - %(levelname)s - %(message)s"
                    }
                },
                "handlers": {
                    "console": {
                "class": "logging.StreamHandler",
                "formatter": "simple",
                "level": "DEBUG",
                "stream": "ext://sys.stdout"
                                },
                },
                "root": {
                    "handlers": ["console"],
                    "level": "DEBUG"
                }
                
            }
        )

LOG=logging.getLogger(__name__)

eventCFG={
            "ccu3IP":"10.90.12.90",
                "https":False,
                "urlPath":"/addons/xmlapi/",
                "blockConnector":30
        }
    
try:
    LOG.debug("start up")
    
    objectID="test@test"
    LOG.debug("obj %s cfg %s"%(objectID,eventCFG))
    modul=testModul(objectID,eventCFG)
    data=modul.XMLdeviceList()
    '''
    run  a modul
    '''
    #modul.startModul()
    #modul.start()
    #modul.updateDevices()
    #sleep(180)
    #modul.shutDownModul()
    
    '''
    print data
    '''
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(data)
except:
    modul.stopModul()
    modul.shutDownModul()
    LOG.critical("error",exc_info=True)