from waitress import serve
from app import app
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('waitress')

if __name__ == '__main__':
    logger.info('Starting production server...')
    # Configure Waitress with reasonable defaults
    serve(
        app,
        host='0.0.0.0',
        port=5000,
        threads=4,  # Adjust based on your CPU cores
        url_scheme='http',
        channel_timeout=300,
        cleanup_interval=30,
        connection_limit=1000
    )