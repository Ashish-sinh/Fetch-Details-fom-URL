import streamlit as st
from helpers.utils import web_scrapper, bs4_extractor, get_ai_suggestion

st.title('Fetch Details from URL 🔗')
URL = st.text_input("Please Enter URL")
st.session_state['URL'] = URL

if st.button("Get Details"):
    with st.spinner("Scrapping Data From Given URL..."):
        url = st.session_state['URL']
        contact_details, web_html_text = web_scrapper(str(url))
        st.session_state['contact_details'] = contact_details
        st.session_state['web_page_content'] = bs4_extractor(web_html_text)[:30000] 
        st.success('Scrapped Data Sucessfully ✅✅..')
    st.divider() 

    with st.spinner('Fetching Contact-Details..'):
        st.header('Below is available contact-details')
        cd = st.session_state['contact_details']
        for key in cd : 
            if len(cd[key]) > 0:
                st.header(f'{key} :')
                for link in cd[key] : 
                        st.write(link)
        st.success('Contact-Detail fetched Sucessfully ✅✅..') 
    st.divider() 

    with st.spinner('Generating AI Response...'):
    
        page_content = str(st.session_state['web_page_content']) 
        response = get_ai_suggestion(page_content)

        st.header('Below is AI-Suggesion for your Given Web-Site')
        for idx, suggestion in enumerate(response) :
            st.header(f'• Suggestion {idx+1}')
            for k in response[suggestion]: 
                st.write(f':red[{k}]',':',response[suggestion][k])

        st.divider() 
        st.success('Done')