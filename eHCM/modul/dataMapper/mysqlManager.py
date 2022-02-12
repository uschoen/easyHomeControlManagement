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
import time
try:
    import mysql.connector                                                         #@UnresolvedImport
    from mysql.connector import Error                                              #@UnresolvedImport,@UnusedImport
    from mysql.connector import errorcode                                          #@UnresolvedImport,@UnusedImport
except:
    raise defaultEXC("no mysql.connector module installed")

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
            LOG.info("call update from MysqlMapper with args %s"%(values))
            self.__callerARGS.update(values)
            
                
            sql=""
               
            dbConnection=self.__dbConnect(self.config['database'])
            sql=self.__buildSQL(self.config["mapping"])
            self.__sqlExecute(dbConnection,sql)
            self.__dbClose(dbConnection)
            LOG.debug("call update from MysqlMapper finish")
        except defaultEXC as e:
            self.__dbClose(dbConnection)
            LOG.critical("error in mysqlMapper: %s with error:%s"%(self.config['name'],e))   
        except:
            self.__dbClose(dbConnection)
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
                  
    def __sqlExecute(self,dbConnection,sql):
        """
        excecute a sql statment
         
        @var: sql , a well form sql statment.
        
        exception: defaultEXC 
         
        """
        try:
            LOG.debug("sqlExecute: %s"%(sql))
            cursor  = dbConnection.cursor()
            cursor.execute(sql)
            dbConnection.commit()  
            cursor.close()
        except (mysql.connector.Error) as e:
            raise defaultEXC("mysql error %s"%(e))
        except :
            raise defaultEXC("unkown error sql:%s"%(sql),True)    
    
    def __dbClose(self,dbConnection):
        '''
        
        close the database connection
        
        catch all errors and exception with no error or LOG
        
        return: none
        
        exception: none
        '''
        try:
            if dbConnection:
                LOG.info("close database")
                dbConnection=False
                dbConnection.close()
               
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
            dbConnection = mysql.connector.connect(**cfg)
                                                
            #dbConnection.apilevel = "2.0"
            dbConnection.threadsafety = 2
            #dbConnection.paramstyle = "format" 
            #dbConnection.autocommit=True
            LOG.info("mysql connect succecfull")
            return dbConnection
        except (mysql.connector.Error) as e:
            self.__dbClose(dbConnection)  
            dbConnection=False
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
                raise defaultEXC ("can't find %s in callerVars"%(value))
            return self.__callerARGS[value]
        except (defaultEXC) as e:
            raise e
        except:
            raise defaultEXC("unknown err in getValue",True)
    
    