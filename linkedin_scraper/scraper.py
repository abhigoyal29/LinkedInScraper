from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
# from selenium import webdriver
# from selenium.common.exceptions import TimeoutException
# from selenium.webdriver.common.by import By
# from selenium.webdriver.firefox.options import Options
# from selenium.webdriver.firefox.service import Service
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.support.ui import WebDriverWait
# from webdriver_manager.firefox import GeckoDriverManager
# from selenium.webdriver.firefox.firefox_binary import FirefoxBinary

from bs4 import BeautifulSoup as bs
import re
import time
import csv
import streamlit as st


def scrape_comments(url):
    @st.experimental_singleton
    def get_driver():
        return webdriver.Chrome(service=Service(ChromeDriverManager(driver_version="2.26").install()), options=chrome_options)

    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Enable headless mode
    driver = get_driver()
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
    # def remove_thank(string):
    #     return string.replace("Thank", "").replace("Thanks", "").replace("thanks", "").replace("thank", "").replace("interested", "").replace("Interested","")

    if url:
        driver.get(url)
        
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'comments-comments-list'))
        )

        def load_more(target: str, target_class: str, driver: webdriver.Chrome):
            webdriver_wait = WebDriverWait(driver, 10)
            action = ActionChains(driver)

            try:
                load_more_button = webdriver_wait.until(
                    EC.element_to_be_clickable((By.CLASS_NAME, target_class))
                )
            except:
                print(f"All {target} are displaying already!")
                return

            print("[", end="", flush=True)

            while True:
                print("#", end="", flush=True)
                action.move_to_element(load_more_button).click().perform()
                time.sleep(1)
                try:
                    load_more_button = webdriver_wait.until(
                        EC.element_to_be_clickable((By.CLASS_NAME, target_class))
                    )
                except:
                    print("]")
                    print(f"All {target} have been displayed!")
                    break

        
        # load_more("comments","comments-comments-list__load-more-comments-button", driver)

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
