#!/usr/bin/env python3
"""
YC AI Startup Tracker
This script scrapes LinkedIn to find AI startups backed by Y Combinator
and updates a markdown file with the findings.
"""

import os
import json
import datetime
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import logging
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)

class LinkedInScraper:
    def __init__(self):
        self.data_file = "data/startups.json"
        self.results_file = "README.md"
        self.ensure_data_dir()
        
    def ensure_data_dir(self):
        """Ensure the data directory exists"""
        os.makedirs("data", exist_ok=True)
        
    def setup_driver(self):
        """Set up the Selenium WebDriver with Chrome in headless mode"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36")
        
        driver = webdriver.Chrome(options=chrome_options)
        return driver
    
    def login_to_linkedin(self, driver, username, password):
        """Login to LinkedIn using provided credentials"""
        try:
            logger.info("Logging into LinkedIn...")
            driver.get("https://www.linkedin.com/login")
            
            # Wait for the login form to appear
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            
            # Enter username and password
            driver.find_element(By.ID, "username").send_keys(username)
            driver.find_element(By.ID, "password").send_keys(password)
            
            # Click login button
            driver.find_element(By.XPATH, "//button[@type='submit']").click()
            
            # Wait for login to complete
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "global-nav"))
            )
            
            logger.info("Successfully logged into LinkedIn")
            return True
            
        except Exception as e:
            logger.error(f"Failed to login to LinkedIn: {e}")
            return False
    
    def search_yc_ai_startups(self, driver):
        """Search for Y Combinator AI startups on LinkedIn"""
        startups = []
        
        try:
            # Navigate to LinkedIn search
            search_url = "https://www.linkedin.com/search/results/companies/?keywords=Y%20Combinator%20AI%20startup"
            logger.info(f"Searching for YC AI startups using URL: {search_url}")
            driver.get(search_url)
            
            # Wait for search results to load
            time.sleep(5)
            
            # Scroll to load more results
            for _ in range(3):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
            
            # Extract company results
            company_cards = driver.find_elements(By.XPATH, "//div[contains(@class, 'entity-result')]")
            
            for card in company_cards:
                try:
                    company_name = card.find_element(By.XPATH, ".//span[@dir='ltr']").text.strip()
                    company_description = card.find_element(By.XPATH, ".//p[contains(@class, 'entity-result__summary')]").text.strip()
                    
                    # Only include if description mentions AI and Y Combinator
                    if ("AI" in company_description or "artificial intelligence" in company_description.lower()) and \
                       ("Y Combinator" in company_description or "YC" in company_description):
                        
                        try:
                            company_url = card.find_element(By.XPATH, ".//a[contains(@class, 'app-aware-link')]").get_attribute("href")
                        except:
                            company_url = ""
                            
                        startup = {
                            "name": company_name,
                            "description": company_description,
                            "url": company_url,
                            "found_date": datetime.datetime.now().strftime("%Y-%m-%d")
                        }
                        
                        startups.append(startup)
                        logger.info(f"Found YC AI startup: {company_name}")
                        
                except Exception as e:
                    logger.warning(f"Failed to parse a company card: {e}")
                    continue
                    
            logger.info(f"Found {len(startups)} YC AI startups")
            return startups
            
        except Exception as e:
            logger.error(f"Error during search: {e}")
            return startups
    
    def save_startups_data(self, startups):
        """Save or update the startups data in JSON file"""
        existing_startups = []
        
        # Read existing data if file exists
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    existing_startups = json.load(f)
            except json.JSONDecodeError:
                existing_startups = []
        
        # Merge new startups with existing ones (avoid duplicates by name)
        existing_names = [s["name"] for s in existing_startups]
        for startup in startups:
            if startup["name"] not in existing_names:
                existing_startups.append(startup)
                existing_names.append(startup["name"])
        
        # Save updated data
        with open(self.data_file, 'w') as f:
            json.dump(existing_startups, f, indent=2)
            
        logger.info(f"Saved {len(existing_startups)} startups to {self.data_file}")
        
        return existing_startups
    
    def update_readme(self, startups):
        """Update the README.md with the latest startups data"""
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        
        # Sort startups by found date (newest first)
        startups.sort(key=lambda x: x.get("found_date", ""), reverse=True)
        
        readme_content = f"""# Y Combinator AI Startup Tracker

Automatically updated list of AI startups backed by Y Combinator found on LinkedIn.

Last updated: {today}

## Latest AI Startups

| Name | Description | Found Date | LinkedIn |
|------|-------------|------------|----------|
"""
        
        for startup in startups:
            name = startup["name"]
            description = startup["description"]
            found_date = startup.get("found_date", "N/A")
            url = startup.get("url", "")
            
            # Create shortened description (first 100 chars)
            short_desc = description[:100] + "..." if len(description) > 100 else description
            
            # Create LinkedIn link
            link = f"[Profile]({url})" if url else "N/A"
            
            readme_content += f"| {name} | {short_desc} | {found_date} | {link} |\n"
        
        readme_content += """
## How It Works

This repository uses GitHub Actions to automatically:
1. Search LinkedIn for AI startups backed by Y Combinator
2. Update this README with the latest findings
3. Run this process daily

## Note

This tool is for educational purposes only. Please respect LinkedIn's terms of service and rate limits.
"""
        
        with open(self.results_file, 'w') as f:
            f.write(readme_content)
            
        logger.info(f"Updated {self.results_file} with {len(startups)} startups")
        
    def run(self, linkedin_username=None, linkedin_password=None):
        """Main execution function"""
        logger.info("Starting YC AI startup tracker")
        
        # For testing without LinkedIn credentials, we'll load mock data
        if not linkedin_username or not linkedin_password:
            logger.warning("No LinkedIn credentials provided. Using mock data for testing.")
            mock_startups = [
                {
                    "name": "AI Builder",
                    "description": "Y Combinator W2024 batch. We're building AI-powered tools for software development.",
                    "url": "https://www.linkedin.com/company/aibuilder",
                    "found_date": datetime.datetime.now().strftime("%Y-%m-%d")
                },
                {
                    "name": "DataSense AI",
                    "description": "YC S2023 batch. Enterprise AI solutions for data analytics.",
                    "url": "https://www.linkedin.com/company/datasense-ai",
                    "found_date": datetime.datetime.now().strftime("%Y-%m-%d")
                }
            ]
            
            all_startups = self.save_startups_data(mock_startups)
            self.update_readme(all_startups)
            return
        
        try:
            driver = self.setup_driver()
            
            login_success = self.login_to_linkedin(driver, linkedin_username, linkedin_password)
            if not login_success:
                logger.error("Failed to login. Exiting.")
                driver.quit()
                return
            
            startups = self.search_yc_ai_startups(driver)
            driver.quit()
            
            all_startups = self.save_startups_data(startups)
            self.update_readme(all_startups)
            
            logger.info("YC AI startup tracking completed successfully")
            
        except Exception as e:
            logger.error(f"Error during execution: {e}")
            if 'driver' in locals():
                driver.quit()

if __name__ == "__main__":
    # Get LinkedIn credentials from environment variables
    linkedin_username = os.environ.get("LINKEDIN_USERNAME")
    linkedin_password = os.environ.get("LINKEDIN_PASSWORD")
    
    scraper = LinkedInScraper()
    scraper.run(linkedin_username, linkedin_password)
