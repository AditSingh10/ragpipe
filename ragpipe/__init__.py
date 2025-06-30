# ArXiv RAG Pipeline Package

from .models import Paper
from .services import ArxivService, PDFService, VectorService, RAGService
from .config import Settings
from .utils import TextCleaner

__all__ = [
    # Models
    'Paper',
    
    # Services
    'ArxivService',
    'PDFService', 
    'VectorService',
    'RAGService',
    
    # Configuration
    'Settings',
    
    # Utilities
    'TextCleaner'
]

# Version info
__version__ = "1.0.0"
__author__ = "Your Name"
__description__ = "A RAG pipeline for academic papers using ArXiv and Pinecone" 