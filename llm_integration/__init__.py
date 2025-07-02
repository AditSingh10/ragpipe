# LLM Integration Package

from .models import Conversation, CachedPaper, UserSession
from .services import LLMService, RAGOrchestrator, PaperCacheService, PromptBuilder
from .config import LLMSettings

__all__ = [
    # Models
    'Conversation',
    'CachedPaper', 
    'UserSession',
    
    # Services
    'LLMService',
    'RAGOrchestrator',
    'PaperCacheService',
    'PromptBuilder',
    
    # Configuration
    'LLMSettings'
]

# Version info
__version__ = "1.0.0"
__author__ = "Adit Singh"
__description__ = "LLM integration with RAG pipeline for academic papers" 