from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import pandas as pd
import json
from datetime import datetime
import time
import logging
import os
from typing import List, Dict
import random
import csv
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service
from config import EMAIL, PASSWORD, PROFILE_URL

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0"
]

class LinkedInScraper:
    def __init__(self):
        self.setup_logging()
        self.setup_driver()

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('linkedin_scraping.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def setup_driver(self):
        try:
            options = webdriver.ChromeOptions()
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_experimental_option('excludeSwitches', ['enable-automation'])
            options.add_experimental_option('useAutomationExtension', False)
            options.add_argument(f"user-agent={random.choice(user_agents)}")
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-infobars')
            options.add_argument('--disable-notifications')
            # options.add_argument('--headless')  # Uncomment this line if you want to run in headless mode
            
            self.driver = webdriver.Chrome(options=options)
            self.driver.set_window_size(1920, 1080)
            
            self.driver.execute_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            )
            
            self.logger.info("Successfully initialized Chrome WebDriver")
        except Exception as e:
            self.logger.error(f"Failed to initialize WebDriver: {str(e)}")
            raise

    def login(self, email: str, password: str) -> bool:

        try:
            # Navigate to LinkedIn login page
            self.driver.get('https://www.linkedin.com/login')
            time.sleep(3)  # Wait for page to load
            

            email_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            email_field.send_keys(email)
            
 
            password_field = self.driver.find_element(By.ID, "password")
            password_field.send_keys(password)
            

            login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_button.click()
            
            # Wait for login to complete
            time.sleep(5)
            
            # Check if login was successful by looking for feed URL
            if "feed" in self.driver.current_url:
                self.logger.info("Successfully logged in to LinkedIn")
                return True
            else:
                self.logger.error("Failed to log in to LinkedIn")
                return False
                
        except Exception as e:
            self.logger.error(f"Error during login: {str(e)}")
            return False

    def get_followed_companies(self, profile_url: str) -> List[Dict]:
        companies = []
        try:
            interests_url = f"{profile_url}details/interests/"
            self.driver.get(interests_url)
            time.sleep(random.uniform(10, 15))

            if not self.is_logged_in():
                self.logger.error("User is not logged in. Attempting to re-login.")
                if not self.login(EMAIL, PASSWORD):
                    raise Exception("Failed to re-login")

            self.logger.info(f"Current URL: {self.driver.current_url}")

            try:
                WebDriverWait(self.driver, 30).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "li.pvs-list__paged-list-item"))
                )
            except TimeoutException:
                self.logger.warning("Timeout waiting for company elements to load")

            self.scroll_to_load_all()

            company_elements = self.driver.find_elements(By.CSS_SELECTOR, "li.pvs-list__paged-list-item")
            
            self.logger.info(f"Found {len(company_elements)} company elements")

            for element in company_elements:
                try:
                    name = element.find_element(By.CSS_SELECTOR, "div.align-items-center.mr1.hoverable-link-text.t-bold").text.strip()
                    url = element.find_element(By.CSS_SELECTOR, "a.optional-action-target-wrapper").get_attribute("href")
                    followers_text = element.find_element(By.CSS_SELECTOR, "span.pvs-entity__caption-wrapper").text.strip()
                    followers = self.extract_follower_count(followers_text)
                    
                    if name and url:
                        companies.append({
                            'Company name': name,
                            'Number of followers': followers,
                            'Company profile LinkedIn URL': url
                        })
                
                except NoSuchElementException as e:
                    self.logger.warning(f"Error processing company element: {str(e)}")
                    continue
                
                time.sleep(0.5)
            
            self.logger.info(f"Successfully collected data for {len(companies)} companies")
            return companies
            
        except Exception as e:
            self.logger.error(f"Error getting followed companies: {str(e)}")
            return []

    def human_like_scroll(self):
        total_height = int(self.driver.execute_script("return document.body.scrollHeight"))
        for i in range(1, total_height, random.randint(100, 200)):
            self.driver.execute_script(f"window.scrollTo(0, {i});")
            time.sleep(random.uniform(0.1, 0.3))
        time.sleep(random.uniform(0.5, 1.5))

    def scroll_to_load_all(self):
        """Scroll the page to load all company elements."""
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        
        while True:
            self.human_like_scroll()
            
            # Calculate new scroll height and compare with last scroll height
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    def extract_follower_count(self, followers_text: str) -> int:

        try:
            # Remove non-numeric characters and convert abbreviations
            followers_text = followers_text.lower().replace(',', '')
            if 'k' in followers_text:
                followers = float(followers_text.replace('k', '')) * 1000
            elif 'm' in followers_text:
                followers = float(followers_text.replace('m', '')) * 1000000
            else:
                followers = float(''.join(filter(str.isdigit, followers_text)))
            return int(followers)
        except:
            return 0

    def save_data(self, companies: List[Dict], output_dir: str = "output"):

        try:
            # Create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)
            
            # Generate timestamp for filenames
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            base_filename = f'linkedin_followed_companies_{timestamp}'
            
            # Save to CSV
            csv_path = os.path.join(output_dir, f'{base_filename}.csv')
            df = pd.DataFrame(companies)
            df.to_csv(csv_path, index=False)
            self.logger.info(f"Data saved to CSV: {csv_path}")
            
            # Save to JSON
            json_path = os.path.join(output_dir, f'{base_filename}.json')
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(companies, f, indent=4)
            self.logger.info(f"Data saved to JSON: {json_path}")
            
        except Exception as e:
            self.logger.error(f"Error saving data: {str(e)}")
            raise

    def cleanup(self):
        """Clean up resources."""
        try:
            self.driver.quit()
            self.logger.info("Successfully closed WebDriver")
        except Exception as e:
            self.logger.error(f"Error closing WebDriver: {str(e)}")

    def is_logged_in(self):
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "global-nav"))
            )
            return True
        except:
            return False

def main():
    try:
        scraper = LinkedInScraper()
        if scraper.login(EMAIL, PASSWORD):
            companies = scraper.get_followed_companies(PROFILE_URL)
            if companies:
                scraper.save_data(companies)
            else:
                print("No companies found.")
        else:
            print("Failed to login to LinkedIn")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        logging.error(f"Script execution failed: {str(e)}")
    finally:
        if scraper:
            scraper.cleanup()

if __name__ == "__main__":
    main()
