import openai
from Utilities import *

openai.api_key = os.getenv('OPENAI_API_KEY')

def create_connection():
    #ssh -L 3307:starburst-ur-mysql-db.czajb75xt9ny.us-west-2.rds.amazonaws.com:3306 ubuntu@bastionur
    return DBConnection('MYSQL',0)

def query_llm_prompt(prompt):
    response = openai.Completion.create(
    model="gpt-3.5-turbo-instruct",
    prompt=prompt,
    max_tokens=150
    )
    return response.choices[0].text.strip()
 
def query_llm(prompt):
    try:
        print("im message based =====>"+prompt)
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0125",
            messages=[
                # {"role": "system", "content": "99 % accuracy in responding the user query \
                # User Query -Provide weather forecast  or nay query ralted to location wikipedia browse web\
                # Answer - weather details  wikipedeia summary URL links "},
                {"role": "system", "content": "be accurate in answering all queries"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150
        )
        #print(response.choices[0].message['content'])
        
        return response.choices[0].message['content'].strip().split('sql')[1].split("```")[0]
    except Exception as e:
        return response.choices[0].message['content'].strip()

def execute_query(query):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    print('results',results)
    cursor.close()
    connection.close()
    return results

def natural_language_to_sql(natural_language_query):
    prompt = f"Convert the following natural language query to an SQL query: {natural_language_query}"
    sql_query = query_llm(prompt)
    return sql_query

def get_results_from_natural_language_query(natural_language_query):
    sql_query = natural_language_to_sql(natural_language_query)
    print(sql_query)
    results = execute_query(sql_query)
    return results

# while (True):
    # print(query_llm(input("Enter your query: ")))