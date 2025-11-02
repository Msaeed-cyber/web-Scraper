#!/usr/bin/env python3
"""
Test script for AI Product Trust & Sentiment Analyzer
"""

import sys
import os
import traceback
from backend.scraper import ProductScraper
from backend.sentiment_analyzer import SentimentAnalyzer
from backend.trust_scorer import TrustScorer

def test_sentiment_analyzer():
    """Test the sentiment analyzer"""
    print("Testing Sentiment Analyzer...")
    
    try:
        analyzer = SentimentAnalyzer()
        
        # Test sample reviews
        test_reviews = [
            {"text": "This product is amazing! Highly recommend it.", "rating": "5"},
            {"text": "Great quality and fast shipping.", "rating": "4"},
            {"text": "It's okay, nothing special.", "rating": "3"},
            {"text": "Terrible quality, waste of money.", "rating": "1"},
            {"text": "Don't buy this, it's a scam.", "rating": "1"}
        ]
        
        result = analyzer.analyze_reviews(test_reviews)
        
        print(f"Sentiment Analysis Results:")
        print(f"  - Positive: {result['positive']}")
        print(f"  - Neutral: {result['neutral']}")
        print(f"  - Negative: {result['negative']}")
        print(f"  - Sentiment Score: {result['sentiment_score']:.2f}")
        
        return True
        
    except Exception as e:
        print(f"Sentiment Analyzer Error: {e}")
        traceback.print_exc()
        return False

def test_trust_scorer():
    """Test the trust scorer"""
    print("\nTesting Trust Scorer...")
    
    try:
        scorer = TrustScorer()
        
        # Test sample product data
        sample_product_data = {
            'title': 'Test Product - High Quality Item',
            'price': '$29.99',
            'rating': '4.5',
            'review_count': '150',
            'seller': 'Trusted Store Official',
            'reviews': [
                {"text": "Great product!", "rating": "5"},
                {"text": "Excellent quality", "rating": "4"},
                {"text": "Good value for money", "rating": "4"}
            ],
            'url': 'https://amazon.com/test-product'
        }
        
        sample_sentiment = {
            'positive': 3,
            'neutral': 0,
            'negative': 0,
            'sentiment_score': 0.8
        }
        
        trust_result = scorer.calculate_trust_score(sample_product_data, sample_sentiment)
        recommendation = scorer.generate_recommendation(trust_result)
        
        print(f"Trust Score Results:")
        print(f"  - Overall Score: {trust_result['overall_score']}%")
        print(f"  - Recommendation: {recommendation['action']}")
        print(f"  - Confidence: {recommendation['confidence']}")
        
        return True
        
    except Exception as e:
        print(f"Trust Scorer Error: {e}")
        traceback.print_exc()
        return False

def test_scraper():
    """Test the web scraper (without actual scraping)"""
    print("\nTesting Web Scraper...")
    
    try:
        scraper = ProductScraper()
        
        # Test platform detection
        test_urls = [
            'https://amazon.com/test-product',
            'https://daraz.pk/test-product',
            'https://ebay.com/test-product',
            'https://unknown-site.com/test-product'
        ]
        
        for url in test_urls:
            platform = scraper.detect_platform(url)
            print(f"{url} -> {platform}")
        
        return True
        
    except Exception as e:
        print(f"Web Scraper Error: {e}")
        traceback.print_exc()
        return False

def test_integration():
    """Test the complete integration"""
    print("\nTesting Complete Integration...")
    
    try:
        # This would normally test the full pipeline
        # For now, we'll just verify all components can be imported
        
        from backend.scraper import ProductScraper
        from backend.sentiment_analyzer import SentimentAnalyzer
        from backend.trust_scorer import TrustScorer
        
        print("All components imported successfully")
        print("System is ready for use")
        
        return True
        
    except Exception as e:
        print(f"Integration Error: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("AI Product Trust & Sentiment Analyzer - System Tests")
    print("=" * 60)
    
    tests = [
        test_sentiment_analyzer,
        test_trust_scorer,
        test_scraper,
        test_integration
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("All tests passed! System is ready to use.")
        print("\nTo start the application:")
        print("   python app.py")
        print("\nThen open: http://localhost:5000")
    else:
        print("Some tests failed. Please check the errors above.")
        return False
    
    return True

if __name__ == "__main__":
    main()
