import pyodbc
import json
import boto3
import time
import datetime
import requests
import os
import zipfile
import shutil
import re
import sys
import math
import platform
#import xmltodict
from pytz import timezone
import logging
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.

starttime=datetime.datetime.now()

ConfigFileName=os.getenv('CONFIG_FILE_NAME')

ConFileChnageTime=os.stat(ConfigFileName).st_mtime
#print(ConFileChnageTime)
#print(os.getcwd()+"//..")
with open("Application.properties") as app_file:
    appProperty=app_file.readlines()
    for confdata in appProperty:
        if "CONFIGFILE" ==(confdata.split("=")[0].strip()).upper():
            print(confdata.split("=")[1].strip())

with open(ConfigFileName) as json_file:
	configdata=json.load(json_file)

if os.name=='nt':
	configdata['OSTypePath']="\\"
	#configdata['SYSTEM_PARAMETERS']['LOCAL_FILE_PATH']=configdata['LOCAL_FILE_PATH_WINDOW']
elif os.name=='posix':
	configdata['OSTypePath']="/"
	### Get Kerberos Ticket To Secure Login
	os.system("echo "+configdata['Password']+"|kinit "+configdata['Username'].split('\\')[1])

if configdata['SYSTEM_PARAMETERS']['LOCAL_FILE_PATH'][0:2]=="//": 
	configdata['OSTypePath']="/"

EntityName=configdata['SYSTEM_PARAMETERS']['ENTITY_NAME']

def EpochTimeConversion(Time,Format):
	utc_time = datetime.datetime.strptime(Time, Format)
	epoch_time = (utc_time - datetime.datetime(1970, 1, 1)).total_seconds()
	#print(epoch_time)
	return int(epoch_time)
	

def DBConnection(DBType,Index):
	if DBType.upper()=='MSSQL':		
		return MSSQLConnection(Index)	
	elif DBType.upper()=='MYSQL':
		return MYSQLConnection(Index)
	elif DBType.upper()=='SNOWFLAKE':
		return SNOWFLAKEConnection(Index)

def MSSQLConnection(Index):
	if configdata['SYSTEM_PARAMETERS']['CREDENTIAL']=='SYSTEM_ENVIRONMENT':
		configdata['DATABASE']['MSSQL'][Index]['PASSWORD']=os.getenv('MSSQL_DBPASSWORD'+'_'+str(Index))

	try:
		if  configdata['DATABASE']['MSSQL'][Index]['AUTH_TYPE'].upper()=="WINLOGIN":
			cnxn= pyodbc.connect(r"Driver="+configdata['DATABASE']['MSSQL'][Index]['DRIVER']+";Server="+configdata['DATABASE']['MSSQL'][Index]['SERVER']+";Database="+configdata['DATABASE']['MSSQL'][Index]['NAME']+";Trusted_Connection=yes;")
			LogMessageInProcessLog("MSSQL Secure DB Connection Succesfull")
			return cnxn

		else:
			cnxn= pyodbc.connect(r"Driver="+configdata['DATABASE']['MSSQL'][Index]['DRIVER']+";Server="+configdata['DATABASE']['MSSQL'][Index]['SERVER']+";Database="+configdata['DATABASE']['MSSQL'][Index]['NAME']+';UID='+configdata['DATABASE']['MSSQL'][Index]['USERNAME']+';PWD='+ configdata['DATABASE']['MSSQL'][Index]['PASSWORD'])		
			LogMessageInProcessLog("MSSQL DB Connection Succesfull")
			return cnxn
	except Exception as e:
		LogMessageInProcessLog("Exception Raiased in "+sys._getframe().f_code.co_name +"...."+str(e))
		raise Exception(str(e))

def MYSQLConnection(Index):
	import mysql.connector

	if configdata['SYSTEM_PARAMETERS']['CREDENTIAL']=='SYSTEM_ENVIRONMENT':
		configdata['DATABASE']['MYSQL'][Index]['PASSWORD']=os.getenv('MYSQL_DBPASSWORD'+'_'+str(Index))
 
	dbport=3306
	print('dbport',dbport)
	if "PORT" in configdata['DATABASE']['MYSQL'][Index]:
		dbport=configdata['DATABASE']['MYSQL'][Index]['PORT']
	try:
		LogMessageInProcessLog("begin MYSQL DB Connection Succesfull\n\n\n")
		print(configdata['DATABASE']['MYSQL'][Index]['SERVER'],configdata['DATABASE']['MYSQL'][Index]['USERNAME'],configdata['DATABASE']['MYSQL'][Index]['PASSWORD'])
		cnxn= mysql.connector.connect(
		host=configdata['DATABASE']['MYSQL'][Index]['SERVER'],
		database=configdata['DATABASE']['MYSQL'][Index]['NAME'],
		user=configdata['DATABASE']['MYSQL'][Index]['USERNAME'],
		password=configdata['DATABASE']['MYSQL'][Index]['PASSWORD'],
		port=dbport)
		LogMessageInProcessLog("MYSQL DB Connection Succesfull\n\n\n")			
		
		return cnxn
	except Exception as e:
		LogMessageInProcessLog("Exception Raiased in "+sys._getframe().f_code.co_name +"...."+str(e))
		raise Exception(str(e))


def SNOWFLAKEConnection(Index):
	if configdata['SYSTEM_PARAMETERS']['CREDENTIAL']=='SYSTEM_ENVIRONMENT':
		configdata['DATABASE']['SNOWFLAKE'][Index]['PASSWORD']=os.getenv('SNOWFLAKE_DBPASSWORD'+'_'+str(Index))
	try:
		cnxn= pyodbc.connect("DSN="+configdata['DATABASE']['SNOWFLAKE'][Index]['DSN']+';UID='+configdata['DATABASE']['SNOWFLAKE'][Index]['USERNAME']+';PWD='+ configdata['DATABASE']['SNOWFLAKE'][Index]['PASSWORD'])
	
		LogMessageInProcessLog("SnowFlake DB Connection Succesfull")
		return cnxn		
	except Exception as e:
		LogMessageInProcessLog("Exception Raiased in "+sys._getframe().f_code.co_name +"...."+str(e))
		raise Exception(str(e))


### Print Log Message	
def LogMessageInProcessLog(LogMessage):	
	
	if configdata['PROCESS_LOG']['ENABLE_FILE_LOGGING'].upper()=='YES':
		logging.error(LogMessage)
	if configdata['PROCESS_LOG']['PRINT_LOG_MESSGAE_ON_CONSOLE'].upper()=='YES':
		print(LogMessage)
	#	print("calll insid..",LogMessage)

### Log Configuration 

def SetProcessLogConfiguration():
	LogFilePath=configdata['SYSTEM_PARAMETERS']['LOCAL_FILE_PATH']+configdata['OSTypePath']+"Logs"+configdata['OSTypePath']
		
	LogLevel=configdata['PROCESS_LOG']['LOG_LEVEL'].upper().replace("ERROR","40").replace("WARNING","30").replace("INFO","20").replace("DEBUG","10") ##ERROR 40|WARNING	30|INFO	20|DEBUG 10
	
	if not os.path.exists(LogFilePath):
		os.makedirs(LogFilePath)	
		
	for file in os.listdir(LogFilePath):
		LogFileName=LogFilePath+file	
		CurrentLogFileSize=os.stat(LogFileName).st_size
		FileCreatedDaysBack= (EpochTimeConversion(str(datetime.datetime.now().astimezone(timezone(configdata['SYSTEM_PARAMETERS']['TIMEZONE']))).split('.')[0],'%Y-%m-%d %H:%M:%S')- os.stat(LogFileName).st_ctime) //86400
		#print(FileCreatedDaysBack)
		if (FileCreatedDaysBack  >=configdata['PROCESS_LOG']['LOG_FILE_RETENTION_PERIOD'] or CurrentLogFileSize >= configdata['PROCESS_LOG']['LOG_FILE_MAX_FILE_SIZE']):
			print("\nLog File <{}> Is Deleted Current File Size <{}> Has Crossed The Permiiited Limit <{}>Big Or Its <{}> Days Old In System -Created Date <{}>\n".format(LogFileName,CurrentLogFileSize,configdata['PROCESS_LOG']['LOG_FILE_MAX_FILE_SIZE'],FileCreatedDaysBack,time.ctime(os.stat(LogFileName).st_ctime)))
			try:
				os.remove(LogFileName)
			except Exception as e:
				print(e)
		
	LogFileName=LogFilePath+configdata['PROCESS_LOG']['LOG_FILE_NAME']+starttime.strftime('%Y%m%d')+".txt"
	logging.basicConfig(filename=LogFileName,format='%(asctime)s %(message)s', filemode='a',level=int(LogLevel))

def GetDataFromMYSQL(QueryString):	
	try:
		data=[]
		coxn=DBConnection('MYSQL',GetItemIndex(configdata['SEARCH_STRING_FOR_INDEX']['MYSQL1']))
		cursorr = coxn.cursor()
		cursorr.execute('SELECT * FROM world.city')
		for j in cursorr:
			data.append(j)
			#print(j)
			
		return str(data)[1:-1] ## send table data as values()tuple
	except Exception as e:
		LogMessageInProcessLog("Exception Raiased in "+sys._getframe().f_code.co_name +"...."+str(e))
		raise Exception(str(e))
	finally:
		cursorr.close()
		coxn.close()

def SnowTest(idx):	
	coxn=DBConnection('SNOWFLAKE',idx)
	cursorr = coxn.cursor()
	try:
		#cursorr.execute("SELECT current_version()")
		#one_row = cursorr.fetchall()
		#print(one_row)
		
		#cursorr.execute("CREATE  DATABASE IF NOT EXISTS  SNOWDBKK")
		#cursorr.execute("CREATE  SCHEMA IF NOT EXISTS  SNOWDBKK.SNOWSCHEMAKK")
		#cursorr.execute("CREATE  TABLE IF NOT EXISTS  SNOWDBKK.SNOWSCHEMAKK.SNOWTABLEKK(Name Varchar(30),Age Number(10),City Varchar(20))")
		#cursorr.execute("INSERT INTO SNOWDBKK.SNOWSCHEMAKK.SNOWTABLEKK VALUES('Kamlesh',10,'Blr'),('Kamlesh1',101,'Blr1')")
		cursorr.execute("SELECT CC_CALL_CENTER_SK,CC_MANAGER,CC_MARKET_MANAGER from SNOWFLAKE_SAMPLE_DATA.TPCDS_SF100TCL.CALL_CENTER Limit 10")
		for j in cursorr.fetchall():
			print(j)
			
	except Exception as e:
		LogMessageInProcessLog("Exception Raiased in "+sys._getframe().f_code.co_name +"...."+str(e))
		raise Exception(str(e))
	finally:
		cursorr.close()
		coxn.commit()
		coxn.close()
global ses
ses=0

def SnowPushViaKafka(idx,DataFromKafka):	
	global ses
	global coxn
	if ses==0:		
		coxn=DBConnection('SNOWFLAKE',idx)
		ses=1
	cursorr = coxn.cursor()
	try:
		
		cursorr.execute("CREATE  DATABASE IF NOT EXISTS  SNOWDBKK")
		cursorr.execute("CREATE  SCHEMA IF NOT EXISTS  SNOWDBKK.SNOWSCHEMAKK")
		cursorr.execute("CREATE  TABLE IF NOT EXISTS SNOWDBKK.SNOWSCHEMAKK.SNOWTABLEKK( \
			ID    Number(10), \
			NAME  Varchar(45), \
			COUNTRYCODE   Varchar(45), \
			DISTRICT Varchar(45),\
			POPULATION  Number(10))"
		)
		
		#for data in eval(DataFromKafka):
		#	print(str(data))
		cursorr.execute("INSERT INTO SNOWDBKK.SNOWSCHEMAKK.SNOWTABLEKK VALUES"+str(DataFromKafka))

			
	except Exception as e:
		LogMessageInProcessLog("Exception Raiased in "+sys._getframe().f_code.co_name +"...."+str(e))
		raise Exception(str(e))
	finally:
		cursorr.close()
		coxn.commit()
		#coxn.close()


def SalesForcePushViaKafka(idx,DataFromKafka,APIName,TableName):	
	global ses
	global coxn
	if ses==0:
		coxn=DBConnection('MYSQL',idx)
		ses=1
	cursorr = coxn.cursor()
	try:
		TableColNames="("
		cursorr.execute("CREATE  DATABASE IF NOT EXISTS  TCRM")
		#cursorr.execute("CREATE  SCHEMA IF NOT EXISTS  TCRM.TCRMSCHMA")
		TableColumns=(configdata['SALESFORCE']['GETAPI'][APIName]['QueryOrHeaderParameters']).split('+')[1].split(',')
		#print(QueryColumns)
		for col in TableColumns:
			TableColNames+=col+" varchar(100),"

		TableColNames=TableColNames[0:-1]+")" 

		cursorr.execute("CREATE  TABLE IF NOT EXISTS TCRM."+TableName+TableColNames)

		cursorr.execute("INSERT INTO TCRM."+TableName+ " VALUES "+str(DataFromKafka))

		LogMessageInProcessLog("INSERT INTO TCRM."+TableName+ " VALUES "+str(DataFromKafka))	
	except Exception as e:
		LogMessageInProcessLog("Exception Raiased in "+sys._getframe().f_code.co_name +"...."+str(e))
		raise Exception(str(e))
	finally:
		cursorr.close()
		coxn.commit()
		#coxn.close()

def SalesForceCDCInject(idx,DataFromKafka,TableName):	
	global ses
	global coxn
	if ses==0:
		coxn=DBConnection('MYSQL',idx)
		ses=1
	cursorr = coxn.cursor()
	try:

		cursorr.execute("CREATE  DATABASE IF NOT EXISTS  TCRM")

		TableColNames="(CreatedDate datetime,ActionType varchar(50),ActionDetailsJson json)"
		
		cursorr.execute("CREATE  TABLE IF NOT EXISTS TCRM."+TableName+TableColNames)

		cursorr.execute("INSERT INTO TCRM."+TableName+ " VALUES "+str(DataFromKafka))

		LogMessageInProcessLog("INSERT INTO TCRM."+TableName+ " VALUES "+str(DataFromKafka))	
	except Exception as e:
		LogMessageInProcessLog("Exception Raiased in "+sys._getframe().f_code.co_name +"...."+str(e))
		raise Exception(str(e))
	finally:
		cursorr.close()
		coxn.commit()
		#coxn.close()


def CreteDynamicTableAsPerFileHeader(Index,FileName):
	with open(FileName, 'r') as file:
		global TableStructure
		TableStructure=""			
		for header_data in file.readlines():
			#print(header_data)
			for col in header_data.replace("\n","").split(configdata['DATABASE']['SNOWFLAKE'][Index]['FILE_FIELD_DELIMITER']):
				TableStructure+= col + "  varchar(100),"
			TableStructure="("+TableStructure[:-1]+")"
				#print(TableStructure)
			break
	
	global ses
	
	if ses==0:		
		global coxn	
		coxn=DBConnection('SNOWFLAKE',Index)
		ses=1
	cursorr = coxn.cursor()
	try:
		#/Create Database
		cursorr.execute("CREATE  DATABASE IF NOT EXISTS  "+\
		configdata['DATABASE']['SNOWFLAKE'][Index]['NAME'])
		
		#Create Schema
		cursorr.execute("CREATE  SCHEMA IF NOT EXISTS  "+\
		configdata['DATABASE']['SNOWFLAKE'][Index]['NAME']+"."+\
		configdata['DATABASE']['SNOWFLAKE'][Index]['SCHEMA'])
		
		#Create Table 
		DynamicTableName=configdata['DATABASE']['SNOWFLAKE'][Index]['NAME']+"."+\
		configdata['DATABASE']['SNOWFLAKE'][Index]['SCHEMA']+"."+\
		configdata['DATABASE']['SNOWFLAKE'][Index]['TABLE_PREFIX']+FileName.split(".")[0].upper()
		
		cursorr.execute("CREATE  TABLE IF NOT EXISTS "+ DynamicTableName+ TableStructure)
		return DynamicTableName
		
	except Exception as e:
		LogMessageInProcessLog("Exception Raiased in "+sys._getframe().f_code.co_name +"...."+str(e))
		raise Exception(str(e))
	finally:
		cursorr.close()
		coxn.commit()
		#coxn.close()

def LoadFileInStageArea(Index,FileName):
	DynamicTableName=CreteDynamicTableAsPerFileHeader(Index,FileName)
	
	global ses
	if ses==0:		
		global coxn	
		coxn=DBConnection('SNOWFLAKE',Index)
		ses=1
	cursorr = coxn.cursor()
	try:
	
		cursorr.execute("CREATE FILE FORMAT IF NOT EXISTS "+\
		configdata['DATABASE']['SNOWFLAKE'][Index]['NAME']+"."+\
		configdata['DATABASE']['SNOWFLAKE'][Index]['SCHEMA']+"."+\
		configdata['DATABASE']['SNOWFLAKE'][Index]['FILE_FORMAT_NAME']+\
			" TYPE = '"+configdata['DATABASE']['SNOWFLAKE'][Index]['FILE_FORMAT_TYPE']+\
			"' FIELD_DELIMITER= '"+configdata['DATABASE']['SNOWFLAKE'][Index]['FILE_FIELD_DELIMITER']+\
			"' SKIP_HEADER = 1;")
		   
		cursorr.execute("CREATE OR REPLACE STAGE "+\
		configdata['DATABASE']['SNOWFLAKE'][Index]['NAME']+"."+\
		configdata['DATABASE']['SNOWFLAKE'][Index]['SCHEMA']+"."+\
		configdata['DATABASE']['SNOWFLAKE'][Index]['STAGE_NAME']+\
		" FILE_FORMAT = "+\
			configdata['DATABASE']['SNOWFLAKE'][Index]['NAME']+"."+\
			configdata['DATABASE']['SNOWFLAKE'][Index]['SCHEMA']+"."+\
			configdata['DATABASE']['SNOWFLAKE'][Index]['FILE_FORMAT_NAME']+";")
		
		#### Need to work on this how to automate the data load process using put command which need snowql
		LoadCommand=(configdata['DATABASE']['SNOWFLAKE'][Index]["SNOWSQL_CMD"]+\
		#" -a "+configdata['DATABASE']['SNOWFLAKE'][Index]['CONNECTION_URI'].split(".")[0]+\
		#" -u "+configdata['DATABASE']['SNOWFLAKE'][Index]['USERNAME']+\
		#" -P "+configdata['DATABASE']['SNOWFLAKE'][Index]['PASSWORD']+\
		#" -w "+configdata['DATABASE']['SNOWFLAKE'][Index]['WAREHOUSE']+\
		" -q "+'"Put file://'+configdata['SYSTEM_PARAMETERS']['LOCAL_FILE_PATH']+FileName +\
		" @"+configdata['DATABASE']['SNOWFLAKE'][Index]['NAME']+"."+\
		configdata['DATABASE']['SNOWFLAKE'][Index]['SCHEMA']+"."+\
		configdata['DATABASE']['SNOWFLAKE'][Index]['STAGE_NAME']+'";')
		LogMessageInProcessLog(LoadCommand)
		os.system(LoadCommand)
		
		#### Copy stage data into table
		CopyQuery="COPY INTO "+DynamicTableName+\
		" FROM @"+\
		configdata['DATABASE']['SNOWFLAKE'][Index]['NAME']+"."+\
		configdata['DATABASE']['SNOWFLAKE'][Index]['SCHEMA']+"."+\
		configdata['DATABASE']['SNOWFLAKE'][Index]['STAGE_NAME']+\
		"/"+FileName+";"
		
		LogMessageInProcessLog(CopyQuery)
		cursorr.execute(CopyQuery)

		'''
		CREATE FILE FORMAT mycsvformat
		   TYPE = "CSV"
		   FIELD_DELIMITER= ','
		   SKIP_HEADER = 1;
		   
		CREATE OR REPLACE STAGE my_stage    FILE_FORMAT = mycsvformat;

		Put file://C:\\Users\\kamlesh.pant\\Downloads\\result.csv @my_stage;

		Put file://D:\\SnowFlake-UR\\SNOWFLAKE\\indicity.csv @MYSQLSTAGE;
		
		copy into copysnowkk from '@mysqlstage/indicity.csv';

		create table copysnowkk as select * from snowtablekk where 1=2;

		select * From copysnowkk;
		'''
	except Exception as e:
		LogMessageInProcessLog("Exception Raiased in "+sys._getframe().f_code.co_name +"...."+str(e))
		raise Exception(str(e))
	finally:
		cursorr.close()
		coxn.commit()
		#coxn.close()


def GetItemIndex(IndexForItem):	
	for k,v in configdata.items():	
		if isinstance(v,dict):
			#print(v,type(v))
			for k1,v1 in v.items():
				if isinstance(v1,list):	
					idx=0
					for litem in v1:					
						#print(litem)
						if isinstance(litem,dict):
							#print(litem)
							for k2,v2 in litem.items():
								#print(litem[k2])
								if IndexForItem in litem[k2]:
									print(litem[k2])
									return idx 
						idx+=1
		
		
		if isinstance(v,list):	
			idx=0
			for litem in v:					
				#print(litem)
				if isinstance(litem,dict):
					#print(litem)
					for k2,v2 in litem.items():
						#print(litem[k2])
						if IndexForItem in litem[k2]:
							print(litem[k2])
							return idx 
				idx+=1
		


### Remove Escape Character
def RemoveEscapeAnsi(line):
	return re.compile(r'(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]').sub('', line).replace('\\','\\\\')
#print(RemoveEscapeAnsi('\t\u001b[0;35mSome\n\rText\u001b[0m\u001b[0;36m172.18.0.2\u001b[0m'))
						
#print(GetItemIndex('SnowflakeDSIIDriver'))
#print(GetItemIndex(configdata['SEARCH_STRING_FOR_INDEX']['MYSQL1']))	
	 
SetProcessLogConfiguration()