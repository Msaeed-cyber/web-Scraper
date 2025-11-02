#!/usr/bin/env python3
"""
Comprehensive debugging script for the web scraper
This will help identify why the scraper is returning fallback data
"""

import requests
from bs4 import BeautifulSoup
import logging
from urllib.parse import urlparse
import time
import random
from fake_useragent import UserAgent

# Setup detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper_debug.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DebugScraper:
    def __init__(self):
        self.session = requests.Session()
        self.ua = UserAgent()
        
        # Enhanced headers to avoid detection
        self.session.headers.update({
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        })
        
        logger.info("Debug scraper initialized with enhanced headers")
    
    def debug_request(self, url):
        """Debug the actual HTTP request and response"""
        logger.info(f"🔍 DEBUGGING REQUEST: {url}")
        
        try:
            # Add random delay to avoid rate limiting
            time.sleep(random.uniform(1, 3))
            
            logger.info(f"📡 Making request to: {url}")
            response = self.session.get(url, timeout=30)
            
            logger.info(f"📊 Response Status: {response.status_code}")
            logger.info(f"📏 Response Length: {len(response.content)} bytes")
            logger.info(f"🌐 Response Headers: {dict(response.headers)}")
            
            # Check if we got blocked
            if response.status_code == 403:
                logger.error("❌ BLOCKED: Got 403 Forbidden - likely anti-bot protection")
                return None, "BLOCKED"
            elif response.status_code == 429:
                logger.error("❌ RATE LIMITED: Got 429 Too Many Requests")
                return None, "RATE_LIMITED"
            elif response.status_code != 200:
                logger.error(f"❌ HTTP ERROR: Status {response.status_code}")
                return None, "HTTP_ERROR"
            
            # Check for anti-bot indicators
            content = response.text.lower()
            if any(indicator in content for indicator in [
                'captcha', 'robot', 'bot detection', 'access denied',
                'blocked', 'suspicious activity', 'verify you are human'
            ]):
                logger.error("❌ ANTI-BOT DETECTED: Page contains bot detection content")
                return None, "ANTI_BOT"
            
            logger.info("✅ Request successful, parsing content...")
            return response, "SUCCESS"
            
        except requests.exceptions.Timeout:
            logger.error("❌ TIMEOUT: Request timed out")
            return None, "TIMEOUT"
        except requests.exceptions.ConnectionError:
            logger.error("❌ CONNECTION ERROR: Failed to connect")
            return None, "CONNECTION_ERROR"
        except Exception as e:
            logger.error(f"❌ UNEXPECTED ERROR: {e}")
            return None, "UNEXPECTED_ERROR"
    
    def debug_amazon_scraping(self, url):
        """Debug Amazon-specific scraping"""
        logger.info("🛒 DEBUGGING AMAZON SCRAPING")
        
        response, status = self.debug_request(url)
        if not response:
            return None
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Debug title extraction
        logger.info("🔍 DEBUGGING TITLE EXTRACTION")
        title_selectors = [
            'span#productTitle',
            '.a-size-large.product-title-word-break',
            'h1.a-size-large',
            'h1'
        ]
        
        for i, selector in enumerate(title_selectors):
            elements = soup.select(selector)
            logger.info(f"  Selector {i+1} '{selector}': Found {len(elements)} elements")
            if elements:
                for j, element in enumerate(elements[:3]):  # Show first 3
                    text = element.get_text(strip=True)
                    logger.info(f"    Element {j+1}: '{text[:100]}...'")
        
        # Debug price extraction
        logger.info("💰 DEBUGGING PRICE EXTRACTION")
        price_selectors = [
            '.a-price-whole',
            '.a-offscreen',
            '#priceblock_dealprice',
            '#priceblock_ourprice',
            '.a-price-range',
            '.a-price .a-offscreen',
            '.a-price-symbol',
            '.a-price'
        ]
        
        for i, selector in enumerate(price_selectors):
            elements = soup.select(selector)
            logger.info(f"  Price Selector {i+1} '{selector}': Found {len(elements)} elements")
            if elements:
                for j, element in enumerate(elements[:3]):
                    text = element.get_text(strip=True)
                    logger.info(f"    Price Element {j+1}: '{text}'")
        
        # Debug rating extraction
        logger.info("⭐ DEBUGGING RATING EXTRACTION")
        rating_selectors = [
            '.a-icon-alt',
            '#acrPopover',
            '.a-size-medium.a-color-base',
            '.a-icon-star',
            '.a-star-mini'
        ]
        
        for i, selector in enumerate(rating_selectors):
            elements = soup.select(selector)
            logger.info(f"  Rating Selector {i+1} '{selector}': Found {len(elements)} elements")
            if elements:
                for j, element in enumerate(elements[:3]):
                    text = element.get_text(strip=True)
                    logger.info(f"    Rating Element {j+1}: '{text}'")
        
        # Debug review extraction
        logger.info("📝 DEBUGGING REVIEW EXTRACTION")
        review_selectors = [
            '#acrCustomerReviewText',
            '.a-size-base',
            '.a-link-normal',
            '[data-hook="review-star-rating"]',
            '.a-icon-alt'
        ]
        
        for i, selector in enumerate(review_selectors):
            elements = soup.select(selector)
            logger.info(f"  Review Selector {i+1} '{selector}': Found {len(elements)} elements")
            if elements:
                for j, element in enumerate(elements[:3]):
                    text = element.get_text(strip=True)
                    logger.info(f"    Review Element {j+1}: '{text}'")
        
        return soup
    
    def debug_daraz_scraping(self, url):
        """Debug Daraz-specific scraping"""
        logger.info("🛒 DEBUGGING DARAZ SCRAPING")
        
        response, status = self.debug_request(url)
        if not response:
            return None
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Debug title extraction
        logger.info("🔍 DEBUGGING DARAZ TITLE EXTRACTION")
        title_selectors = [
            'h1.pdp-product-name',
            '.pdp-product-name',
            'h1',
            '.product-title',
            '.pdp-product-title'
        ]
        
        for i, selector in enumerate(title_selectors):
            elements = soup.select(selector)
            logger.info(f"  Daraz Title Selector {i+1} '{selector}': Found {len(elements)} elements")
            if elements:
                for j, element in enumerate(elements[:3]):
                    text = element.get_text(strip=True)
                    logger.info(f"    Daraz Title Element {j+1}: '{text[:100]}...'")
        
        # Debug price extraction
        logger.info("💰 DEBUGGING DARAZ PRICE EXTRACTION")
        price_selectors = [
            '.pdp-price',
            '.price-current',
            '.price',
            '.product-price',
            '.pdp-price-current',
            '.price-box'
        ]
        
        for i, selector in enumerate(price_selectors):
            elements = soup.select(selector)
            logger.info(f"  Daraz Price Selector {i+1} '{selector}': Found {len(elements)} elements")
            if elements:
                for j, element in enumerate(elements[:3]):
                    text = element.get_text(strip=True)
                    logger.info(f"    Daraz Price Element {j+1}: '{text}'")
        
        return soup
    
    def debug_generic_scraping(self, url):
        """Debug generic scraping for unknown platforms"""
        logger.info("🌐 DEBUGGING GENERIC SCRAPING")
        
        response, status = self.debug_request(url)
        if not response:
            return None
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Look for common e-commerce elements
        logger.info("🔍 LOOKING FOR COMMON E-COMMERCE ELEMENTS")
        
        # Check for title elements
        title_candidates = soup.find_all(['h1', 'h2', 'h3'], string=True)
        logger.info(f"Found {len(title_candidates)} potential title elements:")
        for i, element in enumerate(title_candidates[:5]):
            text = element.get_text(strip=True)
            if len(text) > 10:  # Likely a product title
                logger.info(f"  Title Candidate {i+1}: '{text[:100]}...'")
        
        # Check for price elements
        price_candidates = soup.find_all(string=True)
        price_texts = [text for text in price_candidates if any(symbol in text for symbol in ['$', '€', '£', '₹', 'PKR'])]
        logger.info(f"Found {len(price_texts)} potential price elements:")
        for i, text in enumerate(price_texts[:5]):
            logger.info(f"  Price Candidate {i+1}: '{text.strip()}'")
        
        return soup
    
    def test_platform_detection(self, url):
        """Test platform detection"""
        domain = urlparse(url).netloc.lower()
        logger.info(f"🌐 Testing platform detection for: {domain}")
        
        platforms = {
            'amazon': 'amazon' in domain,
            'daraz': 'daraz' in domain,
            'ebay': 'ebay' in domain,
            'aliexpress': 'aliexpress' in domain,
            'walmart': 'walmart' in domain,
            'target': 'target' in domain
        }
        
        detected = [platform for platform, detected in platforms.items() if detected]
        logger.info(f"🎯 Detected platforms: {detected}")
        
        return detected[0] if detected else 'generic'
    
    def comprehensive_debug(self, url):
        """Run comprehensive debugging for any URL"""
        logger.info("=" * 80)
        logger.info(f"🚀 COMPREHENSIVE DEBUGGING FOR: {url}")
        logger.info("=" * 80)
        
        # Test platform detection
        platform = self.test_platform_detection(url)
        logger.info(f"🎯 Detected Platform: {platform}")
        
        # Debug based on platform
        if platform == 'amazon':
            soup = self.debug_amazon_scraping(url)
        elif platform == 'daraz':
            soup = self.debug_daraz_scraping(url)
        else:
            soup = self.debug_generic_scraping(url)
        
        if soup:
            logger.info("✅ Debugging completed successfully")
            return True
        else:
            logger.error("❌ Debugging failed")
            return False

def main():
    """Main debugging function"""
    debugger = DebugScraper()
    
    # Test URLs
    test_urls = [
        "https://www.daraz.pk/products/original-airpods_wireless-earbu",
        "https://www.amazon.com/dp/B08N5WRWNW",  # Example Amazon URL
        "https://www.ebay.com/itm/123456789",   # Example eBay URL
    ]
    
    print("🔍 Starting comprehensive scraper debugging...")
    print("📝 Logs will be saved to 'scraper_debug.log'")
    
    for i, url in enumerate(test_urls, 1):
        print(f"\n{'='*60}")
        print(f"🧪 TEST {i}: {url}")
        print(f"{'='*60}")
        
        success = debugger.comprehensive_debug(url)
        
        if success:
            print(f"✅ Test {i} completed successfully")
        else:
            print(f"❌ Test {i} failed")
        
        # Add delay between tests
        time.sleep(2)
    
    print("\n🎉 Debugging completed! Check 'scraper_debug.log' for detailed results.")

if __name__ == "__main__":
    main()

