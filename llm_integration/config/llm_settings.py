"""
LLM settings configuration
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class LLMSettings:
    """Configuration settings for LLM integration"""
    
    # LLM API settings
    LLM_MODEL = os.getenv('LLM_MODEL', 'llama2:7b')
    LLM_PROVIDER = os.getenv('LLM_PROVIDER', 'ollama')
    
    # Ollama specific settings
    OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
    OLLAMA_TIMEOUT = int(os.getenv('OLLAMA_TIMEOUT', '30'))
    
    # Context and prompt settings
    MAX_CONTEXT_LENGTH = int(os.getenv('MAX_CONTEXT_LENGTH', '8000'))
    MAX_CACHED_PAPERS = int(os.getenv('MAX_CACHED_PAPERS', '50'))
    RAG_SIMILARITY_THRESHOLD = float(os.getenv('RAG_SIMILARITY_THRESHOLD', '0.7'))
    
    # Cache settings
    CACHE_TTL_HOURS = int(os.getenv('CACHE_TTL_HOURS', '24'))
    MAX_CONVERSATION_HISTORY = int(os.getenv('MAX_CONVERSATION_HISTORY', '100'))
    
    # Prompt templates
    RAG_PROMPT_TEMPLATE = """
    Based on the following academic papers, please answer the user's question:
    
    {paper_context}
    
    Question: {user_query}
    
    Please provide a comprehensive answer based on the papers above.
    """
    
    FOLLOW_UP_PROMPT_TEMPLATE = """
    Previous conversation:
    {conversation_history}
    
    Current question: {user_query}
    
    Please provide a helpful response, building on the previous conversation.
    """ 