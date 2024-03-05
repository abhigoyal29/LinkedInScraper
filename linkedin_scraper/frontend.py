import streamlit as st
import requests
from bs4 import BeautifulSoup
import scraper
import time

# Streamlit app layout
st.title('LinkedIn Comment Scraper')

def callback():
    st.session_state.submit = True

def login():
    st.sidebar.title("Login")

    # Get username and password from user input
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    
    if st.sidebar.button('Submit', on_click=callback) or st.session_state.submit:
        with open("credentials.txt", "w") as f:
            f.write(username + "\n")
            f.write(password + "\n")
        st.success("Thank you! You can put them in again if your account gets blocked")
        return True

def enterURL():
    st.title("URL")
    st.subheader("Enter the URLs of LinkedIn Posts:")
    NUM_LINKEDIN_POSTS = 5
    urls = []
    # Text input for the URLs
    for i in range(NUM_LINKEDIN_POSTS):
        urls.append(st.text_input(f'Url {i} ', '', key = i, label_visibility='hidden'))
    
    # Get rid of the empty URLs
    while("" in urls):
        urls.remove("")

    # Button to perform action
    if st.button('Scrape LinkedIn Post'):
        if urls:
            progress_bar = st.progress(0, "Fetching from each URL...")
            percent_complete = 0
            for url in urls:
                scraper.scrape_comments(url)
                percent_complete += int(100/len(urls))
                progress_bar.progress(percent_complete, "Fetching from each URL...")
        else:
            st.error('Please enter URLs')

        time.sleep(1.2)
        progress_bar.empty()
        st.success("Scraped comments successfully! Feel free to put in new URLs")
        st.text("")
        st.text("")
        with open('emails.csv') as f:
            st.download_button('Download CSV', f, file_name = "linkedin_post_emails.csv")
def main():
    if "submit" not in st.session_state:
        st.session_state.submit = False
    if login():
        time.sleep(1)
        enterURL()

if __name__ == "__main__":
    main()
