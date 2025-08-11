"""
LLM integration with RAG pipeline for academic papers
"""

from .models import Conversation, UserSession
from .services import LLMService, RAGOrchestrator, PromptBuilder
from .config import LLMSettings

__all__ = [
    'Conversation', 
    'UserSession',
    'LLMService',
    'RAGOrchestrator',
    'PromptBuilder',
    'LLMSettings'
]

__version__ = "1.0.0"
__author__ = "Adit Singh"
__description__ = "LLM integration with RAG pipeline for academic papers" 