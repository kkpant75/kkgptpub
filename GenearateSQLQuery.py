from CoreLLM import *

Tables={
"homelisted":["Price","listeddate","addressline1","city","state","zipcode","county","propertytype"],
"leadgendim":["offer","loansavings","equity","newrate","newtotalmonthlypaymentamt","maxborrowableamount","newloanamount","consideredloanproduct","consideredloantype"]
}

# Tables={
# "homelisted":["Price","listeddate"],
# "leadgendim":["Price","loansavings"]
# }

def MYSQLConnection():
	import pymysql
	
	#Create connection
	conn = pymysql.connect(
    host="localhost",
    user="root",
    password="mysql",
    database="world"
	)
	
	LogMessageInProcessLog("MYSQL DB Connection Succesfull\n\n\n")			
	return conn

def GetDataFromDBMySql(query):
	conn=MYSQLConnection()
	cursor = conn.cursor()
	cursor.execute(query)
	data=cursor.fetchall()
	#print(data)
	#print(len(data))
	cols=""
	for k in data:
		cols+=k[0]+","
	return cols[0:-1]
#tableName='city'
#print(GetDataFromDBMySql("SELECT Column_name FROM INFORMATION_SCHEMA.columns WHERE table_schema = 'world' and table_name='"+tableName+"'"))

def GetDBObjectINFO(tableName='city',dbname='world'):
	Query=f"SELECT Column_name FROM INFORMATION_SCHEMA.columns WHERE table_schema = '{dbname}' and table_name='{tableName}'"
	#Query="SELECT Column_name FROM INFORMATION_SCHEMA.columns WHERE table_name='"+tableName+"'"
	print(Query)
	return GetDataFromDBMySql(Query)
	
def GetSQLQueryDB(promptquery):
	try:
		tableName=promptquery.split(',')[0].strip()
		tableCols=""
		if '.' in tableName:
			tableCols=GetDBObjectINFO(tableName.split('.')[1],tableName.split('.')[0])
		else:	
			tableCols=GetDBObjectINFO(tableName)
		print(tableCols)
		if (len(tableCols)==0):
			return "NO SUCH TABLE EXISTS..."
			
		prompt = (f"Get highest or max  price for homelisted \n\n"
				f"Response: select max(price) from homelisted where city='texa'"
				f"Get listdate,address and zipcode for homelisted table where city='sanjose'\n\n"
				f"Response: select listeddate,addressline1,city,zipcode from homelisted where city='texaz'"
				f"Now Geneate Query {promptquery} for {tableName} from  column data {tableCols}\n\n"
				f"Response:")
		
		response = openai.Completion.create(
				model="gpt-3.5-turbo-instruct",
				prompt=prompt,
				max_tokens=50,
				temperature=0,
				frequency_penalty=0.5,
				presence_penalty=0.5,
			)
		#print(prompt)
		answer = response.choices[0].text.strip()#.lower()
		#print(answer)
		return "\n\n"+answer 
	except Exception as e:
		logging.error(f"Error querying OpenAI: {e}")
		return None

#################################################POSTGRES################################################################

def GetPGDBObjectINFO(tableName='employee',dbname='public'):
	Query=f"SELECT Column_name FROM INFORMATION_SCHEMA.columns WHERE table_schema = '{dbname}' and table_name='{tableName}'"
	#Query="SELECT Column_name FROM INFORMATION_SCHEMA.columns WHERE table_name='"+tableName+"'"
	print(Query)
	return GetMetaDataFromPGDB(Query)
	
def GetSQLQueryPGDB(promptquery):
	try:
		tableName=promptquery.split(',')[0].strip()
		tableCols=""
		if '.' in tableName:
			tableCols=GetPGDBObjectINFO(tableName.split('.')[1],tableName.split('.')[0])
		else:	
			tableCols=GetPGDBObjectINFO(tableName)
		print(tableCols)
		if (len(tableCols)==0):
			return "NO SUCH TABLE EXISTS..."
			
		prompt = (f"Get highest or max  price for homelisted \n\n"
				f"Response: select max(price) from homelisted where city='texa'"
				f"Get listdate,address and zipcode for homelisted table where city='sanjose'\n\n"
				f"Response: select listeddate,addressline1,city,zipcode from homelisted where city='texaz'"
				f"Now Geneate Query {promptquery} for {tableName} from  column data {tableCols}\n\n"
				f"Response:")
		
		response = openai.Completion.create(
				model="gpt-3.5-turbo-instruct",
				prompt=prompt,
				max_tokens=50,
				temperature=0,
				frequency_penalty=0.5,
				presence_penalty=0.5,
			)
		print(prompt)
		answer = response.choices[0].text.strip()#.lower()
		#print(answer)
		return "\n\n"+answer 
	except Exception as e:
		logging.error(f"Error querying OpenAI: {e}")
		return None

	
def GetSQLQuery(promptquery):
	try:
		tableName=promptquery.split(',')[0]
		
		prompt = (f"Get highest or max  price for homelisted \n\n"
				f"Response: select max(price) from homelisted where city='texa'"
				f"Get listdate,address and zipcode for homelisted table where city='sanjose'\n\n"
				f"Response: select listeddate,addressline1,city,zipcode from homelisted where city='texaz'"
				f"Now Geneate Query {promptquery} for {tableName} from  column data {Tables[tableName]}\n\n"
				f"Response:")
		
		response = openai.Completion.create(
				model="gpt-3.5-turbo-instruct",
				prompt=prompt,
				max_tokens=50,
				temperature=0,
				frequency_penalty=0.5,
				presence_penalty=0.5,
			)
		#print(prompt)
		answer = response.choices[0].text.strip()#.lower()
		#print(answer)
		return "\n\n"+answer 
	except Exception as e:
		logging.error(f"Error querying OpenAI: {e}")
		return None

def GetSQLQueryJoin(promptquery):
	try:
		tableNames=promptquery.split('|')[0].split(',')
		prompt = (f"join  {tableNames} and loop the array find tables to join and get consdtion from {promptquery.split('|')[1]} and build query by extracting given columnnames in {promptquery.split('|')[2]}\n\n"
				f"Response: select a.firstablecolumn,a.fisttablecolumn, b.secondtableClumn,b.secondtabecolumn from firstable a,secondtable b where a.{promptquery.split('|')[1]}=b.{promptquery.split('|')[1]}"
				
				f"Now Geneate Query {promptquery} for {tableNames} from  column data {Tables[tableName]}\n\n"
				f"Response:")
		
		response = openai.Completion.create(
				model="gpt-3.5-turbo-instruct",
				prompt=prompt,
				max_tokens=50,
				temperature=0,
				frequency_penalty=0.5,
				presence_penalty=0.5,
			)
		#print(prompt)
		answer = response.choices[0].text.strip()#.lower()
		#print(answer)
		return "\n\n"+answer 
	except Exception as e:
		logging.error(f"Error querying OpenAI: {e}")
		return None
		
while (True):
	print(GetSQLQueryDB(input("\nEnter your query: ")))
	#print(GetSQLQueryPGDB(input("\nEnter your query: ")))
    #print(GetSQLQuery(input("\nEnter your query: ")))
	#print(GetSQLQueryJoin(input("\nEnter your query: ")))
ClosePGDB()