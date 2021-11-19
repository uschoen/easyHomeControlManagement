'''
Created on 01.12.2021

@author: uschoen
'''


__version__='0.9'
__author__ = 'ullrich schoen'

# Standard library imports
import os
import sys
import logging
import time

# Local application imports

#
LOG=logging.getLogger(__name__)

class coreDefaults():
    '''
    core events function
    '''
    def __init__(self):
        LOG.info("init core defaults finish, version %s"%(__version__))

    def getCoreDefaults(self):
        defaults={
                'version':__version__,
                'from':int(time.time()),
                'config':{
                    'core':{
                        'daemon':True,
                        },
                    'configuration':{
                        'basePath':"etc",
                        'filePath':self.host,
                        'files':{
                            'devices':"devices.json",
                            'module':"module.json",
                            'cluster':"cluster.json",
                            'core':"config.json",
                            'logger':"logger.json",
                            'script':"script.json"
                            }
                        }
                    }
                }
        return defaults
        
    def getLoggerDefaults(self):
        defaults={
            "colored":{
                "FIELD_STYLES":{
                    'asctime': {'color': 'green'}, 
                    'hostname': {'color': 'magenta'}, 
                    'levelname': {'color': 'black', 'bold': True}, 
                    'name': {'color': 'blue'}, 
                    'programname': {'color': 'cyan'}
                },
                "LEVEL_STYLES":{
                     'critical': {'color': 'red', 
                     'bold': True}, 
                     'debug': {'color': 'green'},
                     'error': {'color': 'red'}, 
                     'info': {}, 
                     'notice': {'color': 'magenta'}, 
                     'spam': {'color': 'green', 'faint': True}, 
                     'success': {'color': 'green', 'bold': True}, 
                     'verbose': {'color': 'blue'}, 
                     'warning': {'color': 'yellow'}
                    
                },
                "level":"DEBUG",
                "milliseconds":True,
                "fmt": "%(msecs)03d %(name)30s[%(process)d] %(lineno)04d %(levelname)8s %(message)s"
            },
            "simple":{
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
                    "warning_handler": {
                        "backupCount": 5,
                        "class": "logging.handlers.RotatingFileHandler",
                        "encoding": "utf8",
                        "filename": "%s/log/%s_warning.log"%(os.path.abspath(os.path.dirname(sys.argv[0])),self.host),
                        "formatter": "simple",
                        "level": "DEBUG",
                        "maxBytes": 1200000,
                        "mode": "a"
                    }
                },
                "root": {
                    "handlers": [
                        "warning_handler","console"                   
                    ],
                    "level": "DEBUG"
                },
                "version": 1
            }}
        return defaults