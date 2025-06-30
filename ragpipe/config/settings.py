import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    """Configuration settings for the application"""
    
    # ArXiv API settings
    ARXIV_BASE_URL = "http://export.arxiv.org/api/query"
    ARXIV_PDF_BASE_URL = "https://arxiv.org/pdf"
    
    # Pinecone settings
    PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
    PINECONE_ENVIRONMENT = os.getenv('ENVIRONMENT')
    PINECONE_INDEX_NAME = os.getenv('INDEX')
    
    # Embedding model settings
    EMBEDDING_MODEL = 'all-MiniLM-L6-v2'
    
    # File paths
    DOWNLOAD_DIR = "downloads"
    
    # Quality thresholds
    DEFAULT_SIMILARITY_THRESHOLD = 0.8
    MIN_AVERAGE_SCORE = 0.75
    MIN_RESULTS_COUNT = 2 