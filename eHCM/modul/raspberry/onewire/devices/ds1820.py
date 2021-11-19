'''
Created on 03.01.2021
@author: ullrich schoen

'''

__version__="8.0"
__author__="ullrich schoen"
__DEVICETYPE__="ds1820"
__DEVICEPACKAGE__="raspberry.onewire"

# Standard library imports
import logging
# Local application imports
from modul.hmc.devices.defaultDevice import defaultDevice

LOG=logging.getLogger(__name__)

class ds1820(defaultDevice):

    deviceType="ds1820"
    devicePackage="raspberry.onewire"
        
    def __init__(self,deviceID,deviceCFG={},restore=False):
        
        
        defaultDevice.__init__(self,deviceID,deviceCFG,restore)
        LOG.info("init %s finish, version %s, deviceID:%s"%(__DEVICETYPE__,__version__,self.deviceID))