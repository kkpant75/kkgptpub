import PyPDF2
from CoreLLM import *

def extract_text_from_pdf(pdf_path):
    pdf_text = ""
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            pdf_text += page.extract_text()
    return pdf_text
	
	
def main_pdf(pdf_path, user_query):
    # Extract text from PDF
    pdf_text = extract_text_from_pdf(pdf_path)
    prompt = f"Based on the following text:\n\n{pdf_text}\n\nAnswer the following query:\n\n\n\n{user_query}"

    # Query the LLM
    answer = query_llm(prompt)
    return answer

def main_text(pdf_path, user_query):
    # Extract text from PDF
    text_text = ""
    with open(text_file_path,"r") as f:
        text_text=f.read()
    
    prompt = f"Based on the following text:\n\n{text_text}\n\nAnswer the following query:\n\n\n\n{user_query}"

    # Query the LLM
    answer = query_llm(prompt)
    return answer
    
if __name__ == "__main__":
    # Example usage
    pdf_path = "C:\\Users\\Kamlesh\\Downloads\\Kamlesh Pant 0724T.pdf"   
    
    while True:
        user_query = input("Enter your query: ")
        try:          
            answer = main_pdf(pdf_path, user_query)
    
            print(answer)               
        except Exception as e:
            print(f"An error occurred: {e}")
            

# if __name__ == "__main__":
    # # Example usage
    # text_file_path="D:\\Work\\Rentcast\\CSV\\Processed\\20240713-CA-2.csv"

    # while True:
        # user_query = input("Enter your query: ")
        # try:          
            # answer = main_text(text_file_path, user_query)
    
            # print(answer)               
        # except Exception as e:
            # print(f"An error occurred: {e}")