"""
LLM settings configuration
"""

import os
from dotenv import load_dotenv

load_dotenv()

class LLMSettings:
    """Configuration settings for LLM integration"""
    
    LLM_MODEL = os.getenv('LLM_MODEL', 'llama2:7b')
    LLM_PROVIDER = os.getenv('LLM_PROVIDER', 'ollama')
    
    OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
    OLLAMA_TIMEOUT = int(os.getenv('OLLAMA_TIMEOUT', '120'))
    
    MAX_CONTEXT_LENGTH = int(os.getenv('MAX_CONTEXT_LENGTH', '4000'))
    RAG_SIMILARITY_THRESHOLD = float(os.getenv('RAG_SIMILARITY_THRESHOLD', '0.7'))
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