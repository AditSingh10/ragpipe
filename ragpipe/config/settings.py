import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """Configuration settings for the application"""
    
    ARXIV_BASE_URL = "http://export.arxiv.org/api/query"
    ARXIV_PDF_BASE_URL = "https://arxiv.org/pdf"
    
    PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
    PINECONE_ENVIRONMENT = os.getenv('ENVIRONMENT')
    PINECONE_INDEX_NAME = os.getenv('INDEX')
    
    EMBEDDING_MODEL = 'all-MiniLM-L6-v2'
    DOWNLOAD_DIR = "downloads"
    
    DEFAULT_SIMILARITY_THRESHOLD = 0.4
    MIN_AVERAGE_SCORE = 0.2
    MIN_RESULTS_COUNT = 1