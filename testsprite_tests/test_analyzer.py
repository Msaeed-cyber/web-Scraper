import unittest
import sys
import os
import json
from flask import Flask
from urllib.parse import urlparse
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.scraper import ProductScraper
from app import app

class TestProductAnalyzer(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.scraper = ProductScraper()

    def test_tc001_valid_url(self):
        """TC001: Test product analysis with valid URL"""
        # Test with multiple valid URLs
        test_urls = [
            "https://www.amazon.com/dp/B08N5KWB9H",
            "https://www.ebay.com/itm/123456789",
            "https://www.daraz.pk/products/sample-1234"
        ]
        
        for url in test_urls:
            response = self.app.post('/analyze', json={'url': url})
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            
            # Verify response structure
            self.assertIn('product_info', data)
            self.assertIn('sentiment_analysis', data)
            self.assertIn('trust_score', data)
            self.assertIn('recommendation', data)
            
            # Verify product info
            product_info = data['product_info']
            self.assertIsNotNone(product_info.get('title'))
            self.assertIsNotNone(product_info.get('price'))
            self.assertIsNotNone(product_info.get('rating'))
            self.assertIsNotNone(product_info.get('review_count'))
            
            # Verify trust score format
            trust_score = data['trust_score']
            self.assertIsInstance(trust_score, float)
            self.assertTrue(0 <= trust_score <= 1)

    def test_tc002_missing_url(self):
        """TC002: Test with missing URL"""
        response = self.app.post('/analyze', json={})
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('URL is required', data['error'])

    def test_tc003_invalid_url_format(self):
        """TC003: Test with invalid URL format"""
        test_cases = [
            "not_a_url",
            "http://",
            "https://.com",
            "ftp://invalid.com",
            ""
        ]
        
        for url in test_cases:
            response = self.app.post('/analyze', json={'url': url})
            self.assertEqual(response.status_code, 400)
            data = json.loads(response.data)
            self.assertIn('error', data)

    def test_tc004_unsupported_platform(self):
        """TC004: Test with unsupported platform"""
        test_urls = [
            "https://www.unsupported.com/product/123",
            "https://unknown-shop.net/item/456",
            "https://example.org/product"
        ]
        
        for url in test_urls:
            response = self.app.post('/analyze', json={'url': url})
            self.assertEqual(response.status_code, 200)  # Should still return 200 with fallback data
            data = json.loads(response.data)
            
            # Should use generic fallback data
            product_info = data['product_info']
            self.assertEqual(product_info['title'], 'Unknown Product')
            self.assertEqual(product_info['price'], '$0.00')
            self.assertEqual(product_info['rating'], 0.0)
            self.assertEqual(product_info['review_count'], 0)

    def test_tc005_internal_server_error(self):
        """TC005: Test internal server error handling"""
        # Test with a URL that should trigger scraping errors
        test_urls = [
            "https://www.amazon.com/404_not_found",
            "https://www.ebay.com/deleted_item",
            "https://www.daraz.pk/nonexistent"
        ]
        
        for url in test_urls:
            response = self.app.post('/analyze', json={'url': url})
            # Should either return 500 or 200 with fallback data
            self.assertIn(response.status_code, [500, 200])
            data = json.loads(response.data)
            if response.status_code == 200:
                self.assertIn('product_info', data)
            else:
                self.assertIn('error', data)

    def test_tc006_main_page_load(self):
        """TC006: Test main page load"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'text/html', response.headers['Content-Type'].encode())

    def test_url_validation(self):
        """Additional test: URL validation"""
        valid_urls = [
            "https://www.amazon.com/dp/B08N5KWB9H",
            "https://www.ebay.com/itm/123456789",
            "http://www.daraz.pk/products/sample"
        ]
        
        invalid_urls = [
            "not_a_url",
            "http://",
            "https://.com",
            "",
            None,
            "ftp://example.com",
            "https://invalid-.com",
            "https://invalid.-domain.com",
            "https://domain..com"
        ]
        
        # Test valid URLs
        for url in valid_urls:
            response = self.app.post('/analyze', json={'url': url})
            self.assertEqual(response.status_code, 200)
        
        # Test invalid URLs
        for url in invalid_urls:
            response = self.app.post('/analyze', json={'url': url})
            self.assertEqual(response.status_code, 400)
            data = json.loads(response.data)
            self.assertIn('error', data)

    def test_scraper_fallback(self):
        """Additional test: Scraper fallback mechanism"""
        url = "https://www.amazon.com/dp/B08N5KWB9H"
        scraper = ProductScraper()
        
        # Test scraping with anti-bot detection
        result = scraper.scrape_product(url)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)
        
        # Verify fallback data structure
        self.assertIn('title', result)
        self.assertIn('price', result)
        self.assertIn('rating', result)
        self.assertIn('review_count', result)
        
        # Verify price format
        self.assertTrue(result['price'].startswith('$'))
        self.assertTrue(float(result['price'].replace('$', '')) >= 0)

    def test_trust_score_calculation(self):
        """Additional test: Trust score calculation"""
        response = self.app.post('/analyze', json={'url': 'https://www.amazon.com/dp/B08N5KWB9H'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        # Verify trust score
        self.assertIn('trust_score', data)
        trust_score = data['trust_score']
        self.assertIsInstance(trust_score, float)
        self.assertTrue(0 <= trust_score <= 1)
        
        # Verify trust score components
        if 'trust_score_components' in data:
            components = data['trust_score_components']
            required_components = ['domain', 'review_quality', 'rating_consistency', 'seller', 'price']
            for component in required_components:
                self.assertIn(component, components)
                self.assertTrue(0 <= components[component] <= 1)

if __name__ == '__main__':
    unittest.main(verbosity=2)