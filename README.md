# AI-Powered Product Trust & Sentiment Analyzer

An intelligent web application that analyzes the trustworthiness, sentiment, and authenticity of online products using advanced AI and machine learning techniques.

## 🚀 Features

- **Multi-Platform Support**: Works with Amazon, Daraz, eBay, AliExpress, and other e-commerce sites
- **AI Sentiment Analysis**: Uses machine learning to analyze customer reviews and determine sentiment
- **Trust Scoring**: Calculates comprehensive trust scores based on multiple factors
- **Real-time Analysis**: Fast and accurate product analysis with detailed reports
- **Beautiful UI**: Modern, responsive web interface with Bootstrap 5
- **Detailed Insights**: Component-wise trust breakdown and recommendations

## 🛠️ Tech Stack

- **Backend**: Python, Flask
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Machine Learning**: Scikit-learn, TextBlob, NLTK
- **Web Scraping**: BeautifulSoup, Selenium, Requests
- **Data Processing**: Pandas, NumPy
- **Database**: SQLite (for model storage)

## 📋 Prerequisites

- Python 3.8 or higher
- Chrome browser (for Selenium web scraping)
- ChromeDriver (automatically managed by Selenium)

## 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd AI-sentiment-web-scraping
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Download NLTK data** (if needed)
   ```bash
   python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
   ```

## 🎯 Usage

1. **Start the application**
   ```bash
   python app.py
   ```

2. **Open your browser**
   Navigate to `http://localhost:5000`

3. **Analyze a product**
   - Enter any product URL from supported e-commerce platforms
   - Click "Analyze Product"
   - View detailed trust score, sentiment analysis, and recommendations

## 📊 How It Works

### 1. Data Collection
- **Web Scraping**: Automatically extracts product information, reviews, ratings, and seller details
- **Multi-Platform**: Supports different e-commerce platforms with platform-specific scraping logic

### 2. Sentiment Analysis
- **Machine Learning Model**: Trained on product review data using Logistic Regression
- **Text Processing**: Uses TF-IDF vectorization and natural language processing
- **Sentiment Classification**: Categorizes reviews as Positive, Neutral, or Negative

### 3. Trust Scoring
The system calculates trust scores based on multiple factors:

- **Domain Trust** (25%): Reputation of the e-commerce platform
- **Review Quality** (25%): Analysis of review authenticity and detail
- **Rating Consistency** (20%): Alignment between ratings and sentiment
- **Seller Reputation** (15%): Seller information and credibility
- **Price Reasonableness** (15%): Price analysis for potential red flags

### 4. Recommendations
Based on the trust score:
- **80-100%**: "Buy" - High confidence, trustworthy product
- **60-79%**: "Be Careful" - Mixed signals, requires more research
- **0-59%**: "Avoid" - Potential fraud or low quality

## 🔧 Configuration

Create a `.env` file in the root directory:
```env
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key-here
```

## 📁 Project Structure

```
AI-sentiment-web-scraping/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
├── backend/              # Backend modules
│   ├── __init__.py
│   ├── scraper.py        # Web scraping logic
│   ├── sentiment_analyzer.py  # ML sentiment analysis
│   └── trust_scorer.py   # Trust scoring algorithm
├── templates/            # HTML templates
│   └── index.html        # Main web interface
├── static/               # Static files
│   ├── css/
│   │   └── style.css     # Custom styles
│   └── js/
│       └── app.js        # Frontend JavaScript
└── models/               # Trained ML models (auto-generated)
```

## 🧪 Supported Platforms

- **Amazon** (.com, .in, etc.)
- **Daraz** (.pk, .com.bd, etc.)
- **eBay**
- **AliExpress**
- **Generic e-commerce sites** (basic scraping)

## 🔍 Example Analysis

Input: `https://amazon.com/product-link`

Output:
- **Trust Score**: 85%
- **Recommendation**: Buy
- **Sentiment**: 78% Positive, 15% Neutral, 7% Negative
- **Components**:
  - Domain Trust: 90%
  - Review Quality: 85%
  - Rating Consistency: 80%
  - Seller Reputation: 85%
  - Price Reasonableness: 90%

## 🚨 Important Notes

- **Rate Limiting**: The scraper includes delays to respect website terms of service
- **Legal Compliance**: Ensure you comply with robots.txt and terms of service
- **Model Training**: The sentiment model is trained on sample data; for production, use larger datasets
- **ChromeDriver**: Selenium requires ChromeDriver; it's automatically managed but ensure Chrome is installed

## 🛡️ Ethical Considerations

- **Respect robots.txt**: Always check and respect website crawling policies
- **Rate Limiting**: Implement appropriate delays between requests
- **User Privacy**: No personal data is stored or transmitted
- **Fair Use**: Use the tool responsibly and ethically

## 🔮 Future Enhancements

- [ ] Support for more e-commerce platforms
- [ ] Social media sentiment analysis (Twitter, Reddit)
- [ ] Price history tracking
- [ ] Advanced fraud detection
- [ ] API endpoints for integration
- [ ] Mobile app development
- [ ] Real-time monitoring and alerts

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Scikit-learn community for ML tools
- BeautifulSoup and Selenium for web scraping
- Bootstrap for the beautiful UI framework
- NLTK and TextBlob for natural language processing

## 📞 Support

For questions, issues, or contributions, please open an issue on the GitHub repository.

---

**Disclaimer**: This tool is for educational and research purposes. Always verify information independently and use responsibly.
