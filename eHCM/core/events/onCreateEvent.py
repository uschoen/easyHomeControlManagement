'''
Created on 22.05.2019

@author: uschoen
'''

__version__='9.1'
__filename__='onCreateEvent.py'
__author__ = 'uschoen'
__eventName__ = "oncreate"

# Standard library imports
import logging

# Local application imports
from core.events.defaultEvent import defaultEvent

LOG=logging.getLogger(__name__)

class onCreateEvent(defaultEvent):
    '''
    classdocs
    '''
    eventName="oncreate"