'''
File:remoteCoreCyrptAES.py
CLASS:AES
Created on 01.12.2018
(C):2018
@author: ullrich schoen
@email: uschoen.hmc(@)johjoh.de
Requierment:pycrypto

Install:pycrypto
Please install pip3: 
    sudo apt-get update
    sudo apt-get install python3-pip
Next, install pycrypto with pip:
    sudo pip3 install crypto
or
    sudo pip-3.2 install pycrypto
'''

__version__='7.0'
__author__ = 'ullrich schoen'

# Standard library imports
import pickle as cPickle                    #@UnresolvedImport 
import hashlib
import os
import logging
from base64 import b64encode
# Local application imports
from .cryptException import cryptException

LOG=logging.getLogger(__name__)
BS = 16
pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS) 
unpad = lambda s : s[0:-ord(s[-1])]

class aes(object):
    
    def __init__(self):
          
        LOG.debug("init aes encryption, version %s"%(__version__))

    def serialData(self,var):
        '''
        serial data, from a json var to a string
        '''
        try:
            serialData=cPickle.dumps(var)
            return serialData
        except:
            raise cryptException("can't serial data",False)
    
    def unSerialData(self,serialData):
        '''
        unsiral data from a string to a jason var
        '''
        try:
            unSerialData=cPickle.loads(serialData)
            return unSerialData 
        except:
            raise cryptException("can't unserial data",False)
        
    def decrypt(self,cryptstring,key):
        '''
        decrypt/entschluesseln a string
        '''
        try:
            LOG.info("use AES decryption")
            plaintext=self.__decrypt(cryptstring,key)
            var=self.unSerialData(plaintext)
            return var
        except:
            raise cryptException( "can not decrypt message",False)
            
    
    def encrypt(self,var,key):
        '''
        encrypt/verschluesseln a var
        '''
        try:
            LOG.info("use AES encryption")
            plaintext=self.serialData(var)   
            string=self.__encrypt(plaintext, key)
            return string
        except:
            raise cryptException( "can not encrypt message",False)
        
    def __formatKey(self,key):
        '''
        return a 32-byte key
        '''
        return hashlib.sha256(key.encode('utf-8')).digest()
    
    def __IVKey(self):
        #token = b64encode(os.urandom(128)).decode('utf-8')[:BS]
        token = b64encode(os.urandom(128))[:BS]
        return token
    
    def __encrypt(self,plaintext,key):
        '''
        ' encrypt (verschlusseln)a string with aes
        '
        ' string: is a plain string
        ' return: an decryptet string
        '''
        try:
            from Crypto.Cipher import AES   #@UnresolvedImport 
            iv=self.__IVKey()
            fKey=self.__formatKey(key)
            decryption_suite = AES.new(fKey,AES.MODE_CBC,iv)
            plaintext+=b'\x00' * (BS -len(plaintext)%BS)
            cryptstring =iv+decryption_suite.encrypt(plaintext)
            return cryptstring
        except:
            raise cryptException( "can not encrypt message")
    
    def __decrypt(self,cryptstring,key):
        '''
        ' encrypt (entschluesseln)a aes string
        '
        ' cryptstring: is a aes cryptedt string
        ' return: an encryptet string
        '''
        try:
            from Crypto.Cipher import AES   #@UnresolvedImport 
            iv=cryptstring[:BS]
            cryptstring=cryptstring[BS:]
            fKey=self.__formatKey(key)
            encryption_suite = AES.new(fKey,AES.MODE_CBC,iv)
            plaintext = encryption_suite.decrypt(cryptstring)
            plaintext=plaintext.rstrip(b'\x00')
            return plaintext
        except:
            raise cryptException( "can't decrypt message")
        
