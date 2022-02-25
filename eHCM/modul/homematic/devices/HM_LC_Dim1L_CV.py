'''
Created on 23.02.2022
@author: ullrich schoen

'''

__version__="0.9"
__author__="ullrich schoen"
__DEVICETYPE__="HM_LC_Dim1L_CV"
__DEVICEPACKAGE__="homematic"

# Standard library imports
import logging
# Local application imports
from modul.hmc.devices.defaultDevice import defaultDevice

LOG=logging.getLogger(__name__)

class HM_LC_Dim1L_CV(defaultDevice):

    deviceType="HM_LC_Dim1L_CV"
    devicePackage="homematic"
        
    def __init__(self,deviceID,deviceCFG={},restore=False):
        
        
        defaultDevice.__init__(self,deviceID,deviceCFG,restore)
        LOG.info("init %s finish, version %s, deviceID:%s"%(__DEVICETYPE__,__version__,self.deviceID))