import os
import openai
from docx import Document
import fitz  # PyMuPDF
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Function to read .docx files
def read_docx(file_path):
    try:
        doc = Document(file_path)
        full_text = [para.text for para in doc.paragraphs]
        return '\n'.join(full_text)
    except Exception as e:
        logging.error(f"Error reading .docx file {file_path}: {e}")
        return ""

# Function to read .pdf files
def read_pdf(file_path):
    doc = fitz.open(file_path)
    full_text = []
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        full_text.append(page.get_text())
    return '\n'.join(full_text)

# Function to read files from a directory
def read_files_from_directory(directory_path):
    file_contents = {}
    for root, _, files in os.walk(directory_path):
        for file in files:
            file_path = os.path.join(root, file)
            if file.endswith('.docx'):
                file_contents[file_path] = read_docx(file_path)
            elif file.endswith('.pdf'):
                file_contents[file_path] = read_pdf(file_path)
            else:
                logging.warning(f"Unsupported file type: {file_path}")
    return file_contents

# Function to check if a file content matches a skill using OpenAI
def match_skill_in_file(file_content, skill):
    try:
        prompt = (f"Please determine if the following text contains information about the skill '{skill}'. "
                  f"Analyze the text and respond with 'Yes' if it contains relevant information about the skill and 'No' if it does not. "
                  f"Here are some examples to guide you:\n\n"
                  f"Example 1:\n"
                  f"Text: 'I have extensive experience in SQL database management and optimization.'\n"
                  f"Skill: 'SQL'\n"
                  f"Answer: Yes\n\n"
                  f"Example 2:\n"
                  f"Skill: 'starburst'\n"
                  f"Answer: Yes\n\n"
                  f"Skill: 'data mesh'\n"
                  f"Answer: Yes\n\n"     
                  f"Skill: 'data fabric'\n"
                  f"Answer: Yes\n\n"                    
                  f"Text: 'I enjoy hiking and outdoor activities.'\n"
                  f"Skill: 'SQL'\n"
                  f"Answer: No\n\n"
                  f"Example 3:\n"
                  f"Text: 'My job involved writing complex SQL queries to retrieve and analyze data.'\n"
                  f"Skill: 'SQL'\n"
                  f"Answer: Yes\n\n"
                  f"Example 4:\n"
                  f"Text: 'I attended a workshop on digital marketing last month.'\n"
                  f"Skill: 'SQL'\n"
                  f"Answer: No\n\n"
                  f"Now analyze the following text:\n\n{file_content}\n\n"
                  f"Skill: '{skill}'\n"
                  f"Answer:")
                  
        response = openai.Completion.create(
            model="gpt-3.5-turbo-instruct",
            prompt=prompt,
            max_tokens=10,
            temperature=0,
            frequency_penalty=0.5,
            presence_penalty=0.5,
        )
        answer = response.choices[0].text.strip().lower()
        return answer == 'yes'
    except Exception as e:
        logging.error(f"Error querying OpenAI: {e}")
        return False

def ReadDirectoryAndAnalyse():
    # Directory path and skill to match
    directory_path = 'C:\\Users\\kamles\\Downloads\\CVS'
    while True:
        skill_to_match = input("\n\nSearch Skills: ")

        # Read files from the directory
        files = read_files_from_directory(directory_path)

        # Find files that match the skill
        matching_files = [file_path for file_path, content in files.items() if match_skill_in_file(content, skill_to_match)]

        # Print matching files
        if matching_files:
            logging.info(f"Files matching the skill '{skill_to_match}':")
            for file in matching_files:
                logging.info(file)
        else:
            logging.info(f"No files found containing the skill: {skill_to_match}")
      
      
ReadDirectoryAndAnalyse()