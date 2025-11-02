import re
import numpy as np
import pandas as pd
from textblob import TextBlob
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import pickle
import os
import logging
from typing import Dict, List, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    def __init__(self):
        self.model = None
        self.vectorizer = None
        self.model_path = 'models/sentiment_model.pkl'
        self.vectorizer_path = 'models/tfidf_vectorizer.pkl'
        
        # Create models directory if it doesn't exist
        os.makedirs('models', exist_ok=True)
        
        # Load or train model
        self._load_or_train_model()
    
    def _load_or_train_model(self):
        """Load existing model or train a new one"""
        try:
            if os.path.exists(self.model_path) and os.path.exists(self.vectorizer_path):
                logger.info("Loading existing sentiment model...")
                with open(self.model_path, 'rb') as f:
                    self.model = pickle.load(f)
                with open(self.vectorizer_path, 'rb') as f:
                    self.vectorizer = pickle.load(f)
            else:
                logger.info("Training new sentiment model...")
                self._train_model()
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            self._train_model()
    
    def _train_model(self):
        """Train a sentiment analysis model using sample data"""
        # Expanded training data with more variety and better examples
        sample_data = [
            # Positive reviews - Clear positive sentiment
            ("This product is amazing! Highly recommend it.", "positive"),
            ("Great quality and fast shipping.", "positive"),
            ("Perfect product, exactly as described.", "positive"),
            ("Excellent value for money.", "positive"),
            ("Love it! Will buy again.", "positive"),
            ("Good product overall.", "positive"),
            ("Fantastic quality, exceeded expectations.", "positive"),
            ("Best purchase I've made this year.", "positive"),
            ("Outstanding product and service.", "positive"),
            ("Highly satisfied with this purchase.", "positive"),
            ("Works perfectly, no complaints.", "positive"),
            ("Great deal, fast delivery.", "positive"),
            ("Amazing product, will definitely buy again.", "positive"),
            ("Superb quality and design.", "positive"),
            ("Excellent customer service and product.", "positive"),
            ("Wonderful product, very happy with purchase.", "positive"),
            ("Top quality item, highly recommended.", "positive"),
            ("Fantastic value, great quality.", "positive"),
            ("Impressed with the quality and service.", "positive"),
            ("Brilliant product, works exactly as expected.", "positive"),
            ("Very pleased with this purchase.", "positive"),
            ("Excellent product, fast shipping.", "positive"),
            ("Great quality, would buy again.", "positive"),
            ("Perfect fit and great quality.", "positive"),
            ("Outstanding value for money.", "positive"),
            
            # Neutral reviews - Clear neutral sentiment
            ("It's okay, nothing special.", "neutral"),
            ("Average quality product.", "neutral"),
            ("Not bad, but could be better.", "neutral"),
            ("It's fine, does the job.", "neutral"),
            ("Meets expectations.", "neutral"),
            ("Decent product.", "neutral"),
            ("Standard quality, nothing extraordinary.", "neutral"),
            ("It works as expected.", "neutral"),
            ("Average product for the price.", "neutral"),
            ("Nothing wrong with it, but nothing special.", "neutral"),
            ("It's a decent product.", "neutral"),
            ("Works fine, could be better.", "neutral"),
            ("Average experience overall.", "neutral"),
            ("It does what it's supposed to do.", "neutral"),
            ("Standard quality product.", "neutral"),
            ("Fair quality for the price.", "neutral"),
            ("It's acceptable, nothing more.", "neutral"),
            ("Average build quality.", "neutral"),
            ("Does the job adequately.", "neutral"),
            ("Neither good nor bad.", "neutral"),
            ("Standard fare.", "neutral"),
            ("It's functional.", "neutral"),
            ("Mediocre quality.", "neutral"),
            ("Average performance.", "neutral"),
            ("It's okay.", "neutral"),
            
            # Negative reviews - Clear negative sentiment
            ("Terrible quality, waste of money.", "negative"),
            ("Don't buy this, it's a scam.", "negative"),
            ("Poor quality, broke after one day.", "negative"),
            ("Worst purchase ever.", "negative"),
            ("Completely disappointed.", "negative"),
            ("Overpriced and low quality.", "negative"),
            ("Fake product, not as advertised.", "negative"),
            ("Avoid this seller at all costs.", "negative"),
            ("This is junk, don't waste your money.", "negative"),
            ("Very poor customer service.", "negative"),
            ("Product arrived damaged.", "negative"),
            ("Not worth the price.", "negative"),
            ("Regret buying this item.", "negative"),
            ("Awful product, avoid at all costs.", "negative"),
            ("Cheap quality, breaks easily.", "negative"),
            ("Waste of money, very disappointed.", "negative"),
            ("Poor quality control.", "negative"),
            ("Defective product, bad experience.", "negative"),
            ("Terrible shipping and product quality.", "negative"),
            ("Not recommended, poor value.", "negative"),
            ("Disappointing purchase experience.", "negative"),
            ("Low quality materials used.", "negative"),
            ("Product doesn't work as described.", "negative"),
            ("Very poor build quality.", "negative"),
            ("Not worth buying, poor design.", "negative"),
            ("Horrible product, complete waste.", "negative"),
            ("Useless item, doesn't work.", "negative"),
            ("Extremely disappointed with quality.", "negative"),
            ("Bad experience, avoid this.", "negative"),
            ("Poor value, not recommended.", "negative"),
            ("Inferior quality product.", "negative"),
            ("Failed to meet expectations.", "negative"),
            ("Substandard materials used.", "negative"),
            ("Doesn't work as advertised.", "negative"),
            ("Poor construction quality.", "negative"),
            ("Worst product I've ever bought.", "negative")
        ]
        
        # Convert to DataFrame
        df = pd.DataFrame(sample_data, columns=['text', 'sentiment'])
        
        # Prepare features and labels
        X = df['text']
        y = df['sentiment']
        
        # Create TF-IDF vectorizer
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2),
            min_df=1
        )
        
        # Transform text to features
        X_tfidf = self.vectorizer.fit_transform(X)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_tfidf, y, test_size=0.2, random_state=42
        )
        
        # Train model
        self.model = LogisticRegression(random_state=42, max_iter=1000)
        self.model.fit(X_train, y_train)
        
        # Evaluate model
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        logger.info(f"Model accuracy: {accuracy:.2f}")
        
        # Save model
        with open(self.model_path, 'wb') as f:
            pickle.dump(self.model, f)
        with open(self.vectorizer_path, 'wb') as f:
            pickle.dump(self.vectorizer, f)
        
        logger.info("Model trained and saved successfully")
    
    def _preprocess_text(self, text):
        """Preprocess text for sentiment analysis"""
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters and digits
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _get_textblob_sentiment(self, text):
        """Get sentiment using TextBlob"""
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            
            if polarity > 0.1:
                return 'positive'
            elif polarity < -0.1:
                return 'negative'
            else:
                return 'neutral'
        except:
            return 'neutral'
    
    def _get_ml_sentiment(self, text):
        """Get sentiment using trained ML model"""
        try:
            if not self.model or not self.vectorizer:
                return self._get_textblob_sentiment(text)
            
            # Preprocess text
            processed_text = self._preprocess_text(text)
            
            # Transform text
            text_vector = self.vectorizer.transform([processed_text])
            
            # Predict sentiment
            prediction = self.model.predict(text_vector)[0]
            
            return prediction
        except Exception as e:
            logger.warning(f"Error in ML sentiment analysis: {e}")
            return self._get_textblob_sentiment(text)
    
    def analyze_single_review(self, review_text):
        """Analyze sentiment of a single review"""
        if not review_text or not review_text.strip():
            return 'neutral'
        
        # Use both methods for better accuracy
        ml_sentiment = self._get_ml_sentiment(review_text)
        textblob_sentiment = self._get_textblob_sentiment(review_text)
        
        # Combine results (prefer ML model, fallback to TextBlob)
        return ml_sentiment
    
    def analyze_reviews(self, reviews):
        """Analyze sentiment of multiple reviews"""
        if not reviews:
            return {
                'positive': 0,
                'neutral': 0,
                'negative': 0,
                'total_reviews': 0,
                'sentiment_score': 0.0,
                'detailed_sentiments': []
            }
        
        sentiments = []
        detailed_sentiments = []
        
        for review in reviews:
            if isinstance(review, dict):
                review_text = review.get('text', '')
            else:
                review_text = str(review)
            
            sentiment = self.analyze_single_review(review_text)
            sentiments.append(sentiment)
            
            detailed_sentiments.append({
                'text': review_text[:100] + '...' if len(review_text) > 100 else review_text,
                'sentiment': sentiment
            })
        
        # Count sentiments
        positive_count = sentiments.count('positive')
        neutral_count = sentiments.count('neutral')
        negative_count = sentiments.count('negative')
        total_count = len(sentiments)
        
        # Calculate sentiment score (-1 to 1, where 1 is most positive)
        if total_count > 0:
            sentiment_score = (positive_count - negative_count) / total_count
        else:
            sentiment_score = 0.0
        
        return {
            'positive': positive_count,
            'neutral': neutral_count,
            'negative': negative_count,
            'total_reviews': total_count,
            'sentiment_score': sentiment_score,
            'detailed_sentiments': detailed_sentiments[:5]  # Return first 5 detailed sentiments
        }
