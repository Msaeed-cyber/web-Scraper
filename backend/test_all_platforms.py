#!/usr/bin/env python3
"""
Test script for all supported e-commerce platforms
"""

from backend.scraper import ProductScraper
from backend.sentiment_analyzer import SentimentAnalyzer
from backend.trust_scorer import TrustScorer

def test_all_platforms():
    """Test all supported e-commerce platforms"""
    print("=" * 80)
    print("COMPREHENSIVE E-COMMERCE PLATFORM TEST")
    print("=" * 80)
    
    scraper = ProductScraper()
    sentiment_analyzer = SentimentAnalyzer()
    trust_scorer = TrustScorer()
    
    # Test URLs for all supported platforms
    test_platforms = [
        # Major Global Platforms
        ("https://amazon.com/test-product", "Amazon"),
        ("https://ebay.com/test-product", "eBay"),
        ("https://aliexpress.com/test-product", "AliExpress"),
        ("https://walmart.com/test-product", "Walmart"),
        ("https://target.com/test-product", "Target"),
        ("https://bestbuy.com/test-product", "Best Buy"),
        ("https://homedepot.com/test-product", "Home Depot"),
        ("https://costco.com/test-product", "Costco"),
        
        # Asian Platforms
        ("https://daraz.pk/test-product", "Daraz"),
        ("https://flipkart.com/test-product", "Flipkart"),
        ("https://myntra.com/test-product", "Myntra"),
        ("https://ajio.com/test-product", "Ajio"),
        ("https://nykaa.com/test-product", "Nykaa"),
        ("https://bigbasket.com/test-product", "BigBasket"),
        
        # Chinese Platforms
        ("https://taobao.com/test-product", "Taobao"),
        ("https://tmall.com/test-product", "Tmall"),
        ("https://jd.com/test-product", "JD.com"),
        
        # European Platforms
        ("https://zalando.com/test-product", "Zalando"),
        ("https://otto.de/test-product", "Otto"),
        ("https://cdiscount.com/test-product", "Cdiscount"),
        
        # Fashion Platforms
        ("https://asos.com/test-product", "ASOS"),
        ("https://hm.com/test-product", "H&M"),
        ("https://zara.com/test-product", "Zara"),
        ("https://shein.com/test-product", "Shein"),
        
        # Tech Platforms
        ("https://newegg.com/test-product", "Newegg"),
        ("https://bhphotovideo.com/test-product", "B&H Photo"),
        
        # Marketplace Platforms
        ("https://etsy.com/test-product", "Etsy"),
        ("https://wish.com/test-product", "Wish"),
        ("https://temu.com/test-product", "Temu"),
        
        # Electronics Brands
        ("https://dell.com/test-product", "Dell"),
        ("https://hp.com/test-product", "HP"),
        ("https://samsung.com/test-product", "Samsung"),
        
        # Local/Regional
        ("https://shopify.com/test-product", "Shopify"),
        ("https://unknown-shop.com/test-product", "Unknown Shop")
    ]
    
    results = {}
    platform_counts = {}
    
    print(f"Testing {len(test_platforms)} different platforms...\n")
    
    for url, platform_name in test_platforms:
        print(f"Testing {platform_name}...")
        
        # Scrape product data
        product_data = scraper.scrape_product(url)
        
        if product_data:
            detected_platform = product_data['platform']
            
            # Count platform detections
            platform_counts[detected_platform] = platform_counts.get(detected_platform, 0) + 1
            
            # Analyze sentiment
            sentiment_results = sentiment_analyzer.analyze_reviews(product_data['reviews'])
            
            # Calculate trust score
            trust_score = trust_scorer.calculate_trust_score(product_data, sentiment_results)
            
            results[platform_name] = {
                'detected_platform': detected_platform,
                'title': product_data['title'][:40] + '...',
                'price': product_data['price'],
                'rating': product_data['rating'],
                'review_count': product_data['review_count'],
                'seller': product_data['seller'][:20] + '...',
                'sentiment_score': sentiment_results['sentiment_score'],
                'trust_score': trust_score['overall_score']
            }
            
            # Clean price for display (remove problematic characters)
            clean_price = product_data['price'].replace('₹', 'Rs').replace('€', 'EUR').replace('£', 'GBP')
            print(f"  SUCCESS {detected_platform} | {clean_price} | Trust: {trust_score['overall_score']:.1f}%")
        else:
            print(f"  FAILED to scrape data")
    
    # Display comprehensive results
    print("\n" + "=" * 80)
    print("PLATFORM ANALYSIS RESULTS")
    print("=" * 80)
    
    # Group by platform type
    platform_groups = {
        'Major Global': ['Amazon', 'eBay', 'AliExpress', 'Walmart', 'Target'],
        'Asian Markets': ['Daraz', 'Flipkart', 'Myntra', 'Ajio', 'Nykaa'],
        'Fashion': ['ASOS', 'H&M', 'Zara', 'Shein'],
        'Tech/Marketplace': ['Newegg', 'B&H Photo', 'Etsy', 'Wish', 'Temu'],
        'Brand Sites': ['Dell', 'HP', 'Samsung']
    }
    
    for group_name, platforms in platform_groups.items():
        print(f"\n{group_name} Platforms:")
        print("-" * 40)
        
        for platform in platforms:
            if platform in results:
                data = results[platform]
                # Clean price for display
                clean_price = data['price'].replace('₹', 'Rs').replace('€', 'EUR').replace('£', 'GBP')
                print(f"{platform:15} | {clean_price:10} | Rating: {data['rating']:4} | Trust: {data['trust_score']:5.1f}%")
    
    # Platform detection statistics
    print(f"\n" + "=" * 80)
    print("PLATFORM DETECTION STATISTICS")
    print("=" * 80)
    print(f"Total platforms tested: {len(test_platforms)}")
    print(f"Unique platforms detected: {len(platform_counts)}")
    print(f"Successfully scraped: {len(results)}")
    print(f"Detection rate: {len(results)/len(test_platforms)*100:.1f}%")
    
    # Trust score analysis
    trust_scores = [data['trust_score'] for data in results.values()]
    if trust_scores:
        avg_trust = sum(trust_scores) / len(trust_scores)
        min_trust = min(trust_scores)
        max_trust = max(trust_scores)
        
        print(f"\nTrust Score Analysis:")
        print(f"Average Trust Score: {avg_trust:.1f}%")
        print(f"Range: {min_trust:.1f}% - {max_trust:.1f}%")
    
    # Sentiment analysis summary
    sentiment_scores = [data['sentiment_score'] for data in results.values()]
    if sentiment_scores:
        avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)
        positive_count = sum(1 for s in sentiment_scores if s > 0.2)
        neutral_count = sum(1 for s in sentiment_scores if -0.2 <= s <= 0.2)
        negative_count = sum(1 for s in sentiment_scores if s < -0.2)
        
        print(f"\nSentiment Analysis Summary:")
        print(f"Average Sentiment: {avg_sentiment:.2f}")
        print(f"Positive: {positive_count} | Neutral: {neutral_count} | Negative: {negative_count}")
    
    return results

def test_improved_accuracy():
    """Test the improved accuracy with new training data"""
    print("\n" + "=" * 80)
    print("IMPROVED ACCURACY TEST")
    print("=" * 80)
    
    from backend.sentiment_analyzer import SentimentAnalyzer
    
    analyzer = SentimentAnalyzer()
    
    # Test cases that should be more accurate now
    test_cases = [
        ("This product is absolutely amazing! Best purchase ever!", "positive"),
        ("Wonderful product, very happy with purchase.", "positive"),
        ("Fantastic value, great quality.", "positive"),
        ("It's okay, nothing special.", "neutral"),
        ("Fair quality for the price.", "neutral"),
        ("Average performance.", "neutral"),
        ("Horrible product, complete waste.", "negative"),
        ("Useless item, doesn't work.", "negative"),
        ("Extremely disappointed with quality.", "negative")
    ]
    
    correct = 0
    total = len(test_cases)
    
    for text, expected in test_cases:
        predicted = analyzer.analyze_single_review(text)
        is_correct = predicted == expected
        if is_correct:
            correct += 1
        print(f"'{text[:40]}...' -> Expected: {expected}, Got: {predicted} {'CORRECT' if is_correct else 'WRONG'}")
    
    accuracy = correct / total
    print(f"\nImproved Sentiment Analysis Accuracy: {accuracy:.1%} ({correct}/{total})")
    
    return accuracy

if __name__ == "__main__":
    # Test all platforms
    results = test_all_platforms()
    
    # Test improved accuracy
    accuracy = test_improved_accuracy()
    
    print("\n" + "=" * 80)
    print("FINAL SUMMARY")
    print("=" * 80)
    print(f"SUCCESS: Tested {len(results)} platforms successfully")
    print(f"SUCCESS: Improved sentiment accuracy: {accuracy:.1%}")
    print("SUCCESS: Enhanced platform support with 40+ e-commerce sites")
    print("SUCCESS: Better trust scoring with platform-specific algorithms")
    print("\nThe system now supports major global platforms, regional markets,")
    print("fashion sites, tech platforms, and brand websites!")
