from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService

from bs4 import BeautifulSoup as bs
import time
import csv
import streamlit as st
import os
import shutil
import math


@st.cache_resource(show_spinner=False)
def get_webdriver_options() -> Options:
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-features=NetworkService")
    options.add_argument("--window-size=1920x1080")
    options.add_argument("--disable-features=VizDisplayCompositor")
    options.add_argument('--ignore-certificate-errors')
    return options

@st.cache_resource(show_spinner=False)
def get_chromedriver_path() -> str:
    return shutil.which('chromedriver')

@st.cache_resource(show_spinner=False)
def get_logpath() -> str:
    return os.path.join(os.getcwd(), 'selenium.log')

def get_webdriver_service(logpath) -> ChromeService:
    service = ChromeService(
        executable_path=get_chromedriver_path(),
        log_output = logpath
    )
    return service

def scrape_comments(url):
    driver = webdriver.Chrome(options=get_webdriver_options(),
                        service=get_webdriver_service(get_logpath()))
    driver.get("https://www.linkedin.com/login?fromSignIn=true&trk=guest_homepage-basic_nav-header-signin")

    #Enter login info:
    with open('credentials.txt', 'r') as f:
        elementID = driver.find_element(By.ID, 'username')
        elementID.send_keys(f.readline().strip())

        elementID = driver.find_element(By.ID, 'password')
        elementID.send_keys(f.readline().strip())

        elementID.submit()
    
    # Specify the filename for the CSV file
    csv_file = 'emails.csv'

    if url:
        driver.get(url)
        
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'comments-comments-list'))
        )

        def load_more(target: str, target_class: str, driver: webdriver.Chrome):
            webdriver_wait = WebDriverWait(driver, 10)
            action = ActionChains(driver)
            progress_bar = st.progress(0, "Loading comments from current URL...")
            percent_complete = 0

            try:
                load_more_button = webdriver_wait.until(
                    EC.element_to_be_clickable((By.CLASS_NAME, target_class))
                )
            except:
                print(f"All {target} are displaying already!")
                return

            print("[", end="", flush=True)

            # Estimate total number of loads or loading time
            total_loads = 320  # You can estimate this value based on your data

            while True:
                print("#", end="", flush=True)
                percent_increment = 100 / total_loads
                percent_complete += int(math.ceil(percent_increment))
                if percent_complete > 100:
                    percent_complete = 99

                progress_bar.progress(percent_complete, "Loading comments from current URL...")

                action.move_to_element(load_more_button).click().perform()
                time.sleep(1)  # Adjust sleep time as needed

                try:
                    load_more_button = webdriver_wait.until(
                        EC.element_to_be_clickable((By.CLASS_NAME, target_class))
                    )
                except:
                    print("]")
                    percent_complete = 100
                    time.sleep(1.2)
                    progress_bar.empty()
                    print(f"All {target} have been displayed!")
                    break
    
        load_more("comments","comments-comments-list__load-more-comments-button", driver)

        # load all html source into a file
        bs_obj = bs(driver.page_source, "html.parser")
        comments = bs_obj.find_all("span", {"class": "comments-comment-item__main-content"})
        # comments = [comment.get_text(strip=True) for comment in comments]

        emails = []
        for comment in comments:
            # Find all 'a' tags within the comment span
            email_links = comment.find_all("a", href=True)
        
            for email_link in email_links:
                # Filter email links
                if email_link['href'].startswith('mailto:'):
                    email_address = email_link['href'][7:]  # Remove 'mailto:' prefix
                    emails.append(email_address)
        
        # Open the CSV file in write mode
        with open(csv_file, mode='a', newline='') as file:
            writer = csv.writer(file)  # Create a CSV writer object
            for email in emails:
                writer.writerow([email])

if __name__ == "__main__":
    # linkedin_post_url = 'https://www.linkedin.com/posts/myan_jobsearch-hiring-activity-7167941891936780289-cjMW/?utm_source=share&utm_medium=member_desktop'
    # comments = scrape_comments(linkedin_post_url)
    pass
