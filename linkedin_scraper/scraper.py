from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup as bs
import re
import time
import csv


def scrape_comments(linkedin_post_url):
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Enable headless mode
    driver = webdriver.Chrome(options=chrome_options)
    driver.get("https://www.linkedin.com/login?fromSignIn=true&trk=guest_homepage-basic_nav-header-signin")

    #Enter login info:
    with open('credentials.txt', 'r') as f:
        elementID = driver.find_element(By.ID, 'username')
        elementID.send_keys(f.readline().strip())

        elementID = driver.find_element(By.ID, 'password')
        elementID.send_keys(f.readline().strip())

        elementID.submit()

    driver.get(linkedin_post_url)
    
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'comments-comments-list'))
    )

    def scroll_down():
        """A method for scrolling the page."""

        # Get scroll height.
        last_height = driver.execute_script("return document.body.scrollHeight")

        while True:

            # Scroll down to the bottom.
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Wait to load the page.
            time.sleep(2)

            # Calculate new scroll height and compare with last scroll height.
            new_height = driver.execute_script("return document.body.scrollHeight")

            if new_height == last_height:

                break

            last_height = new_height

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

    
    load_more("comments","comments-comments-list__load-more-comments-button", driver)

    # load all html source into a file
    bs_obj = bs(driver.page_source, "html.parser")
    comments = bs_obj.find_all("span", {"class": "comments-comment-item__main-content"})
    comments = [comment.get_text(strip=True) for comment in comments]

    emails = []
    for comment in comments:
        email_match = re.findall(r"[\w\.-]+@[\w\.-]+\.\w+", comment)
        if email_match:
            emails.extend(email_match)
    
    def remove_thank(string):
        return string.replace("Thank", "").replace("Thanks", "").replace("thanks", "").replace("thank", "").replace("interested", "").replace("Interested","")

    # Specify the filename for the CSV file
    csv_file = 'emails.csv'

    # Open the CSV file in write mode
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)  # Create a CSV writer object
        for email in emails:
            writer.writerow([remove_thank(email)])

if __name__ == "__main__":
    # linkedin_post_url = 'https://www.linkedin.com/posts/myan_jobsearch-hiring-activity-7167941891936780289-cjMW/?utm_source=share&utm_medium=member_desktop'
    # comments = scrape_comments(linkedin_post_url)
    pass
