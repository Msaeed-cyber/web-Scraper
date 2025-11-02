from backend.scraper import ProductScraper
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO)

def test_scraping():
    scraper = ProductScraper()
    
    # Test URLs for different platforms
    test_urls = [
        'https://www.amazon.com/Amazon-Essentials-Standard-T-Shirt-Black/dp/B06XLLJ6Y2/',
        'https://www.ebay.com/itm/403726040284',
        'https://www.aliexpress.com/item/1005001634193080.html'
    ]
    
    for url in test_urls:
        print(f"\nTesting URL: {url}")
        result = scraper.scrape_product(url)
        print(f"Result: {result}")
        time.sleep(5)  # Wait between tests

if __name__ == '__main__':
    test_scraping()

