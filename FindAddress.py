from CoreLLM import *

jsonAdd=    [{
        "id": "4-Kiki-Pl,-Pacific-Palisades,-CA-90272",
        "formattedAddress": "4 Kiki Pl, Pacific Palisades, CA 90272",
        "addressLine1": "4 Kiki Pl",
        "addressLine2": None,
        "city": "Pacific Palisades",
        "state": "CA",
        "zipCode": "90272",
        "county": "Los Angeles",
        "latitude": 34.039123,
        "longitude": -118.536275,
        "propertyType": "Manufactured",
        "bedrooms": 2,
        "bathrooms": 2,
        "squareFootage": 1200,
        "lotSize": 3307,
        "yearBuilt": 1974,
        "status": "Active",
        "price": 1339000,
        "listedDate": "2024-06-27T00:00:00.000Z",
        "removedDate": None,
        "createdDate": "2024-03-08T00:00:00.000Z",
        "lastSeenDate": "2024-08-13T13:42:00.425Z",
        "daysOnMarket": 49
    },
    {
        "id": "E-165th-St,-Lancaster,-CA-93535",
        "formattedAddress": " 	",
        "addressLine1": "E 165th St",
        "addressLine2": None,
        "city": "Lancaster",
        "state": "CA",
        "zipCode": "93535",
        "county": "Los Angeles",
        "latitude": 34.740329,
        "longitude": -117.839406,
        "propertyType": "Land",
        "lotSize": 110642,
        "status": "Active",
        "price": 24950,
        "listedDate": "2024-06-27T00:00:00.000Z",
        "removedDate": None,
        "createdDate": "2024-06-28T00:00:00.000Z",
        "lastSeenDate": "2024-08-13T13:42:00.424Z",
        "daysOnMarket": 49
    },
    {
        "id": "108-W-84th-St,-Los-Angeles,-CA-90003",
        "formattedAddress": "108 W 84th St, Los Angeles, 	CA 90003",
        "addressLine1": "108 W 84th St",
        "addressLine2": None,
        "city": "Los Angeles",
        "state": "CA",
        "zipCode": "90003",
        "county": "Los Angeles",
        "latitude": 33.963109,
        "longitude": -118.274355,
        "propertyType": "Multi-Family",
        "bedrooms": 9,
        "bathrooms": 5,
        "squareFootage": 2400,
        "lotSize": 4222,
        "yearBuilt": 1928,
        "status": "Active",
        "price": 850000,
        "listedDate": "2024-06-27T00:00:00.000Z",
        "removedDate": None,
        "createdDate": "2024-06-28T00:00:00.000Z",
        "lastSeenDate": "2024-08-13T13:42:00.424Z",
        "daysOnMarket": 49
    }]
	
def FindMatchingAddress(actulaAddressDatabase, queryAddress):
    try:
        #answer=	None
        prompt = (f"\n\nAnalyze the text and respond with Actual Address if it has 99% Matching Address"
                  f"\n\nHere are some examples to guide you:\n\n"
                  f"Example 1:\n"
				  f"Text:'id: 4-Kiki-Pl,-Pacific-Palisades,-CA-90272, formattedAddress: 4 Kiki Pl, Pacific Palisades, CA 90272'"
                  f"\nQueryAddress : '4 Kiki Pl, P'\n\n"
                  f"Answer:  '4 Kiki Pl, Pacific Palisades, CA 90272'\n\n"
                  f"Example 2:\n"
				  f"Text: 'id: 108-W-84th-St,-Los-Angeles,-CA-90003, formattedAddress: 108 W 84th St, Los Angeles, 	CA 90003, addressLine1: 108 W 84th St,24-08-13T13:42:00.424Z'"
                  f"\nQueryAddress: '	08-W-84th-St'\n"
                  f"Answer:  '108 W 84th St, Los Angeles, 	CA 90003\n\n"    
                  f"Now analyze the following text:\n\n{actulaAddressDatabase}\n\n"
                  f"QueryAddress: {queryAddress}\n"
				  f"Answer:")
                 
                  
        #print(prompt)		  
        response = openai.Completion.create(
            model="gpt-3.5-turbo-instruct",
            prompt=prompt,
            max_tokens=20,
            temperature=0,
            frequency_penalty=0.5,
            presence_penalty=0.5,
        )
        #print(response)
        answer = response.choices[0].text.strip()#.lower()
        #print(answer)
        return answer 
    except Exception as e:
        logging.error(f"Error querying OpenAI: {e}")
        return answer

def GetMatchingAddress():
	jsonAdd=[]
	minimumData={}
	f=open("D:\Work\kkgpt\Data\AddressFile.json")
	jsonbuffer=json.load(f)
	for data in jsonbuffer:
		for k,v in data.items():
			if k in('id','formattedAddress'):
				minimumData[k]=v
		#print(minimumData)	
		jsonAdd.append(minimumData)
	
	#print(jsonAdd)s
	while True:
		queryAddress = input("\n\nQuery Address: ")	
		answer=FindMatchingAddress(str(jsonAdd),queryAddress)
		print(answer)
		
#GetMatchingAddress()

def GetFormattedAddress(badFormatAddress):
    try:
        prompt = (f"\n\Reformat the Provided Bad Address As per USA standard address format"
                  f"\n\nHere are some examples to guide you:\n\n"
                  f"Example 1:\n"
                  f"Text:'3030 Mckinney Ave Unit 2302,Dallas,TX,75204"
                  f"\nFormattedAddress : 'Convert Unit to Apt and format as per USA Address System with comma seperated'\n\n"
                  f"Response:  '3030 McKinney Ave, Apt 2302, Dallas, TX 7520\n\n"    
                  f"Example 2:\n"
                  f"Text:'316706 E Hammon,Montgomery,TX"
                  f"\nFormattedAddress : 'Convert Unit to Apt , Street is st , Road is rd , Lane is ln ,Avenue is Ave ,Apartment is apt ,Boulevard is blvd ,Drive is dr, Parkway is pkwyand format as per USA Address System with comma seperated and add zip code'\n\n"
                  f"Response:  '316706 E Hammon, Montgomery, TX 77316\n\n"    
				  f"Example 3:\n"
                  f"Text:'316706 E Hammon,Montgomery,TX|822 Gavin Walker Dr,Rosharon"
                  f"\nFormattedAddress : 'Reformat as per USA address standars for bulk address input seperated by | add zip code if misisng and response as key value'\n\n"
                  f"Response: 1:316706 E Hammon, Montgomery, TX 77316\n2:822 Gavin Walker Dr, Rosharon, TX 77583"    
                  f"Now Reformat  {badFormatAddress}\n\n"
                  f"Response:")
        
        response = openai.Completion.create(
                model="gpt-3.5-turbo-instruct",
                prompt=prompt,
                max_tokens=50,
                temperature=0,
                frequency_penalty=0.5,
                presence_penalty=0.5,
            )
        #print(response)
        answer = response.choices[0].text.strip()#.lower()
        #print(answer)
        return answer 
    except Exception as e:
        logging.error(f"Error querying OpenAI: {e}")
        return None
    
    
def GetUSFormatAddress():
    while True:
        queryAddress = input("\n\nQuery Bad Format Address: ")    
        answer=GetFormattedAddress(queryAddress)
        print(answer)

GetUSFormatAddress()
