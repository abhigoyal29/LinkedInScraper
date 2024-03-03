import streamlit as st
import requests
from bs4 import BeautifulSoup
import scraper

def fetch_page_title(url):
    """Fetch and return the title of a webpage."""
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            return soup.title.string
    except Exception as e:
        return str(e)

# Streamlit app layout
st.title('LinkedIn Comment Scraper')

# Text input for the URL
url = st.text_input('Enter the URL of a LinkedIn Post:', '')

# Button to perform action
if st.button('Scrape LinkedIn Post'):
    if url:
        title = scraper.scrape_comments(url)
        st.success("Scraped comments successfully!")
    else:
        st.error('Please enter a URL.')

