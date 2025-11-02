import unittest
from pathlib import Path
from backend.scraper import ProductScraper

class TestIntegrationFixtures(unittest.TestCase):
    def setUp(self):
        self.scraper = ProductScraper()
        self.fixtures_dir = Path(__file__).parent / 'fixtures'

    def _load_fixture(self, name):
        p = self.fixtures_dir / name
        return p.read_text(encoding='utf-8')

    def test_amazon_fixture(self):
        html = self._load_fixture('amazon_sample.html')
        data = self.scraper.extract_data(html, 'amazon', url='https://www.amazon.com/dp/B00TEST123')
        self.assertIsInstance(data, dict)
        self.assertIn('title', data)
        self.assertTrue('Sample Amazon Product' in data['title'])
        self.assertTrue(data['price'].startswith('$'))
        self.assertEqual(data['rating'], 4.5)
        self.assertEqual(data['review_count'], 123)
        self.assertTrue(len(data.get('reviews', [])) >= 1)

    def test_ebay_fixture(self):
        html = self._load_fixture('ebay_sample.html')
        data = self.scraper.extract_data(html, 'ebay', url='https://www.ebay.com/itm/999999')
        self.assertIsInstance(data, dict)
        self.assertIn('title', data)
        self.assertTrue('Sample eBay Product' in data['title'])
        self.assertTrue(data['price'].startswith('$'))
        self.assertEqual(data['rating'], 3.9)
        self.assertEqual(data['review_count'], 45)
        self.assertTrue(len(data.get('reviews', [])) >= 1)

    def test_aliexpress_fixture(self):
        html = self._load_fixture('aliexpress_sample.html')
        data = self.scraper.extract_data(html, 'aliexpress', url='https://www.aliexpress.com/item/12345.html')
        self.assertIsInstance(data, dict)
        self.assertIn('title', data)
        self.assertTrue('AliExpress Fancy Gadget' in data['title'])
        self.assertTrue(data['price'].startswith('$'))
        self.assertEqual(data['rating'], 4.0)
        self.assertEqual(data['review_count'], 10)
        self.assertTrue(len(data.get('reviews', [])) >= 1)

if __name__ == '__main__':
    unittest.main()
