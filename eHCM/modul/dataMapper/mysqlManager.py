'''
Created on 01.12.2018

@author: uschoen


install python package mysql.connector
use:
sudo pip3 install mysql-connector-python

'''


__version__='0.91'
__author__ = 'ullrich schoen'

# Local application imports
from core.exception import defaultEXC
from modul.defaultModul import defaultModul
# Standard library imports
import logging
try:
    import mysql.connector                                                         #@UnresolvedImport
    from mysql.connector import Error                                              #@UnresolvedImport,@UnusedImport
    from mysql.connector import errorcode                                          #@UnresolvedImport,@UnusedImport
except:
    raise defaultEXC("no mysql.connector module installed")
import time

# Local apllication constant
LOG=logging.getLogger(__name__)


class mysqlManager(defaultModul,object):
    '''
    modulCFG={
         'database':{
                    "database": "unkown", 
                    "host": "127.0.0.1", 
                    "password": "password", 
                    "port": 3306, 
                    "user": "unkown",
                    "raise_on_warnings": True
                    },
                    "mapping":{
                        "table":"unkown",
                        "fields":{}
                    },
        },
        "name": "dataMapper@hmc"
        }
    '''
    def __init__(self,objectID,modulCFG={}):
        '''
        Constructor
        '''
        try:
            ''' modul Config '''
            defaultModulCFG={
                        'database':{
                            "database": "unkown", 
                            "host": "127.0.0.1", 
                            "password": "password", 
                            "port": 3306, 
                            "user": "unkown",
                            "raise_on_warnings": True
                        },
                        "mapping":{
                            "table":"unkown",
                            "fields":{}
                            },
                        'name':objectID,
                        'enable':False
                        }
            defaultModulCFG.update(modulCFG)
            defaultModul.__init__(self,objectID,defaultModulCFG)
            
                        
            ''' actual caller arguments '''
            self.__callerARGS={}
            
            ''' data mappaers '''
            self.__mappers={
               "callerValues":self.__callerValues
            }
            
            ''' db connection object '''
            self.__dbConnection=False
            LOG.info("build mysqlMapper , version:%s"%(__version__))
        except:
            raise defaultEXC("can't build modul mysqlMapper version:%s"%(__version__),True)
    
    
    
    def update(self,values={}):
        '''
        update the database
        
        values:{        }
        
        exception: NONE
        '''
        try:
            LOG.debug("call update from MysqlMapper witha rgs %s"%(values))
            self.__callerARGS.update(values)
            
                
            sql=""
            self.__buildSQL(self.config['mapping'])    
            
            # check if dbconnection ready
            if not self.__dbConnection:
                self.__dbConnect(self.config['database'])
            sql=self.__buildSQL(self.config["mapping"])
            self.__sqlExecute(sql)
        except defaultEXC as e:
            LOG.critical("error in mysqlMapper: %s with error:%s"%(self.config['name'],e))   
        except:
            LOG.critical("unkown error in modul %s"%(self.config['name']),True)
           
        
    def stop(self):
        LOG.error("modul %s is stop"%(self.config['name'])) 
    
    def shutdown(self):
        try:
            LOG.critical("shutdown mysql modul")   
            self.__dbClose()  
        except:
            pass
        LOG.error("modul %s is shutdown"%(self.config['name']))       
                  
    def __sqlExecute(self,sql):
        """
        excecute a sql statment
         
        @var: sql , a well form sql statment.
        
        exception: defaultEXC 
         
        """
        try:
            LOG.debug("sqlExecute: %s"%(sql))
            
            cursor  = self.__dbConnection.cursor()
            cursor.execute(sql)
            self.__dbConnection.commit()  
        except (mysql.connector.Error) as e:
            raise defaultEXC("mysql error %s"%(e))
        except :
            raise defaultEXC("unkown error sql:%s"%(sql),True)    
    
    def __dbClose(self):
        '''
        
        close the database connection
        
        catch all errors and exception with no error or LOG
        
        return: none
        
        exception: none
        '''
        try:
            if self.__dbConnection:
                LOG.info("close database")
                self.__dbConnection=False
                self.__dbConnection.close()
               
        except:
            pass
        
            
    def __dbConnect(self,cfg={}):
        '''
        build a new database connection
        
        cfg={
            'host':'127.0.0.1',
            'database':'databaseName',
            'user':'username'
            'password':'password'
            'port':3306
            }
            
        exception: defaultEXC
        '''
        LOG.info("try connect to host:%s:%s with user:%s table:%s"%(cfg['host'],cfg['port'],cfg['user'],cfg['database']))
        try:
            self.__dbConnection = mysql.connector.connect(**cfg)
                                                
            #self.__dbConnection.apilevel = "2.0"
            #self.__dbConnection.threadsafety = 3
            #self.__dbConnection.paramstyle = "format" 
            #self.__dbConnection.autocommit=True
            LOG.info("mysql connect succecfull")
        except (mysql.connector.Error) as e:
            self.__dbClose()  
            self.__dbConnection=False
            raise defaultEXC("can't not connect to database: %s"%(e))
        except:
            raise defaultEXC("unkown error in modul %s"%(self.config['name']),True)
        
    def __buildSQL(self,mapping):
        '''
        build the sql string
        '''
        try:
            field=mapping["fields"]
            
            tableString=""
            valueString=""
            secound=False
            for tableEntry in field:
                if secound:
                    tableString+=","
                    valueString+=","
                secound=True
                tableString+=("`%s`"%(tableEntry))
                
                (command,commandValue)=(*field[tableEntry].keys(),*field[tableEntry].values())
                if command not in self.__mappers:
                    raise defaultEXC("can't find %s in mysqlMapper")
                
                
                valueString+=("'%s'"%(self.__mappers[command](commandValue)))
            
            sql=("INSERT INTO %s (%s) VALUES (%s);"%(mapping['table'],tableString,valueString))
            LOG.debug("build sql string:%s"%(sql))
            return sql
        except defaultEXC as e: 
            raise e
        except:
            raise defaultEXC("error in modul %s: buildSQL"%(self.config['name']),True)  
   
    def __callerValues(self,value):
        '''
        give back the Value from caller
        
        give the value from self.callerArgs back. This variable have be
        set by the update(self,vars={}) 
        
        return: the value from 
                
        exception: defaultEXC
        '''
        try:
            if value not in self.__callerARGS:
                raise defautEXC ("can't find % in callerVars"%(value))
            return self.__callerARGS[value]
        except (defaultEXC) as e:
            raise e
        except:
            raise defaultEXC("unknown err in getValue",True)
    
    