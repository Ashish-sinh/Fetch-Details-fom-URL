import streamlit as st
from helpers.utils import AI_SUGGESTION_PROMPT, CONTACT_GENERATION_PROMPT, get_ai_suggestion, selenium_text_loader, get_contact_detail

st.title('Fetch Details from URL 🔗')
URL = st.text_input("Please Enter URL")
st.session_state['URL'] = URL

if st.button("Scrape Data"):
    with st.spinner("Scrapping Data From Given URL..."):
        url = st.session_state['URL']
        url_lists, url_pages_content = selenium_text_loader(str(url))
        st.session_state['url_lists'] = url_lists
        st.session_state['url_pages_content'] = url_pages_content
        st.success('Scrapped Data Sucessfully ✅✅..')

st.write('')
col_1, col_2 = st.columns(2)
if col_1.button('Generate Suggestion'):

    with st.spinner("Generating..."):

        url_pages_content = st.session_state['url_pages_content']
        url_pages_content = url_pages_content[:40000]
        response = get_ai_suggestion(url_pages_content, AI_SUGGESTION_PROMPT)

        keys = list(response.keys())

        col_1.header('Below is AI-Suggesion for your Given Site')
        for idx, key in enumerate(keys):
            col_1.write(f':red[{idx+1}]. {response[key]}')

        col_1.success('Done')

if col_2.button('Fetch Contact Detail'):

    with st.spinner('Fetching Details...'):
        docs = st.session_state['url_lists']
        response = get_contact_detail(docs, CONTACT_GENERATION_PROMPT)
        keys = list(response.keys())
        col_2.header('Contact Detail')
        for idx, key in enumerate(keys):
            col_2.write(f':red[{idx+1}]. {response[key]}')

        col_2.success('Done')
