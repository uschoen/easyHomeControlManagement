'''
Created on 01.12.2018

@author: uschoen
'''

__version__='9.0'
__author__ = 'ullrich schoen'

# Standard library imports
import pickle 
import logging
# Local application imports
from .exception import cryptException

LOG=logging.getLogger(__name__)

class plain(object):
    
    def __init__(self):
        LOG.debug("init plain encryption, version %s"%(__version__))

    def __serialData(self,var):
        '''
        serial data, from a json var to a string
        '''
        try:
            serialData=pickle.dumps(var)
            return serialData
        except:
            raise cryptException("can't serial data",True)
    
    def __unSerialData(self,serialData):
        try:
            unSerialData=pickle.loads(serialData)
            return unSerialData 
        except:
            raise cryptException("can't unserial data",True)
        
    def decrypt(self,cryptstring,key=""):
        '''
        decrypt/entschluesseln a string
        '''
        try:
            plaintext=cryptstring
            var=self.__unSerialData(plaintext)
            return var
        except (cryptException) as e:
            raise e
        except:
            raise cryptException( "can not decrypt message",False)
            
    
    def encrypt(self,var,key=""):
        '''
        encrypt/verschluesseln a var
        '''
        try:
            plaintext=self.__serialData(var)   
            string=plaintext
            return string
        except (cryptException) as e:
            raise e
        except:
            raise cryptException( "can not encrypt message",False)
        
    
        
