from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from urllib.parse import urlparse
import re
import traceback
import logging
from backend.scraper import ProductScraper
from backend.sentiment_analyzer import SentimentAnalyzer
from backend.trust_scorer import TrustScorer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Set explicit template and static folders to match project structure
app = Flask(__name__, template_folder=os.path.join(os.path.dirname(__file__), 'frontend', 'templates'), static_folder=os.path.join(os.path.dirname(__file__), 'frontend', 'static'))
CORS(app)

# Initialize components
scraper = ProductScraper()
sentiment_analyzer = SentimentAnalyzer()
trust_scorer = TrustScorer()

@app.route('/')
def index():
    return render_template('index.html')

def validate_url(url):
    """Validate URL format and domain"""
    try:
        if not url or not isinstance(url, str):
            return False, "URL is required and must be a string"
            
        # Basic format validation
        parsed = urlparse(url)
        
        # Scheme validation
        if not parsed.scheme:
            return False, "Missing URL scheme (http/https)"
        if parsed.scheme not in ['http', 'https']:
            return False, "URL must use HTTP or HTTPS"
            
        # Netloc (domain) validation
        if not parsed.netloc:
            return False, "Missing domain name"
            
        # Domain parts validation
        domain_parts = parsed.netloc.split('.')
        if len(domain_parts) < 2:  # Must have at least two parts (domain + TLD)
            return False, "Invalid domain format: must have at least a domain and TLD"
            
        # Check for empty parts
        if '' in domain_parts:
            return False, "Invalid domain format: contains empty parts"
            
        # Domain format validation
        for part in domain_parts:
            # Each part must:
            # - Start with alphanumeric
            # - Can contain hyphens in middle
            # - End with alphanumeric
            # - Not be all numeric (to prevent IP-like domains)
            if not re.match(r'^[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?$', part) or part.isdigit():
                return False, "Invalid domain format: invalid characters or format"
        
        # Path validation (optional)
        if parsed.path not in ['', '/'] and not re.match(r'^/[\w\-\.~!$&\'()*+,;=:@/%]*$', parsed.path):
            return False, "Invalid URL path format"
                
        return True, None
        
    except Exception as e:
        logger.error(f"URL validation error: {str(e)}")
        return False, "Invalid URL format"

@app.route('/analyze', methods=['POST'])
def analyze_product():
    """Analyze product URL for trust and sentiment"""
    try:
        # Get and validate request data
        data = request.get_json()
        if not data:
            return jsonify({'error': 'URL is required'}), 400
            
        product_url = data.get('url')
        if not product_url:
            return jsonify({'error': 'URL is required'}), 400
            
        # Validate URL format
        is_valid, error_msg = validate_url(product_url)
        if not is_valid:
            return jsonify({'error': error_msg}), 400
            
        # Parse URL for domain info
        parsed = urlparse(product_url)
        
        try:
            # Step 1: Scrape product data
            product_data = scraper.scrape_product(product_url)
            
            if not product_data:
                logger.warning(f"Failed to scrape product data, using fallback for {parsed.netloc}")
                product_data = scraper.fallback_data.get('generic', {
                    'title': 'Unknown Product',
                    'price': '$0.00',
                    'rating': 0.0,
                    'review_count': 0,
                    'reviews': []
                })
            
            # Step 2: Analyze sentiment
            sentiment_results = sentiment_analyzer.analyze_reviews(product_data.get('reviews', []))
            
            # Step 3: Calculate trust score
            trust_score = trust_scorer.calculate_trust_score(
                product_data=product_data,
                sentiment_data=sentiment_results,
                domain=parsed.netloc
            )
            
            # Step 4: Generate recommendation
            recommendation = trust_scorer.generate_recommendation(trust_score)
            
            # Step 5: Prepare response
            response = {
                'product_info': product_data,
                'sentiment_analysis': sentiment_results,
                'trust_score': trust_score['overall_score'] / 100.0,  # Convert percentage to 0-1 scale
                'trust_score_components': trust_scorer.get_score_components(),
                'recommendation': recommendation
            }
            
            return jsonify(response), 200
            
        except Exception as e:
            logger.error(f"Processing error: {str(e)}\n{traceback.format_exc()}")
            return jsonify({
                'error': 'Internal processing error',
                'details': str(e),
                'product_info': scraper.fallback_data.get('generic'),
                'sentiment_analysis': {'positive': 0, 'neutral': 0, 'negative': 0},
                'trust_score': 0.0,
                'recommendation': 'Unable to analyze product'
            }), 200
            
    except Exception as e:
        logger.error(f"Request error: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': 'Invalid request'}), 400
        
        result = {
            'product_info': {
                'title': product_data['title'],
                'price': product_data['price'],
                'rating': product_data['rating'],
                'review_count': product_data['review_count'],
                'seller': product_data['seller']
            },
            'sentiment_analysis': sentiment_results,
            'trust_score': trust_score,
            'recommendation': recommendation
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000, use_reloader=False)
