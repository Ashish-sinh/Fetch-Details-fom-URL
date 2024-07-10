import re
import os
import json
from bs4 import BeautifulSoup
import google.generativeai as genai
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from langchain_community.document_loaders import RecursiveUrlLoader

from dotenv import load_dotenv
load_dotenv()

MAX_TRY = 5
CUSTOM_HEADER = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    'accept-language': 'en-GB,en;q=0.9',
}

# selenium configuration
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--enable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--disable-images')
service = Service()

# load gemini
genai.configure(api_key=os.environ['GOOGLE_API_KEY'])
gemini = genai.GenerativeModel("gemini-pro")

# compiler for phone and email :
phone_pattern = re.compile(r'\(?\b[5-9]{3}[-.)\s]?[0-9]{3}[-.\s]?[0-9]{4}\b')
email_pattern = re.compile(
    r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')


def phone_email_extractor(text: str):
    try:
        emails = list(set(email_pattern.findall(text)))
        phones = list(set(phone_pattern.findall(text)))
        return emails, phones
    except:
        [], []


def whole_contact_detail_byhtml(text: str):

    soup = BeautifulSoup(text, 'lxml')

    output = {'linkedin': [],
              'facebook': [],
              'twitter': [],
              'instagram': [],
              'youtube': [],
              'email': [],
              'phone': []}

    email, phone = phone_email_extractor(text)
    output['email'].extend(email)
    output['phone'].extend(phone)

    try:
        for link in soup.find_all('a', href=True):
            href = link['href']
            if 'linkedin.com' in href.lower() and href not in output['linkedin']:
                output['linkedin'].append(href)
            elif 'facebook.com' in href.lower() and href not in output['facebook']:
                output['facebook'].append(href)
            elif 'twitter.com' in href.lower() and href not in output['twitter']:
                output['twitter'].append(href)
            elif '/x.com' in href.lower() and href not in output['twitter']:
                output['twitter'].append(href)
            elif 'instagram.com' in href.lower() and href not in output['instagram']:
                output['instagram'].append(href)
            elif 'youtube.com' in href.lower() and href not in output['youtube']:
                output['youtube'].append(href)
        return output
    except:

        return output


def bs4_extractor(html: str) -> str:
    html_1, html_2 = html.split('**||SPLIT||**')
    soup_1, soup_2 = BeautifulSoup(
        html_1, "lxml"), BeautifulSoup(html_2, "lxml")
    return re.sub(r"\n\n+", "\n\n", soup_1.text).strip() + re.sub(r"\n\n+", "\n\n", soup_2.text).strip()


def selenium_extractor(url):
    html_text = ''
    try:
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.get(url)
        html_text += driver.page_source
        driver.quit()
        return html_text
    except:
        return html_text


def recursive_url_extractor(url, headers=CUSTOM_HEADER):
    html_text = ''
    try:
        loader = RecursiveUrlLoader(url, headers=headers)
        for idx, text in enumerate(loader.lazy_load()):
            if idx < 21:
                html_text += text.page_content
            else:
                break
        return html_text
    except:
        return html_text


def web_scrapper(url):

    selenium_html = selenium_extractor(url)
    urlloader_html = recursive_url_extractor(url)

    selenium_contact_detail = whole_contact_detail_byhtml(selenium_html)
    urlloader_contact_detail = whole_contact_detail_byhtml(urlloader_html)

    contact_detail = selenium_contact_detail

    for key in selenium_contact_detail:
        if key in urlloader_contact_detail:
            contact_detail[key] = list(
                set(selenium_contact_detail[key] + urlloader_contact_detail[key]))

    whole_html_text = urlloader_html + '**||SPLIT||**' + selenium_html
    return contact_detail, whole_html_text


def get_ai_suggestion(docs: str):

    ai_suggestion_prompt_template = f'''
    Below is the content of a website that I have scraped. 
    I aim to introduce AI features to enhance the site's functionality and user experience, 
    along with other possible modifications.

    • Please provide 10 detailed suggestions for modifications that incorporate AI into the site. 
    Each suggestion should include:

    Comprehensive Description of the AI Feature: Provide a detailed explanation of the AI feature, 
    including how it works and what it does.
    
    Integration with Site's Context: Explain how this feature fits into the existing website, considering its content, 
    purpose, and user base.
    
    Benefits and Improvements: Describe the potential advantages and improvements this feature will 
    bring to the user experience and overall site functionality.
    
    Technical Requirements and Considerations: Outline any technical aspects, requirements, or 
    considerations necessary for implementing the feature.
    
    • Ensure that each suggestion is closely related to the overall context and purpose of the website. 
      Focus on enhancing the current functionalities and user experience based on the site's content and nature.

    • Site Context is Below: 
        {docs} 

    • Output Format Should be JSON format like below : 

    Provide the suggestions in valid JSON format as shown below, 
    ensuring that the JSON string is properly formatted for parsing using json.loads(json_string). 
    Only provide the JSON string in the output, without any additional text or explanation'''+'''

    {
        "suggestion_1": {
            "feature_description": ".....detailed description of the AI feature",
            "integration_with_site": ".....explanation of how it integrates with the site's context",
            "benefits_and_improvements": ".....benefits and improvements to the user experience",
            "technical_requirements": ".....technical requirements and considerations"
        },
        "suggestion_2": {
            "feature_description": ".....detailed description of the AI feature",
            "integration_with_site": ".....explanation of how it integrates with the site's context",
            "benefits_and_improvements": ".....benefits and improvements to the user experience",
            "technical_requirements": ".....technical requirements and considerations"
        },
        "suggestion_3": {
            "feature_description": ".....detailed description of the AI feature",
            "integration_with_site": ".....explanation of how it integrates with the site's context",
            "benefits_and_improvements": ".....benefits and improvements to the user experience",
            "technical_requirements": ".....technical requirements and considerations"
        },
                                    .
                                    .
                                    .
        
        "suggestion_10": {
            "feature_description": ".....detailed description of the AI feature",
            "integration_with_site": ".....explanation of how it integrates with the site's context",
            "benefits_and_improvements": ".....benefits and improvements to the user experience",
            "technical_requirements": ".....technical requirements and considerations"
        }
    }

    The JSON string should be valid and properly formatted for JSON parsing using json.loads(json_string).
    Only provide the JSON string in the output, without any additional text or explanation.
    '''

    retry = 0
    while retry < MAX_TRY:
        try:
            llm_prompt = ai_suggestion_prompt_template
            gemini_response = gemini.generate_content(llm_prompt).text
            response = gemini_response[gemini_response.find(
                '{'):gemini_response.rfind('}')+1]
            response = json.loads(response)
            return response
        except:
            retry += 1
