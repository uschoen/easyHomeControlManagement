'''
Created on 22.05.2019

@author: uschoen
'''

__version__='9.1'
__filename__='onBootEvent.py'
__author__ = 'uschoen'
__eventName__= "onboot"

# Standard library imports
import logging

# Local application imports
from core.events.defaultEvent import defaultEvent

LOG=logging.getLogger(__name__)

class onBootEvent(defaultEvent):
    '''
    classdocs
    '''
    
    eventName="onboot"