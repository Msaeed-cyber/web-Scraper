#!/usr/bin/env python3
"""
Comprehensive accuracy test for the AI Product Trust & Sentiment Analyzer
"""

import sys
import os
from backend.sentiment_analyzer import SentimentAnalyzer
from backend.trust_scorer import TrustScorer
from backend.scraper import ProductScraper
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import numpy as np

def test_sentiment_model_accuracy():
    """Test the accuracy of the sentiment analysis model"""
    print("=" * 60)
    print("SENTIMENT ANALYSIS MODEL ACCURACY TEST")
    print("=" * 60)
    
    analyzer = SentimentAnalyzer()
    
    # Test data with known labels
    test_data = [
        ("This product is absolutely amazing! Best purchase ever!", "positive"),
        ("Great quality and excellent customer service.", "positive"),
        ("Perfect product, exactly as described.", "positive"),
        ("Love it! Highly recommend to everyone.", "positive"),
        ("Outstanding quality and fast shipping.", "positive"),
        ("Fantastic product, exceeded my expectations.", "positive"),
        ("It's okay, nothing special about it.", "neutral"),
        ("Average product, meets basic expectations.", "neutral"),
        ("Decent quality, could be better.", "neutral"),
        ("It works fine, nothing extraordinary.", "neutral"),
        ("Standard product, does the job.", "neutral"),
        ("Meets expectations but nothing more.", "neutral"),
        ("Terrible product, complete waste of money!", "negative"),
        ("Awful quality, broke after one day.", "negative"),
        ("Worst purchase ever, avoid this seller.", "negative"),
        ("Poor quality and terrible customer service.", "negative"),
        ("Disappointed with this product, not worth it.", "negative"),
        ("Cheap materials, very poor build quality.", "negative")
    ]
    
    # Separate text and labels
    test_texts = [item[0] for item in test_data]
    true_labels = [item[1] for item in test_data]
    
    # Get predictions
    predictions = []
    for text in test_texts:
        sentiment = analyzer.analyze_single_review(text)
        predictions.append(sentiment)
    
    # Calculate accuracy
    accuracy = accuracy_score(true_labels, predictions)
    
    print(f"Test Dataset Size: {len(test_data)} samples")
    print(f"Model Accuracy: {accuracy:.2%}")
    print()
    
    # Detailed classification report
    print("Classification Report:")
    print(classification_report(true_labels, predictions))
    
    # Confusion matrix
    print("Confusion Matrix:")
    cm = confusion_matrix(true_labels, predictions, labels=['positive', 'neutral', 'negative'])
    print("                 Predicted")
    print("                 Pos  Neu  Neg")
    print(f"Actual Positive {cm[0][0]:4d} {cm[0][1]:4d} {cm[0][2]:4d}")
    print(f"Actual Neutral  {cm[1][0]:4d} {cm[1][1]:4d} {cm[1][2]:4d}")
    print(f"Actual Negative {cm[2][0]:4d} {cm[2][1]:4d} {cm[2][2]:4d}")
    
    return accuracy

def test_trust_scoring_accuracy():
    """Test the consistency and accuracy of trust scoring"""
    print("\n" + "=" * 60)
    print("TRUST SCORING ACCURACY TEST")
    print("=" * 60)
    
    scorer = TrustScorer()
    
    # Test scenarios with expected trust levels
    test_scenarios = [
        {
            "name": "High Trust Amazon Product",
            "product_data": {
                "title": "Premium Quality Product",
                "price": "$99.99",
                "rating": "4.8",
                "review_count": "1250",
                "seller": "Amazon Official Store",
                "reviews": [
                    {"text": "Excellent product, highly recommend!", "rating": "5"},
                    {"text": "Great quality and fast shipping", "rating": "5"},
                    {"text": "Perfect, exactly as described", "rating": "5"}
                ],
                "platform": "amazon"
            },
            "sentiment": {"sentiment_score": 0.8, "positive": 3, "neutral": 0, "negative": 0},
            "expected_range": (80, 95)
        },
        {
            "name": "Medium Trust Daraz Product",
            "product_data": {
                "title": "Decent Quality Item",
                "price": "₹599",
                "rating": "3.5",
                "review_count": "45",
                "seller": "Local Seller",
                "reviews": [
                    {"text": "Good for the price", "rating": "4"},
                    {"text": "Average quality", "rating": "3"},
                    {"text": "Works fine", "rating": "3"}
                ],
                "platform": "daraz"
            },
            "sentiment": {"sentiment_score": 0.2, "positive": 1, "neutral": 2, "negative": 0},
            "expected_range": (50, 70)
        },
        {
            "name": "Low Trust Suspicious Product",
            "product_data": {
                "title": "Super Cheap Item",
                "price": "$0.99",
                "rating": "1.2",
                "review_count": "5",
                "seller": "Unknown Seller",
                "reviews": [
                    {"text": "Terrible quality", "rating": "1"},
                    {"text": "Complete scam", "rating": "1"},
                    {"text": "Waste of money", "rating": "1"}
                ],
                "platform": "generic"
            },
            "sentiment": {"sentiment_score": -0.8, "positive": 0, "neutral": 0, "negative": 3},
            "expected_range": (10, 30)
        }
    ]
    
    correct_predictions = 0
    
    for scenario in test_scenarios:
        trust_result = scorer.calculate_trust_score(scenario["product_data"], scenario["sentiment"])
        trust_score = trust_result['overall_score']
        expected_min, expected_max = scenario["expected_range"]
        
        is_correct = expected_min <= trust_score <= expected_max
        if is_correct:
            correct_predictions += 1
        
        print(f"{scenario['name']}:")
        print(f"  Trust Score: {trust_score:.1f}% (Expected: {expected_min}-{expected_max}%)")
        print(f"  Prediction: {'CORRECT' if is_correct else 'INCORRECT'}")
        print()
    
    trust_accuracy = correct_predictions / len(test_scenarios)
    print(f"Trust Scoring Accuracy: {trust_accuracy:.2%} ({correct_predictions}/{len(test_scenarios)} correct)")
    
    return trust_accuracy

def test_scraper_accuracy():
    """Test the accuracy of platform detection and data extraction"""
    print("\n" + "=" * 60)
    print("WEB SCRAPER ACCURACY TEST")
    print("=" * 60)
    
    scraper = ProductScraper()
    
    # Test platform detection
    test_urls = [
        ("https://amazon.com/product", "amazon"),
        ("https://www.amazon.in/product", "amazon"),
        ("https://daraz.pk/product", "daraz"),
        ("https://www.daraz.com.bd/product", "daraz"),
        ("https://ebay.com/product", "ebay"),
        ("https://www.ebay.co.uk/product", "ebay"),
        ("https://aliexpress.com/product", "aliexpress"),
        ("https://unknown-shop.com/product", "generic")
    ]
    
    correct_detections = 0
    
    print("Platform Detection Test:")
    for url, expected_platform in test_urls:
        detected_platform = scraper.detect_platform(url)
        is_correct = detected_platform == expected_platform
        if is_correct:
            correct_detections += 1
        
        print(f"  {url}")
        print(f"    Expected: {expected_platform}, Detected: {detected_platform} {'CORRECT' if is_correct else 'INCORRECT'}")
    
    detection_accuracy = correct_detections / len(test_urls)
    print(f"\nPlatform Detection Accuracy: {detection_accuracy:.2%} ({correct_detections}/{len(test_urls)} correct)")
    
    return detection_accuracy

def overall_system_accuracy():
    """Calculate overall system accuracy"""
    print("\n" + "=" * 60)
    print("OVERALL SYSTEM ACCURACY")
    print("=" * 60)
    
    # Run all accuracy tests
    sentiment_acc = test_sentiment_model_accuracy()
    trust_acc = test_trust_scoring_accuracy()
    scraper_acc = test_scraper_accuracy()
    
    # Calculate weighted average (sentiment analysis is most important)
    overall_acc = (sentiment_acc * 0.5) + (trust_acc * 0.3) + (scraper_acc * 0.2)
    
    print("\n" + "=" * 60)
    print("ACCURACY SUMMARY")
    print("=" * 60)
    print(f"Sentiment Analysis Accuracy: {sentiment_acc:.2%}")
    print(f"Trust Scoring Accuracy:     {trust_acc:.2%}")
    print(f"Platform Detection Accuracy: {scraper_acc:.2%}")
    print("-" * 40)
    print(f"OVERALL SYSTEM ACCURACY:    {overall_acc:.2%}")
    
    # Accuracy rating
    if overall_acc >= 0.9:
        rating = "EXCELLENT"
    elif overall_acc >= 0.8:
        rating = "VERY GOOD"
    elif overall_acc >= 0.7:
        rating = "GOOD"
    elif overall_acc >= 0.6:
        rating = "FAIR"
    else:
        rating = "NEEDS IMPROVEMENT"
    
    print(f"System Rating: {rating}")
    
    return overall_acc

if __name__ == "__main__":
    overall_system_accuracy()
