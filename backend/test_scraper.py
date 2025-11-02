from backend.scraper import ProductScraper
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

def test_scraping():
    scraper = ProductScraper()
    
    # Test URLs
    urls = [
        "https://www.amazon.com/dp/B08N5KWB9H",  # Amazon
        "https://www.ebay.com/itm/123456789",    # eBay
        "https://www.aliexpress.com/item/1234"   # AliExpress
    ]
    
    for url in urls:
        print(f"\nTesting URL: {url}")
        result = scraper.scrape_product(url)
        print(f"Result: {result}")

if __name__ == "__main__":
    test_scraping()