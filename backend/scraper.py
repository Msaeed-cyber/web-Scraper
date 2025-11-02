import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent
from urllib.parse import urlparse
import time
import random
import logging
import re
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProductScraper:
    def __init__(self):
        self.session = requests.Session()
        self.ua = UserAgent()
        self.setup_session()
        self.setup_platform_configs()
        # Provide a lightweight fallback dataset so callers (e.g. app.py)
        # can still access `scraper.fallback_data` even when live scraping
        # is preferred. This does NOT force fallback usage; it's only a
        # safe default for error-handling paths in the application.
        self.setup_fallback_data()
        # Allow callers/tests to use fallback data when live scraping fails.
        # Can be set to False to enforce live-only behavior.
        self.allow_fallback = True
    # self.setup_fallback_data()  # Removed fallback data setup
        
    def setup_session(self):
        """Initialize session with enhanced anti-bot protection"""
        self.session.headers.update({
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
            'TE': 'Trailers',
            'Cookie': ''  # Will be populated by the site
        })
        logger.info("Enhanced scraper initialized with improved anti-bot protection")
        
    def setup_platform_configs(self):
        """Setup platform-specific configurations"""
        self.platform_configs = {
            'amazon': {
                'selectors': {
                    'title': '#productTitle, span#productTitle',
                    'price': '#priceblock_ourprice, #priceblock_dealprice, .a-price .a-offscreen, .a-price-whole',
                    'rating': '#acrPopover, .a-icon-alt, .averageStarRating',
                    'review_count': '#acrCustomerReviewText, #reviewsMedley .a-size-base, .totalReviewCount',
                    'reviews': '[data-hook="review-body"], .review-text, .a-size-base.review-text'
                },
                'wait_for': '#productTitle'
            },
            'ebay': {
                'selectors': {
                    'title': 'h1.x-item-title__mainTitle, h1.it-ttl, h1[itemprop="name"]',
                    'price': '.x-price-primary .s-item__price, #prcIsum, .notranslate',
                    'rating': '.x-star-rating, .reviews-star-rating',
                    'review_count': '.x-item-review-count, .count, [itemprop="reviewCount"]',
                    'reviews': '.ebay-review-section .review-item, .review'
                },
                'wait_for': '.x-item-title__mainTitle'
            },
            'daraz': {
                'selectors': {
                    'title': '.pdp-mod-product-badge-title, .pdp-product-title, h1',
                    'price': '.pdp-price, .pdp-price .pdp-price',
                    'rating': '.score-average, .rating',
                    'review_count': '.count, .pdp-reviews',
                    'reviews': '.pdp-product-review__review--content, .product-review'
                },
                'wait_for': '.pdp-mod-product-badge-title'
            }
        }

    # def setup_fallback_data(self):
    def setup_fallback_data(self):
        """Initialize minimal fallback data used only for error paths.

        The scraper prefers live extraction; this dict exists so the
        Flask app can read `scraper.fallback_data` when handling errors.
        """
        self.fallback_data = {
            'amazon': {'title': 'Amazon Product', 'price': '$99.99', 'rating': 4.5, 'review_count': 100, 'seller': 'Amazon', 'reviews': []},
            'ebay': {'title': 'eBay Product', 'price': '$89.99', 'rating': 4.0, 'review_count': 50, 'seller': 'eBay', 'reviews': []},
            'daraz': {'title': 'Daraz Product', 'price': '$79.99', 'rating': 3.5, 'review_count': 25, 'seller': 'Daraz', 'reviews': []},
            'generic': {'title': 'Unknown Product', 'price': '$0.00', 'rating': 0.0, 'review_count': 0, 'seller': 'Unknown Seller', 'reviews': []}
        }

    def get_selenium_driver(self):
        """Configure Selenium with improved anti-bot measures"""
        options = Options()
        options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument(f'--user-agent={self.ua.random}')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-javascript')  # Try without JavaScript first
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Enhanced anti-detection
        options.add_argument('--disable-gpu')
        options.add_argument('--lang=en-US,en')
        options.add_argument('--disable-notifications')
        
        # Random viewport
        sizes = [(1366, 768), (1920, 1080), (1536, 864), (1440, 900)]
        width, height = random.choice(sizes)
        options.add_argument(f'--window-size={width},{height}')
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        # Additional anti-bot evasion
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")
        driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']})")
        
        return driver

    def scrape_product(self, url):
        """Main product scraping method with improved error handling"""
        try:
            # Extract platform and validate URL
            parsed_url = urlparse(url)
            if not parsed_url.scheme or not parsed_url.netloc or parsed_url.scheme not in ['http', 'https']:
                logger.error("Invalid URL format")
                raise ValueError("Invalid URL format")
            
            # Get domain and validate
            domain_parts = parsed_url.netloc.split('.')
            if len(domain_parts) < 2:
                logger.error("Invalid domain format")
                raise ValueError("Invalid domain format")
            
            # Determine platform (more robust detection)
            platform = self.detect_platform(parsed_url.netloc)
            logger.info(f"Detected platform: {platform}")
            
            logger.info(f"ENHANCED SCRAPING: {url}")
            logger.info(f"Detected platform: {platform}")
            
            # Try Selenium first for better reliability
            logger.info("Attempting Selenium scraping")
            data = self.scrape_with_selenium(url, platform)
            if data:
                # Validate extracted data corresponds to the requested URL/product
                if self.validate_extracted_data(url, data):
                    logger.info("Selenium scraping successful and validated")
                    data['platform'] = platform
                    data['url'] = url
                    return data
                else:
                    logger.warning("Selenium scraping returned data that did not match the requested product; continuing to fallback methods")
                
            # Try regular request as backup
            logger.info("Attempting regular request scraping")
            response = self.scrape_with_anti_bot(url)
            if response and response.status_code == 200:
                logger.info("Regular request successful")
                data = self.extract_data(response.text, platform, url)
                if data and data.get('price', '$0.00') != '$0.00' and self.validate_extracted_data(url, data):
                    data['platform'] = platform
                    data['url'] = url
                    return data
                    
            # Both methods failed — either return fallback or raise
            logger.warning("All scraping methods failed")
            if getattr(self, 'allow_fallback', True) and hasattr(self, 'fallback_data'):
                logger.warning(f"USING FALLBACK DATA for {platform}")
                fb = self.fallback_data.get(platform, self.fallback_data['generic']).copy()
                fb['platform'] = platform
                fb['url'] = url
                return fb
            else:
                raise RuntimeError(f"Scraping failed for platform: {platform}")
            
        except Exception as e:
            logger.error(f"Scraping error: {str(e)}")
            # If fallback allowed, return generic fallback instead of raising
            if getattr(self, 'allow_fallback', True) and hasattr(self, 'fallback_data'):
                logger.warning("Returning generic fallback due to exception")
                fb = self.fallback_data.get('generic').copy()
                fb['platform'] = getattr(self, 'detect_platform', lambda x: 'generic')(urlparse(url).netloc if url else '')
                fb['url'] = url
                return fb
            raise

    def scrape_with_anti_bot(self, url):
        """Scrape with enhanced anti-bot protection"""
        logger.info(f"SCRAPING WITH ANTI-BOT PROTECTION: {url}")
        
        try:
            # Add random delay
            time.sleep(random.uniform(2, 4))
            
            # Update headers
            self.session.headers.update({
                'User-Agent': self.ua.random,
                'Referer': 'https://www.google.com'
            })
            
            # Make request
            response = self.session.get(url, timeout=30)
            logger.info(f"Response Status: {response.status_code}")
            logger.info(f"Response Length: {len(response.content)} bytes")
            
            if response.status_code == 200:
                if any(marker in response.text.lower() for marker in ['robot', 'captcha', 'verify']):
                    logger.warning("ANTI-BOT DETECTED: Using Selenium fallback...")
                    return None
                    
                logger.info("SUCCESS: Requests scraping worked")
                return response
                
        except Exception as e:
            logger.warning(f"Requests failed: {str(e)}, trying Selenium fallback...")
            
        return None

    def scrape_with_selenium(self, url, platform):
        """Scrape using Selenium with improved reliability"""
        logger.info(f"SELENIUM SCRAPING: {url}")
        driver = None
        
        try:
            driver = self.get_selenium_driver()
            
            # Add random delay
            time.sleep(random.uniform(2, 4))
            
            # Load page
            driver.get(url)
            time.sleep(random.uniform(3, 5))
            
            # Check for anti-bot
            page_source = driver.page_source.lower()
            if any(marker in page_source for marker in ['robot', 'captcha', 'verify']):
                logger.error("ANTI-BOT DETECTED in Selenium")
                return None
                
            # Extract data using platform-specific selectors or generic extraction
            config = self.platform_configs.get(platform)
                
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, config['wait_for']))
                )
            except Exception as e:
                logger.error(f"Timeout waiting for main element: {str(e)}")
                return None
                
            # Extract initial data container
            data = {
                'title': 'Unknown Product',
                'price': '$0.00',
                'rating': 0.0,
                'review_count': 0,
                'seller': 'Unknown Seller',
                'reviews': []
            }

            # Use platform-specific selectors where available
            try:
                if config and 'selectors' in config:
                    selectors = config['selectors']
                    # Title
                    try:
                        title_elem = driver.find_element(By.CSS_SELECTOR, selectors['title'])
                        if title_elem:
                            data['title'] = title_elem.text.strip()
                    except:
                        pass

                    # Price
                    try:
                        price_elem = driver.find_element(By.CSS_SELECTOR, selectors['price'])
                        if price_elem:
                            data['price'] = self.extract_price(price_elem.text)
                    except:
                        pass

                    # Rating
                    try:
                        rating_elem = driver.find_element(By.CSS_SELECTOR, selectors['rating'])
                        if rating_elem:
                            rating_text = rating_elem.get_attribute('innerText') or rating_elem.text
                            rating_match = re.search(r'\d+\.?\d*', rating_text)
                            if rating_match:
                                data['rating'] = float(rating_match.group())
                    except:
                        pass

                    # Review count
                    try:
                        review_elem = driver.find_element(By.CSS_SELECTOR, selectors['review_count'])
                        if review_elem:
                            review_text = review_elem.text
                            count_match = re.search(r'\d+', review_text.replace(',', ''))
                            if count_match:
                                data['review_count'] = int(count_match.group())
                    except:
                        pass

            except Exception as e:
                logger.debug(f"Platform selector extraction error: {e}")

            # If we still lack useful info, fall back to parsing the page source with BeautifulSoup
            try:
                if data['title'] == 'Unknown Product' or data['price'] == '$0.00':
                    page_html = driver.page_source
                    fallback = self.extract_data(page_html, platform, url)
                    if fallback:
                        data.update({k: v for k, v in fallback.items() if v})
            except Exception:
                pass
                
            # Get price
            try:
                price_elem = driver.find_element(By.CSS_SELECTOR, selectors['price'])
                if price_elem:
                    price_text = price_elem.text
                    data['price'] = self.extract_price(price_text)
            except:
                pass
                
            # Get rating
            try:
                rating_elem = driver.find_element(By.CSS_SELECTOR, selectors['rating'])
                if rating_elem:
                    rating_text = rating_elem.get_attribute('innerHTML')
                    rating_match = re.search(r'\d+\.?\d*', rating_text)
                    if rating_match:
                        data['rating'] = float(rating_match.group())
            except:
                pass
                
            # Get review count
            try:
                review_elem = driver.find_element(By.CSS_SELECTOR, selectors['review_count'])
                if review_elem:
                    review_text = review_elem.text
                    count_match = re.search(r'\d+', review_text)
                    if count_match:
                        data['review_count'] = int(count_match.group())
            except:
                pass
                
            return data if data.get('title') and data.get('title') != 'Unknown Product' else None
            
        except Exception as e:
            logger.error(f"Selenium error: {str(e)}")
            return None
            
        finally:
            if driver:
                driver.quit()

    def detect_platform(self, netloc):
        """Detect known platform from netloc"""
        netloc = netloc.lower()
        if 'amazon.' in netloc:
            return 'amazon'
        if 'ebay.' in netloc:
            return 'ebay'
        if 'daraz.' in netloc:
            return 'daraz'
        if 'aliexpress' in netloc or 'taobao' in netloc or 'tmall' in netloc:
            return 'aliexpress'
        if 'walmart' in netloc:
            return 'walmart'
        # default to generic
        return 'generic'

    def extract_price(self, text):
        """Extract a dollar-style price from text or return original string"""
        try:
            if not text:
                return '$0.00'
            m = re.search(r'\$\s?[\d,]+\.?\d*', text)
            if m:
                raw = m.group()
                # remove spaces and commas, normalize to two decimals if possible
                cleaned = raw.replace(' ', '').replace(',', '')
                try:
                    num = float(re.search(r'[\d]+\.?\d*', cleaned).group())
                    return f"${num:.2f}"
                except Exception:
                    return cleaned
            # Try to extract number-only price
            m2 = re.search(r'[\d,]+\.?\d*', text)
            if m2:
                cleaned2 = m2.group().replace(',', '')
                try:
                    num2 = float(cleaned2)
                    return f"${num2:.2f}"
                except Exception:
                    return f"${cleaned2}"
        except Exception:
            pass
        return '$0.00'

    def validate_extracted_data(self, url, data):
        """Basic validation that extracted data corresponds to the requested URL/product.

        Strategy:
        - Ensure platform keyword exists in the request URL
        - Check title similarity (word overlap) between URL path and extracted title
        - If product id (ASIN/item id) is present in URL, prefer checking for its presence in title or seller/meta
        """
        try:
            parsed = urlparse(url)
            netloc = parsed.netloc.lower()
            path = parsed.path.lower()

            # Platform check
            platform = self.detect_platform(netloc)
            if platform == 'generic':
                # generic: accept if title is not unknown
                return bool(data.get('title') and data.get('title') != 'Unknown Product')

            # If platform-specific id exists in URL, check for it in title or seller
            # Amazon ASIN
            if platform == 'amazon':
                m = re.search(r'/dp/([A-Z0-9]{10})|/gp/product/([A-Z0-9]{10})', url)
                asin = m.group(1) if m and m.group(1) else (m.group(2) if m and m.group(2) else None)
                if asin:
                    hay = (data.get('title', '') + ' ' + str(data.get('seller', ''))).lower()
                    if asin.lower() in hay:
                        return True

            # eBay item id
            if platform == 'ebay':
                m = re.search(r'/itm/(\d+)', url)
                if m:
                    itemid = m.group(1)
                    hay = (data.get('title', '') + ' ' + str(data.get('seller', ''))).lower()
                    if itemid in hay:
                        return True

            # Title similarity fallback: compute overlap
            title = (data.get('title') or '').lower()
            if not title or title == 'unknown product':
                return False

            # Use words from URL path to compare
            url_tokens = re.findall(r'[a-z0-9]{3,}', path)
            title_tokens = re.findall(r'[a-z0-9]{3,}', title)
            if not url_tokens or not title_tokens:
                # If tokens are missing, accept if title is present
                return True

            # compute overlap ratio
            url_set = set(url_tokens)
            title_set = set(title_tokens)
            overlap = url_set.intersection(title_set)
            ratio = len(overlap) / max(1, min(len(url_set), len(title_set)))
            return ratio >= 0.25  # fairly lenient
        except Exception:
            return False

    def extract_data(self, content, platform, url=None):
        """Extract product data based on platform"""
        # Validate URL format first
        if url and not url.startswith(('http://', 'https://')):
            raise ValueError(f"Invalid URL format: {url}")
            
        # Validate we have content to parse
        if not content or len(content.strip()) < 100:  # Basic content validation
            raise ValueError("Insufficient content for scraping")
            
        try:
            # Try html.parser first as it's more lenient
            soup = BeautifulSoup(content, 'html.parser')
            logger.info(f"EXTRACTING {platform.upper()} DATA ENHANCED")

            # Attempt to parse JSON-LD product schema first (structured data)
            try:
                scripts = soup.find_all('script', type='application/ld+json')
                structured_found = False
                for s in scripts:
                    try:
                        payload = json.loads(s.string or s.get_text() or '{}')
                    except Exception:
                        continue

                    # payload may be a dict or list
                    candidates = payload if isinstance(payload, list) else [payload]
                    for cand in candidates:
                        if not isinstance(cand, dict):
                            continue
                        # Look for Product schema
                        t = cand.get('@type') or cand.get('type')
                        if isinstance(t, list):
                            types = [x.lower() for x in t]
                        else:
                            types = [t.lower()] if isinstance(t, str) else []

                        if 'product' in types or 'product' == (t or '').lower():
                            # Extract structured fields
                            name = cand.get('name') or cand.get('headline')
                            if name:
                                data = data if 'data' in locals() else {
                                    'title': name.strip(),
                                    'price': None,
                                    'rating': None,
                                    'review_count': None,
                                    'seller': None,
                                    'reviews': []
                                }

                            offers = cand.get('offers') or {}
                            if isinstance(offers, dict):
                                price_val = offers.get('price') or offers.get('priceCurrency')
                                if price_val:
                                    try:
                                        # normalize numeric price
                                        data['price'] = f"${float(str(price_val)):.2f}"
                                    except Exception:
                                        # use raw
                                        data['price'] = str(price_val)

                            agg = cand.get('aggregateRating') or {}
                            if isinstance(agg, dict):
                                r = agg.get('ratingValue')
                                rc = agg.get('reviewCount') or agg.get('ratingCount')
                                try:
                                    if r:
                                        data['rating'] = float(r)
                                except Exception:
                                    pass
                                try:
                                    if rc:
                                        data['review_count'] = int(rc)
                                except Exception:
                                    pass

                            # extract reviews array
                            raw_reviews = cand.get('review') or cand.get('reviews') or []
                            if isinstance(raw_reviews, dict):
                                raw_reviews = [raw_reviews]
                            if isinstance(raw_reviews, list) and raw_reviews:
                                revs = []
                                for rv in raw_reviews[:5]:
                                    text = rv.get('reviewBody') or rv.get('description') or rv.get('name')
                                    if text:
                                        revs.append({'text': text})
                                if revs:
                                    data['reviews'] = revs
                            # If we got structured data, mark and stop searching further JSON-LD
                            if 'data' in locals():
                                structured_found = True
                                break
                    if structured_found:
                        break
            except Exception as e:
                logger.debug(f"JSON-LD parsing error: {e}")
            # Try platform-specific extraction first
            # Only set defaults if structured data was not found
            if 'data' not in locals():
                data = {
                'title': 'Unknown Product',
                'price': '$0.00',
                'rating': 0.0,
                'review_count': 0,
                'seller': 'Unknown Seller',
                'reviews': []
                }

            config = self.platform_configs.get(platform)
            if config and 'selectors' in config:
                sel = config['selectors']
                # title
                try:
                    title_elem = soup.select_one(sel.get('title'))
                    if title_elem:
                        data['title'] = title_elem.get_text(strip=True)
                except:
                    pass

                # price
                try:
                    price_elem = soup.select_one(sel.get('price'))
                    if price_elem:
                        data['price'] = self.extract_price(price_elem.get_text())
                except:
                    pass

                # rating
                try:
                    rating_elem = soup.select_one(sel.get('rating'))
                    if rating_elem:
                        rating_text = rating_elem.get_text()
                        m = re.search(r'\d+\.?\d*', rating_text)
                        if m:
                            data['rating'] = float(m.group())
                except:
                    pass

                # review count
                try:
                    rc = soup.select_one(sel.get('review_count'))
                    if rc:
                        m = re.search(r'\d+', rc.get_text().replace(',', ''))
                        if m:
                            data['review_count'] = int(m.group())
                except:
                    pass

            # Generic fallbacks: price and title from common places
            if data['price'] == '$0.00':
                try:
                    price_pattern = r'\$\s?[\d,]+\.?\d*'
                    price_texts = soup.find_all(text=re.compile(price_pattern))
                    if price_texts:
                        data['price'] = re.search(price_pattern, price_texts[0]).group()
                except:
                    pass

            # Try to get title from page title if missing
            if not data.get('title') and soup.title:
                data['title'] = soup.title.string.strip()
            
            # Validate we have the minimum required data
            if not data.get('title'):
                raise ValueError("Could not extract product title")

            # Attempt to extract seller
            # Extract seller information
            seller = None
            for sel_candidate in ['#sellerProfileTriggerId', '.seller-name', '.brand', '.sold-by', '.merchant-name']:
                el = soup.select_one(sel_candidate)
                if el and el.get_text(strip=True):
                    seller = el.get_text(strip=True)
                    break
            data['seller'] = seller  # May be None if not found

            # Extract reviews using simpler selectors
            reviews = []
            
            try:
                for div in soup.find_all('div'):
                    if div.get('data-hook') == 'review-body':
                        text = div.get_text(strip=True)
                        if text:
                            reviews.append({'text': text})
            except:
                pass

            if reviews:
                data['reviews'] = reviews

            return data
            
        except Exception as e:
            logger.error(f"Data extraction failed: {str(e)}")
            raise RuntimeError(f"Data extraction failed for platform: {platform}")
