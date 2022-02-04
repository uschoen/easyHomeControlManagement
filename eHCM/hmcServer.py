#!/usr/bin/python3 -u

'''
File:hmcServer.py

Created on 01.12.2018
(C):2018
@author: ullrich schoen
@email: uschoen.hmc(@)johjoh.de
Requierment:python 3.2.3

Please use command to start:
python3 hmcServer.py 
'''



__version__='0.9'
__author__ = 'ullrich schoen'
__PYTHONVERSION__=(3,2,3)
__LOGLEVEL__="DEBUG"
logType="simple" # simple or colored


# Standard library imports
import sys
import signal
import argparse
import logging.config


# local library import
from core.manager import manager as coreManager


''' 
######################################################
set logging configuration
######################################################
'''
if logType=="colored":
    try:
        import coloredlogs              #@UnresolvedImport
        coloredlogs.DEFAULT_FIELD_STYLES = {'asctime': {'color': 'green'}, 'hostname': {'color': 'magenta'}, 'levelname': {'color': 'black', 'bold': True}, 'name': {'color': 'blue'}, 'programname': {'color': 'cyan'}}
        coloredlogs.DEFAULT_LEVEL_STYLES = {'critical': {'color': 'red', 'bold': True}, 'debug': {'color': 'green'}, 'error': {'color': 'red'}, 'info': {}, 'notice': {'color': 'magenta'}, 'spam': {'color': 'green', 'faint': True}, 'success': {'color': 'green', 'bold': True}, 'verbose': {'color': 'blue'}, 'warning': {'color': 'yellow'}}
        coloredlogs.install(level=__LOGLEVEL__,milliseconds=True,fmt='%(msecs)03d %(name)30s[%(process)d] %(lineno)04d %(levelname)8s %(message)s')
    except:
        print ("no cocloredlog install")
        print ("use: pip3 install coloredlogs, use simple logging")
        logType="simple"    

if logType=="simple":
    cfg={
        "disable_existing_loggers": False,
        "formatters": {
            "simple": {"format": "%(asctime)s - %(name)30s - %(lineno)d - %(levelname)s - %(message)s"}
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "simple",
                "level": "DEBUG",
                "stream": "ext://sys.stdout"
            }
        },
        "root": {
            "handlers": ["console"],
            "level": "DEBUG"
        },
        "version": 1
    }
    logging.config.dictConfig(cfg)
    
LOG=logging.getLogger(__name__)
'''
######################################################
check python version
######################################################
'''
if sys.version_info <= __PYTHONVERSION__: 
    LOG.critical(__doc__)
    LOG.critical("This server have Python version is %s.%s.%s,"%(sys.version_info[:3]))
    LOG.critical("please use python version %s.%s.%s or grader."%(__PYTHONVERSION__))
    sys.exit(0)
LOG.info("start hmcServer on python version %s.%s.%s"%(sys.version_info[0],sys.version_info[1],sys.version_info[2],))
'''
######################################################
set signal handler
######################################################
'''
ALL_SIGNALS= dict((getattr(signal, n), n) \
    for n in dir(signal) if n.startswith('SIG') and '_' not in n )

def signal_handler(signum, frame):
    LOG.critical("Signal handler called with signal:%s frame:%s"%(signum,frame))
    sys.exit()

LOG.debug("set up signal handler ") 
for i in [x for x in dir(signal) if x.startswith("SIG")]:
    try:
        signum = getattr(signal,i)
        signal.signal(signum,signal_handler)
    except:
        LOG.info("skip signal handler signal.%s, ot catchable"%(i)) 


'''
######################################################
start arguments
######################################################
@todo: test start arguments
'''    
configFile=None
daemon=False
coreServer=False
try:
    parser = argparse.ArgumentParser(description='hmcServer help interface')
    parser.add_argument('--configfile','-c',help="full path of the configuration file",action="store", dest="configfile",default=None)
    parser.add_argument('--daemon','-d',help="start hmc as daemon, default true",action="store", dest="daemon",default=False) 
except:
    print("you forget some start arguments. Use -h help option"%(sys.version_info))
    sys.exit(0)
args = parser.parse_args()
configFile=args.configfile
daemon=args.daemon

'''
######################################################
Main
######################################################
'''
try:
    LOG.info("start up hmcServer -c %s -d %s -l %s"%(configFile,daemon,logType)) 
    LOG.info("starting hmc hmcCore version %s"%(__version__))
    
    coreServer=coreManager(configFile,logType)
    coreServer.start()   
except (SystemExit, KeyboardInterrupt) as e:
    LOG.critical("get signal to kill hmcServer process! hmcServer going down !!") 
except:
    LOG.critical("hmcServer have some problem and going down !!",exc_info=True) 
finally:
    LOG.critical("hmcServer now in finally state and try to going down !!")
    if coreServer:
        coreServer.shutdown() 
    coreServer=None
    LOG.critical("hmcServer is finally down !!")
    sys.exit()
        