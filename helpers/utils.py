import re
import os
import json
from bs4 import BeautifulSoup
import google.generativeai as genai
from langchain.prompts import PromptTemplate
# selenium req.
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# from langchain_community.vectorstores import FAISS
# from langchain_google_genai import GoogleGenerativeAIEmbeddings
# from langchain_community.document_loaders import RecursiveUrlLoader
# from langchain.text_splitter import RecursiveCharacterTextSplitter

from dotenv import load_dotenv
load_dotenv()

MAX_TRY = 5

# selenium configuration
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
service = Service()

# load gemini
genai.configure(api_key=os.environ['GOOGLE_API_KEY'])
gemini = genai.GenerativeModel("gemini-pro")

# Prompt for AI Suggestion
ai_suggestion_prompt_template = '''
Below is the content of a website that I have scraped. 
I am looking to introduce AI features to enhance the site's functionality and user experience or any Other modifictions. 
Please provide 10 detailed suggestions for modifications that incorporate AI into the site. 
Each suggestion should be a comprehensive description, 
explaining the idea clearly and how it integrates with the site's context.

Site Context is Below: 
{context} 

Output Format Should be JSON format like below : 

'suggestion_1' : '.....detailed suggestion 1' ,
'suggestion_2' : '.....detailed suggestion 2' ,
'suggestion_3' : '.....detailed suggestion 3' ,
'suggestion_4' : '.....detailed suggestion 4' ,
'suggestion_5' : '.....detailed suggestion 5' ,
             .
             .
             .
'suggestion_10' : '.....detailed suggestion 10' 

The JSON string should be valid and properly formatted for JSON parsing using json.loads(json_string).
Only provide the JSON string in the output, without any additional text or explanation.

'''

# Prompt for Contact Generation
contact_generation_propt_template = '''
i have given the site scrapped text/html to you 
so can u please provide all contact detail , email-address ,phone number linkdin profile links or any other 
contact detail , whatever you can able to find related to contact detail 

Below is the site content : 
{context} 

output should be in JSON format :

"
email_address : [email_addresss..] , 
phone_number : [phone_numbers...] ,
linkdin_profile_link : [linkdin_profile_links]
other_contact_detail : [other_contact_detail,instagrammer,twitter]
"

The JSON string should be valid and properly formatted for JSON parsing using json.loads(json_string).
Only provide the JSON string in the output, without any additional text or explanation.

'''

AI_SUGGESTION_PROMPT = PromptTemplate(
    template=ai_suggestion_prompt_template, input_variables=['context'])
CONTACT_GENERATION_PROMPT = PromptTemplate(
    template=contact_generation_propt_template, input_variables=['context',])


def bs4_extractor(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    return re.sub(r"\n\n+", "\n\n", soup.text).strip()


def selenium_text_loader(url):
    all_links = []
    text = ''
    driver = webdriver.Chrome(service=service, options=chrome_options)

    driver.get(url)
    links = driver.find_elements(By.TAG_NAME, "a")
    page_urls = list(set([link.get_attribute("href") for link in links]))
    all_links.extend(page_urls)
    page_urls = [url_ for url_ in page_urls if url in url_]

    for url in page_urls:
        driver.get(url)
        page_content = driver.page_source
        page_text = bs4_extractor(page_content)
        text += page_text
        links = driver.find_elements(By.TAG_NAME, "a")
        page_urls = list(set([link.get_attribute("href") for link in links]))
        all_links.extend(page_urls)

    return list(set(all_links)), text

# def text_loader(url: str)->str:
#     doc_loder = RecursiveUrlLoader(url=url, extractor=bs4_extractor)
#     docs = doc_loder.load()
#     text = ''.join([doc.page_content for doc in docs])
#     return text ,docs

# def chunk_creator(text: str) -> List[str]:
#     splitter = RecursiveCharacterTextSplitter(chunk_size = 400,
#                                             chunk_overlap = 200)
#     chunks = splitter.split_text(text)
#     return chunks

# def get_embeddings_and_store_vector_geminit(chunks) :
#     embeddings = GoogleGenerativeAIEmbeddings(model ='models/embedding-001',
#                                               google_api_key = os.environ['GOOGLE_API_KEY'])
#     vector_store= FAISS.from_texts(chunks ,embeddings)
#     vector_store.save_local('gemeni-embedding')


def get_ai_suggestion(docs, prompt):

    retry = 0
    while retry < MAX_TRY:
        try:
            # site_page_content = ''.join([chunk.page_content for chunk in chunks])
            llm_prompt = prompt.invoke(docs).text
            gemini_response = gemini.generate_content(llm_prompt).text
            response = gemini_response[gemini_response.find(
                '{'):gemini_response.rfind('}')+1]
            response = json.loads(response)
            return response
        except:

            retry += 1


def get_contact_detail(docs, prompt):
    retry = 0
    while retry < MAX_TRY:
        try:
            # whole_context = ''.join([chunk.page_content for chunk in chunks])
            llm_prompt = prompt.invoke(docs).text
            gemini_response = gemini.generate_content(llm_prompt).text
            response = gemini_response[gemini_response.find(
                '{'):gemini_response.rfind('}')+1]
            response = json.loads(response)
            return response
        except:
            retry += 1
