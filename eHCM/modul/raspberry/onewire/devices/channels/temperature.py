'''
Created on 03.01.2021
@author: ullrich schoen

'''

__version__="8.0"
__author__="ullrich schoen"

# Standard library imports
import logging
# Local application imports
from modul.hmc.devices.channels.defaultChannel import defaultChannel

LOG=logging.getLogger(__name__)

class temperature(defaultChannel):

    channel_type="temperature"
    channel_package="raspberry.onewire"

    def __init__(self,deviceID,channelCFG={},restore=False):

        defaultChannel.__init__(self,deviceID,channelCFG,restore)



        self.parameter['CFGVersion']=__version__

        LOG.info("init channel %s finish, version %s, deviceID:%s"%(self.channel_type,self.channelName,__version__))