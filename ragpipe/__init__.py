"""
RAG pipeline for academic papers

Tools for searching, downloading, and querying research papers from ArXiv.
Combines vector search with LLM capabilities for intelligent paper analysis.
"""

from .models import Paper
from .services import ArxivService, PDFService, VectorService, RAGService
from .config import Settings
from .utils import TextCleaner

__all__ = [
    'Paper',
    'ArxivService',
    'PDFService', 
    'VectorService',
    'RAGService',
    'Settings',
    'TextCleaner'
]

__version__ = "1.0.0"
__author__ = "Adit Singh"
__description__ = "A RAG pipeline for academic papers using ArXiv and Pinecone intended for querying LLM" 