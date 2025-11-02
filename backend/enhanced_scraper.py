import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent
from urllib.parse import urlparse
import time
import random
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedScraper:
    def __init__(self):
        self.session = requests.Session()
        self.ua = UserAgent()
        self.setup_session()
        
    def setup_session(self):
        """Initialize session with enhanced anti-bot protection"""
        self.session.headers.update({
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1'
        })
        logger.info("Enhanced scraper initialized with anti-bot protection")

    def get_selenium_driver(self):
        """Configure Selenium with enhanced anti-bot measures"""
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument(f'--user-agent={self.ua.random}')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Random window size
        sizes = [(1366, 768), (1920, 1080), (1536, 864)]
        width, height = random.choice(sizes)
        options.add_argument(f'--window-size={width},{height}')
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        # Hide automation
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")
        
        return driver

    def test_scraper(self):
        """Test the scraper implementation"""
        urls = [
            "https://www.amazon.com/dp/B08N5KWB9H",
            "https://www.ebay.com/itm/123456789"
        ]
        
        for url in urls:
            print(f"\nTesting URL: {url}")
            try:
                result = self.scrape_with_anti_bot(url)
                if result:
                    print("Success!")
                else:
                    print("Failed - trying Selenium...")
                    result = self.scrape_with_selenium(url)
                    if result:
                        print("Selenium succeeded!")
                    else:
                        print("Both methods failed")
            except Exception as e:
                print(f"Error: {str(e)}")

    def scrape_with_anti_bot(self, url):
        """Scrape with enhanced anti-bot protection and retries"""
        logger.info(f"SCRAPING WITH ANTI-BOT PROTECTION: {url}")
        
        delay = random.uniform(2, 4)
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                # Add random delay
                time.sleep(delay * (1 + random.uniform(-0.1, 0.1)))
                
                # Update headers
                self.session.headers.update({
                    'User-Agent': self.ua.random,
                    'Referer': 'https://www.google.com/',
                })
                
                response = self.session.get(url, timeout=30)
                logger.info(f"Response Status: {response.status_code}")
                
                if response.status_code == 200:
                    content = response.text.lower()
                    if any(marker in content for marker in ['robot', 'captcha', 'verify']):
                        raise Exception("Anti-bot measures detected")
                    
                    logger.info("SUCCESS: Requests scraping worked")
                    return response
                
                delay *= 1.5
                
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt == max_retries - 1:
                    logger.warning("All attempts failed, switching to Selenium")
                    break
                delay *= 2
        
        return None

    def scrape_with_selenium(self, url):
        """Scrape using Selenium with anti-bot protection"""
        logger.info(f"SELENIUM SCRAPING: {url}")
        driver = None
        try:
            driver = self.get_selenium_driver()
            driver.get(url)
            time.sleep(random.uniform(3, 5))
            
            if any(marker in driver.page_source.lower() for marker in ['robot', 'captcha']):
                logger.error("ANTI-BOT DETECTED in Selenium")
                return None
                
            return driver.page_source
            
        except Exception as e:
            logger.error(f"Selenium error: {str(e)}")
            return None
            
        finally:
            if driver:
                driver.quit()

if __name__ == "__main__":
    # Run a quick test
    scraper = EnhancedScraper()
    scraper.test_scraper()