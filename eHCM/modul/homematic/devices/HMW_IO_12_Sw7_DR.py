'''
Created on 23.02.2022
@author: ullrich schoen

'''

__version__="0.9"
__author__="ullrich schoen"
__DEVICETYPE__="HMW_IO_12_Sw7_DR"
__DEVICEPACKAGE__="homematic"

# Standard library imports
import logging
# Local application imports
from modul.hmc.devices.defaultDevice import defaultDevice

LOG=logging.getLogger(__name__)

class HMW_IO_12_Sw7_DR(defaultDevice):

    deviceType="HMW_IO_12_Sw7_DR"
    devicePackage="homematic"
        
    def __init__(self,deviceID,deviceCFG={},restore=False):
        
        
        defaultDevice.__init__(self,deviceID,deviceCFG,restore)
        LOG.info("init %s finish, version %s, deviceID:%s"%(__DEVICETYPE__,__version__,self.deviceID))