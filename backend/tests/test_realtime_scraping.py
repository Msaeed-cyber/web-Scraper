import unittest
import sys
import os
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))
from backend.scraper import ProductScraper

def load_fixture(filename):
    """Load test fixture HTML file"""
    fixture_path = Path(__file__).parent / 'fixtures' / filename
    with open(fixture_path, 'r', encoding='utf-8') as f:
        return f.read()

class TestRealtimeScraping(unittest.TestCase):
    def setUp(self):
        self.scraper = ProductScraper()

    def test_invalid_url(self):
        """Test that invalid URLs raise ValueError instead of returning fallback data"""
        with self.assertRaises(ValueError):
            self.scraper.extract_data("invalid-url", "amazon")
        
        with self.assertRaises(ValueError):
            self.scraper.extract_data("not-a-url", "ebay")

    def test_amazon_scraping(self):
        """Test real-time scraping using Amazon fixture"""
        url = "https://www.amazon.com/dp/test123"  # Test URL for validation
        content = load_fixture('amazon_product.html')
        
        result = self.scraper.extract_data(content, "amazon", url)
        self.assertIsNotNone(result)
        self.assertEqual(result['title'], 'Test Product Name')
        self.assertEqual(result['price'], '$29.99')
        self.assertEqual(result['rating'], 4.5)
        self.assertEqual(result['review_count'], 100)
        self.assertIn('seller', result)  # Seller may be None but should be present
        self.assertEqual(len(result['reviews']), 2)

    def test_ebay_scraping(self):
        """Test real-time scraping using eBay fixture"""
        url = "https://www.ebay.com/itm/test123"  # Test URL for validation
        content = load_fixture('ebay_item.html')
        
        result = self.scraper.extract_data(content, "ebay", url)
        self.assertIsNotNone(result)
        self.assertEqual(result['title'], 'Test eBay Item Name')
        self.assertEqual(result['price'], '$19.99')  # Price format should be consistent
        self.assertIn('seller', result)  # Seller may be None but should be present

    def test_failed_scraping_raises_error(self):
        """Test that failed scraping raises an error instead of returning fallback data"""
        with self.assertRaises(Exception):
            self.scraper.extract_data("https://nonexistent-site-12345.com/product", "amazon")

if __name__ == '__main__':
    unittest.main()