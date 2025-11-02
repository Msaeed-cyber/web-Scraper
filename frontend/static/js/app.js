// AI Product Trust Analyzer - Frontend JavaScript

document.addEventListener('DOMContentLoaded', function() {
    const analyzeForm = document.getElementById('analyzeForm');
    const productUrlInput = document.getElementById('productUrl');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const resultsSection = document.getElementById('resultsSection');
    const errorAlert = document.getElementById('errorAlert');
    const errorMessage = document.getElementById('errorMessage');

    // Form submission handler
    analyzeForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const url = productUrlInput.value.trim();
        
        if (!url) {
            showError('Please enter a product URL');
            return;
        }

        if (!isValidUrl(url)) {
            showError('Please enter a valid URL');
            return;
        }

        await analyzeProduct(url);
    });

    // Analyze product function
    async function analyzeProduct(url) {
        try {
            showLoading(true);
            hideError();
            hideResults();

            const response = await fetch('/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ url: url })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Analysis failed');
            }

            displayResults(data);

        } catch (error) {
            console.error('Error:', error);
            showError(error.message || 'An error occurred while analyzing the product');
        } finally {
            showLoading(false);
        }
    }

    // Display results
    function displayResults(data) {
        displayProductInfo(data.product_info);
        displayTrustScore(data.trust_score, data.recommendation);
        displaySentimentAnalysis(data.sentiment_analysis);

        // Backend returns component scores in `trust_score_components`
        // which is a flat object like { domain: 0.5, review_quality: 0.0, ... }
        displayDetailedScores(data.trust_score_components || {});

        showResults();
    }

    // Display product information
    function displayProductInfo(productInfo) {
        const container = document.getElementById('productInfo');
        
        const platform = productInfo.platform || 'unknown';
        const platformBadge = `<span class="platform-badge ${platform}">${platform}</span>`;

        container.innerHTML = `
            <div class="row">
                <div class="col-md-8">
                    <h6 class="text-muted mb-2">${platformBadge}</h6>
                    <h5 class="mb-3">${productInfo.title || 'Product Title Not Available'}</h5>
                </div>
                <div class="col-md-4 text-md-end">
                    <h4 class="text-primary mb-0">${productInfo.price || 'Price Not Available'}</h4>
                </div>
            </div>
            <div class="row mt-3">
                <div class="col-md-3">
                    <div class="product-info-item">
                        <span class="label">Rating:</span>
                        <span class="value">
                            ${productInfo.rating || 'N/A'}
                            ${productInfo.rating !== 'N/A' ? '<i class="fas fa-star text-warning ms-1"></i>' : ''}
                        </span>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="product-info-item">
                        <span class="label">Reviews:</span>
                        <span class="value">${productInfo.review_count || '0'}</span>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="product-info-item">
                        <span class="label">Seller:</span>
                        <span class="value">${productInfo.seller || 'Unknown'}</span>
                    </div>
                </div>
            </div>
        `;
    }

    // Display trust score
    function displayTrustScore(trustScore, recommendation) {
        const container = document.getElementById('trustScore');

        // Backend may return trustScore as a float (0-1) or an object.
        // Normalize to percentage integer for the UI.
        let scorePercent = 0;
        if (typeof trustScore === 'number') {
            scorePercent = Math.round(trustScore * 100);
        } else if (trustScore && typeof trustScore.overall_score !== 'undefined') {
            // If backend provided the full object (older format)
            scorePercent = Math.round(Number(trustScore.overall_score));
        }

        const circumference = 2 * Math.PI * 60; // radius = 60
        const strokeDasharray = (scorePercent / 100) * circumference;
        const colorClass = getTrustScoreColor(scorePercent);

        container.innerHTML = `
            <div class="trust-score-circle">
                <svg width="150" height="150">
                    <circle class="progress-ring-circle" cx="75" cy="75" r="60"></circle>
                    <circle class="progress-ring-progress ${colorClass}" 
                            cx="75" cy="75" r="60"
                            style="stroke-dasharray: ${strokeDasharray} ${circumference};"></circle>
                </svg>
                <div class="score-text">${scorePercent}%</div>
            </div>
            <div class="recommendation-badge bg-${recommendation && recommendation.color ? recommendation.color : 'secondary'}">
                <i class="fas fa-${getRecommendationIcon((recommendation && recommendation.action) || '')} me-2"></i>
                ${recommendation && recommendation.action ? recommendation.action : 'No Recommendation'}
            </div>
            <p class="mt-3 text-muted">${recommendation && recommendation.message ? recommendation.message : ''}</p>
            <small class="text-muted">${recommendation && recommendation.confidence ? 'Confidence: ' + recommendation.confidence : ''}</small>
        `;
    }

    // Display sentiment analysis
    function displaySentimentAnalysis(sentimentData) {
        const container = document.getElementById('sentimentAnalysis');
        
        const positivePercent = (sentimentData.positive / sentimentData.total_reviews * 100).toFixed(1);
        const neutralPercent = (sentimentData.neutral / sentimentData.total_reviews * 100).toFixed(1);
        const negativePercent = (sentimentData.negative / sentimentData.total_reviews * 100).toFixed(1);

        let sentimentBars = '';
        if (sentimentData.total_reviews > 0) {
            sentimentBars = `
                <div class="sentiment-bar positive" style="width: ${positivePercent}%">
                    <i class="fas fa-thumbs-up me-2"></i>
                    ${sentimentData.positive} Positive (${positivePercent}%)
                </div>
                <div class="sentiment-bar neutral" style="width: ${neutralPercent}%">
                    <i class="fas fa-minus me-2"></i>
                    ${sentimentData.neutral} Neutral (${neutralPercent}%)
                </div>
                <div class="sentiment-bar negative" style="width: ${negativePercent}%">
                    <i class="fas fa-thumbs-down me-2"></i>
                    ${sentimentData.negative} Negative (${negativePercent}%)
                </div>
            `;
        } else {
            sentimentBars = '<p class="text-muted">No reviews available for sentiment analysis.</p>';
        }

        let detailedSentiments = '';
        if (sentimentData.detailed_sentiments && sentimentData.detailed_sentiments.length > 0) {
            detailedSentiments = `
                <h6 class="mt-4 mb-3">Sample Reviews:</h6>
                ${sentimentData.detailed_sentiments.map(review => `
                    <div class="sentiment-detail-card ${review.sentiment}">
                        <div class="d-flex justify-content-between align-items-start">
                            <span class="text-muted">${review.text}</span>
                            <span class="badge bg-${getSentimentColor(review.sentiment)} ms-2">${review.sentiment}</span>
                        </div>
                    </div>
                `).join('')}
            `;
        }

        container.innerHTML = `
            <div class="mb-4">
                <h6>Overall Sentiment Score: ${(sentimentData.sentiment_score * 100).toFixed(1)}%</h6>
                <div class="progress mb-3" style="height: 25px;">
                    <div class="progress-bar ${getSentimentProgressColor(sentimentData.sentiment_score)}" 
                         style="width: ${Math.abs(sentimentData.sentiment_score * 100)}%"></div>
                </div>
            </div>
            
            <h6>Review Distribution:</h6>
            <div class="mb-4">
                ${sentimentBars}
            </div>
            
            ${detailedSentiments}
        `;
    }

    // Display detailed scores
    function displayDetailedScores(componentScores) {
        const container = document.getElementById('detailedScores');

        // Map backend keys to friendly labels and icons
        const components = [
            { key: 'domain', label: 'Domain Trust', icon: 'globe' },
            { key: 'review_quality', label: 'Review Quality', icon: 'star' },
            { key: 'rating_consistency', label: 'Rating Consistency', icon: 'chart-line' },
            { key: 'seller', label: 'Seller Reputation', icon: 'store' },
            { key: 'price', label: 'Price Reasonableness', icon: 'dollar-sign' }
        ];

        container.innerHTML = components.map(component => {
            // Backend component scores are 0-1 floats — convert to percentage
            const raw = componentScores && typeof componentScores[component.key] !== 'undefined' ? componentScores[component.key] : 0;
            const pct = Math.round(Number(raw) * 100);
            return `
            <div class="component-score">
                <div class="score-label d-flex justify-content-between align-items-center">
                    <div>
                        <i class="fas fa-${component.icon} me-2"></i>
                        ${component.label}
                    </div>
                    <div>${pct}%</div>
                </div>
                <div class="progress mt-2">
                    <div class="progress-bar ${getScoreColor(pct)}" 
                         style="width: ${pct}%;"></div>
                </div>
            </div>
        `;
        }).join('');
    }

    // Utility functions
    function isValidUrl(string) {
        try {
            new URL(string);
            return true;
        } catch (_) {
            return false;
        }
    }

    function getTrustScoreColor(score) {
        if (score >= 80) return 'text-success';
        if (score >= 60) return 'text-warning';
        return 'text-danger';
    }

    function getRecommendationIcon(action) {
        switch(action.toLowerCase()) {
            case 'buy': return 'check-circle';
            case 'be careful': return 'exclamation-triangle';
            case 'avoid': return 'times-circle';
            default: return 'question-circle';
        }
    }

    function getSentimentColor(sentiment) {
        switch(sentiment) {
            case 'positive': return 'success';
            case 'neutral': return 'warning';
            case 'negative': return 'danger';
            default: return 'secondary';
        }
    }

    function getSentimentProgressColor(score) {
        if (score > 0.2) return 'bg-success';
        if (score < -0.2) return 'bg-danger';
        return 'bg-warning';
    }

    function getScoreColor(score) {
        if (score >= 80) return 'bg-success';
        if (score >= 60) return 'bg-warning';
        return 'bg-danger';
    }

    function showLoading(show) {
        if (show) {
            loadingSpinner.classList.remove('d-none');
            analyzeBtn.disabled = true;
            analyzeBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Analyzing...';
        } else {
            loadingSpinner.classList.add('d-none');
            analyzeBtn.disabled = false;
            analyzeBtn.innerHTML = '<i class="fas fa-search me-2"></i>Analyze Product';
        }
    }

    function showResults() {
        resultsSection.classList.remove('d-none');
        resultsSection.classList.add('fade-in');
    }

    function hideResults() {
        resultsSection.classList.add('d-none');
        resultsSection.classList.remove('fade-in');
    }

    function showError(message) {
        errorMessage.textContent = message;
        errorAlert.classList.remove('d-none');
    }

    function hideError() {
        errorAlert.classList.add('d-none');
    }

    // Add smooth scrolling for better UX
    function scrollToResults() {
        resultsSection.scrollIntoView({ behavior: 'smooth' });
    }

    // Enhanced form validation
    productUrlInput.addEventListener('input', function() {
        const url = this.value.trim();
        if (url && isValidUrl(url)) {
            this.classList.remove('is-invalid');
            this.classList.add('is-valid');
        } else if (url) {
            this.classList.remove('is-valid');
            this.classList.add('is-invalid');
        } else {
            this.classList.remove('is-valid', 'is-invalid');
        }
    });
});
