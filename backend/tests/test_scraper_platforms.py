import unittest
from backend.scraper import ProductScraper

class TestScraperPlatformDetection(unittest.TestCase):
    def setUp(self):
        self.scraper = ProductScraper()

    def test_detect_platform_amazon(self):
        self.assertEqual(self.scraper.detect_platform('www.amazon.com'), 'amazon')
        self.assertEqual(self.scraper.detect_platform('amazon.co.uk'), 'amazon')

    def test_detect_platform_ebay(self):
        self.assertEqual(self.scraper.detect_platform('www.ebay.com'), 'ebay')

    def test_extract_price(self):
        p = self.scraper.extract_price('Only $1,234.56 for a limited time')
        self.assertEqual(p, '$1234.56')
        p2 = self.scraper.extract_price('Price: 99.99 USD')
        self.assertEqual(p2, '$99.99')

    def test_extract_data_jsonld(self):
        # sample minimal HTML containing JSON-LD Product
        html = '''
        <html><head><title>Sample</title>
        <script type="application/ld+json">
        {
          "@context": "http://schema.org/",
          "@type": "Product",
          "name": "Test Product 123",
          "offers": {
            "@type": "Offer",
            "price": "19.95",
            "priceCurrency": "USD"
          },
          "aggregateRating": {
            "@type": "AggregateRating",
            "ratingValue": "4.2",
            "reviewCount": "42"
          },
          "review": [
            {"@type": "Review", "reviewBody": "Excellent product"},
            {"@type": "Review", "reviewBody": "Not bad"}
          ]
        }
        </script>
        </head><body>Product page</body></html>
        '''
        data = self.scraper.extract_data(html, 'amazon')
        self.assertIsInstance(data, dict)
        self.assertIn('title', data)
        self.assertTrue('Test Product' in data['title'] or 'Test Product' in data.get('title', ''))
        self.assertIn('price', data)
        self.assertTrue(data['price'].startswith('$'))
        self.assertEqual(data['rating'], 4.2)
        self.assertEqual(data['review_count'], 42)
        self.assertTrue(len(data.get('reviews', [])) >= 1)

if __name__ == '__main__':
    unittest.main()
