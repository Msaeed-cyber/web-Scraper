import re
import math
from typing import Dict, Any, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TrustScorer:
    def __init__(self):
        self._last_component_scores = {}
        self._last_overall_score = 50.0
        self.suspicious_keywords = [
            'fake', 'scam', 'fraud', 'counterfeit', 'knockoff', 'replica',
            'cheap quality', 'waste of money', 'terrible', 'awful',
            'don\'t buy', 'avoid', 'regret', 'disappointed', 'ripoff'
        ]
        
        self.trusted_keywords = [
            'genuine', 'authentic', 'original', 'high quality', 'excellent',
            'recommend', 'love it', 'perfect', 'amazing', 'great value',
            'fast shipping', 'good customer service', 'exactly as described'
        ]
        
        self.trusted_domains = [
            # Major global platforms
            'amazon.com', 'amazon.in', 'amazon.co.uk', 'amazon.de',
            'ebay.com', 'ebay.co.uk', 'ebay.de',
            'walmart.com', 'target.com', 'bestbuy.com',
            'homedepot.com', 'costco.com', 'macys.com', 'nordstrom.com',
            
            # Asian platforms
            'daraz.pk', 'daraz.com.bd', 'flipkart.com', 'myntra.com',
            'ajio.com', 'nykaa.com', 'bigbasket.com',
            
            # Chinese platforms
            'aliexpress.com', 'taobao.com', 'tmall.com', 'jd.com',
            
            # European platforms
            'zalando.com', 'otto.de', 'cdiscount.com', 'fnac.com',
            
            # Fashion platforms
            'asos.com', 'hm.com', 'zara.com', 'uniqlo.com',
            
            # Tech platforms
            'newegg.com', 'bhphotovideo.com', 'adorama.com',
            
            # Premium marketplaces
            'etsy.com', 'mercadolibre.com'
        ]
        
        self.suspicious_domains = [
            # Known problematic platforms
            'temu.com', 'wish.com', 'pinduoduo.com',
            
            # Generic suspicious patterns
            'cheap-deals.com', 'super-discount.com', 'mega-sale.com'
        ]
        
        self.medium_trust_domains = [
            # Fashion platforms with mixed reputation
            'shein.com', 'zaful.com', 'romwe.com',
            
            # Local marketplaces
            'shopify.com', 'woocommerce.com', 'magento.com',
            
            # Electronics brands
            'dell.com', 'hp.com', 'lenovo.com', 'samsung.com'
        ]
    
    def calculate_domain_trust_score(self, url):
        """Calculate trust score based on domain reputation"""
        from urllib.parse import urlparse
        
        domain = urlparse(url).netloc.lower()
        
        # Remove www prefix
        if domain.startswith('www.'):
            domain = domain[4:]
        
        # High trust domains (major established platforms)
        if domain in self.trusted_domains:
            return 0.95  # Very high trust for established platforms
        
        # Medium trust domains (known but with mixed reputation)
        elif domain in self.medium_trust_domains:
            return 0.75  # Medium-high trust
        
        # Suspicious domains (known problematic platforms)
        elif domain in self.suspicious_domains:
            return 0.15  # Very low trust
        
        # Check for common e-commerce patterns and provide varied scores
        else:
            if any(pattern in domain for pattern in ['shop', 'store', 'mall', 'buy']):
                return 0.7  # Medium-high trust for e-commerce sites
            elif any(pattern in domain for pattern in ['marketplace', 'market', 'trade']):
                return 0.6  # Medium trust for marketplaces
            elif any(pattern in domain for pattern in ['deal', 'discount', 'sale', 'cheap']):
                return 0.4  # Lower trust for discount sites
            elif any(pattern in domain for pattern in ['official', 'brand', 'company']):
                return 0.8  # High trust for official brand sites
            else:
                return 0.5  # Default trust for unknown domains
    
    def calculate_review_quality_score(self, reviews):
        """Calculate quality score based on review characteristics"""
        if not reviews:
            return 0.0
        
        quality_score = 0.0
        total_reviews = len(reviews)
        
        # Check for review length and detail
        detailed_reviews = 0
        for review in reviews:
            if isinstance(review, dict):
                text = review.get('text', '')
            else:
                text = str(review)
            
            if len(text) > 50:  # Detailed reviews
                detailed_reviews += 1
        
        # Reward detailed reviews
        if total_reviews > 0:
            detail_ratio = detailed_reviews / total_reviews
            quality_score += detail_ratio * 0.3
        
        # Check for suspicious patterns
        suspicious_patterns = 0
        for review in reviews:
            if isinstance(review, dict):
                text = review.get('text', '').lower()
            else:
                text = str(review).lower()
            
            # Check for repetitive content
            if len(set(text.split())) < 5:  # Very short reviews
                suspicious_patterns += 1
            
            # Check for suspicious keywords
            if any(keyword in text for keyword in self.suspicious_keywords):
                suspicious_patterns += 1
        
        if total_reviews > 0:
            suspicious_ratio = suspicious_patterns / total_reviews
            quality_score -= suspicious_ratio * 0.4
        
        return max(0.0, min(1.0, quality_score))
    
    def calculate_rating_consistency_score(self, rating, review_count, sentiment_score):
        """Calculate consistency score between rating and sentiment"""
        if not rating or rating == "N/A" or not review_count:
            return 0.5
        
        try:
            rating_value = float(rating)
            review_count_value = int(review_count)
            
            # Normalize rating to 0-1 scale (assuming 5-star scale)
            normalized_rating = rating_value / 5.0
            
            # Convert sentiment score from -1 to 1 scale to 0-1 scale
            normalized_sentiment = (sentiment_score + 1) / 2
            
            # Calculate consistency
            consistency = 1.0 - abs(normalized_rating - normalized_sentiment)
            
            # Bonus for high review count
            if review_count_value > 100:
                consistency += 0.1
            elif review_count_value > 50:
                consistency += 0.05
            
            return max(0.0, min(1.0, consistency))
            
        except (ValueError, TypeError):
            return 0.5
    
    def calculate_seller_reputation_score(self, seller):
        """Calculate seller reputation score"""
        if not seller or seller == "Unknown":
            return 0.5
        
        # Check for suspicious seller names
        suspicious_seller_patterns = [
            'store', 'shop', 'seller', 'dealer', 'wholesale',
            'cheap', 'discount', 'outlet'
        ]
        
        seller_lower = seller.lower()
        
        # Penalize generic seller names
        if any(pattern in seller_lower for pattern in suspicious_seller_patterns):
            return 0.3
        
        # Reward branded sellers
        if any(pattern in seller_lower for pattern in ['official', 'brand', 'authorized']):
            return 0.8
        
        # Default score for regular sellers
        return 0.6
    
    def calculate_price_reasonableness_score(self, price, title):
        """Calculate if price seems reasonable for the product"""
        if not price or price == "Price not available":
            return 0.5
        
        try:
            # Extract numeric price
            price_match = re.search(r'[\d,]+\.?\d*', price.replace(',', ''))
            if not price_match:
                return 0.5
            
            price_value = float(price_match.group())
            
            # Check for extremely low prices (potential red flag)
            if price_value < 1:
                return 0.2
            
            # Check for extremely high prices (might be legitimate luxury items)
            if price_value > 10000:
                return 0.7
            
            # Normal range
            return 0.8
            
        except (ValueError, TypeError):
            return 0.5
    
    def calculate_trust_score(self, product_data, sentiment_data, domain=None):
        """Calculate overall trust score"""
        try:
            # Get individual component scores
            domain_score = self.calculate_domain_trust_score(product_data.get('url', ''))
            review_quality_score = self.calculate_review_quality_score(product_data.get('reviews', []))
            rating_consistency_score = self.calculate_rating_consistency_score(
                product_data.get('rating'), 
                product_data.get('review_count'), 
                sentiment_data.get('sentiment_score', 0)
            )
            seller_score = self.calculate_seller_reputation_score(product_data.get('seller'))
            price_score = self.calculate_price_reasonableness_score(
                product_data.get('price'), 
                product_data.get('title')
            )
            
            # Store component scores for get_score_components method
            self._last_component_scores = {
                'domain': round(domain_score, 2),
                'review_quality': round(review_quality_score, 2),
                'rating_consistency': round(rating_consistency_score, 2),
                'seller': round(seller_score, 2),
                'price': round(price_score, 2)
            }
            
            # Weighted combination
            weights = {
                'domain': 0.25,
                'review_quality': 0.25,
                'rating_consistency': 0.20,
                'seller': 0.15,
                'price': 0.15
            }
            
            overall_score = (
                domain_score * weights['domain'] +
                review_quality_score * weights['review_quality'] +
                rating_consistency_score * weights['rating_consistency'] +
                seller_score * weights['seller'] +
                price_score * weights['price']
            )
            
            # Adjust based on sentiment
            sentiment_adjustment = sentiment_data.get('sentiment_score', 0) * 0.1
            overall_score += sentiment_adjustment
            
            # Ensure score is between 0 and 1
            overall_score = max(0.0, min(1.0, overall_score))
            
            logger.info(f"Trust score components: domain={domain_score:.2f}, "
                       f"review_quality={review_quality_score:.2f}, "
                       f"rating_consistency={rating_consistency_score:.2f}, "
                       f"seller={seller_score:.2f}, price={price_score:.2f}")
            logger.info(f"Overall trust score: {overall_score:.2f}")
            
            # Store overall score
            self._last_overall_score = round(overall_score * 100, 1)
            
            return {
                'overall_score': self._last_overall_score,  # Keep overall score as percentage for UI
                'component_scores': self._last_component_scores  # Component scores as 0-1 floats for tests
            }
            
        except Exception as e:
            logger.error(f"Error calculating trust score: {e}")
            return {
                'overall_score': 50.0,
                'component_scores': {
                    'domain': 0.5,
                    'review_quality': 0.5,
                    'rating_consistency': 0.5,
                    'seller': 0.5,
                    'price': 0.5
                }
            }
    
    def get_score_components(self):
        """Return the score components from the last calculation"""
        return self._last_component_scores
    
    def get_last_score(self):
        """Return the overall score from the last calculation"""
        return self._last_overall_score
    
    def generate_recommendation(self, trust_score):
        """Generate recommendation based on trust score"""
        score = trust_score.get('overall_score', 50)
        
        if score >= 80:
            return {
                'action': 'Buy',
                'confidence': 'High',
                'message': 'This product appears to be trustworthy with high ratings and genuine reviews.',
                'color': 'success'
            }
        elif score >= 60:
            return {
                'action': 'Be Careful',
                'confidence': 'Medium',
                'message': 'This product has mixed signals. Consider reading more reviews before purchasing.',
                'color': 'warning'
            }
        else:
            return {
                'action': 'Avoid',
                'confidence': 'High',
                'message': 'This product shows signs of being potentially fraudulent or low quality.',
                'color': 'danger'
            }
