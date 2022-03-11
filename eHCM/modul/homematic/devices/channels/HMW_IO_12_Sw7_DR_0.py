'''
Created on 11.03.2022
@author: ullrich schoen

'''

__version__="8.0"
__author__="ullrich schoen"

# Standard library imports
import logging
# Local application imports
from modul.hmc.devices.channels.defaultChannel import defaultChannel

LOG=logging.getLogger(__name__)

class HMW_IO_12_Sw7_DR_0(defaultChannel):

    channel_type="HMW_IO_12_Sw7_DR_0"
    channel_package="homematic"

    def __init__(self,deviceID,channelCFG={},restore=False):

        defaultChannel.__init__(self,deviceID,channelCFG,restore)



        self.parameter['CFGVersion']=__version__

        LOG.info("init channel %s finish, version %s, deviceID:%s"%(self.channel_type,self.channelName,__version__))