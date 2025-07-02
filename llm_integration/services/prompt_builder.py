"""
Prompt builder service for constructing LLM prompts
"""

from typing import List
from ..models.cached_paper import CachedPaper

class PromptBuilder:
    """Service for building prompts for LLM"""
    
    def __init__(self, max_context_length: int = 8000):
        """
        Initialize prompt builder
        
        Args:
            max_context_length: Maximum context length in tokens
        """
        self.max_context_length = max_context_length
    
    def build_rag_prompt(self, query: str, papers: List[CachedPaper]) -> str:
        """
        Build a prompt for RAG-augmented queries
        
        Args:
            query: User's question
            papers: Relevant papers for context
            
        Returns:
            Formatted prompt
        """
        if not papers:
            return query
        
        # Format paper context
        paper_context = self.format_paper_context(papers)
        
        # Use the template from settings
        from ..config.llm_settings import LLMSettings
        prompt = LLMSettings.RAG_PROMPT_TEMPLATE.format(
            paper_context=paper_context,
            user_query=query
        )
        
        return prompt
    
    def build_follow_up_prompt(self, query: str, conversation_history: List[str]) -> str:
        """
        Build a prompt for follow-up questions
        
        Args:
            query: Follow-up question
            conversation_history: Previous conversation
            
        Returns:
            Formatted prompt
        """
        if not conversation_history:
            return query
        
        # Format conversation history
        history_text = "\n".join(conversation_history)
        
        # Use the template from settings
        from ..config.llm_settings import LLMSettings
        prompt = LLMSettings.FOLLOW_UP_PROMPT_TEMPLATE.format(
            conversation_history=history_text,
            user_query=query
        )
        
        return prompt
    
    def format_paper_context(self, papers: List[CachedPaper]) -> str:
        """
        Format papers into context string
        
        Args:
            papers: Papers to format
            
        Returns:
            Formatted context string
        """
        if not papers:
            return ""
        
        context_parts = []
        for i, paper in enumerate(papers, 1):
            paper_text = f"""
            Paper {i}: {paper.title}
            Authors: {', '.join(paper.authors)}
            Summary: {paper.summary}
            Content: {paper.text_content[:1000]}...  # Truncate for context
            """
            context_parts.append(paper_text)
        
        return "\n".join(context_parts)
    
    def truncate_context(self, context: str, max_tokens: int) -> str:
        """
        Truncate context to fit within token limits
        
        Args:
            context: Context to truncate
            max_tokens: Maximum tokens allowed
            
        Returns:
            Truncated context
        """
        # Simple character-based truncation (rough approximation)
        # In production, you'd want to use a proper tokenizer
        chars_per_token = 4  # Rough approximation
        max_chars = max_tokens * chars_per_token
        
        if len(context) <= max_chars:
            return context
        
        # Truncate and add ellipsis
        return context[:max_chars-3] + "..."
    
    def get_prompt_template(self, template_name: str) -> str:
        """Get a prompt template by name"""
        # TODO: Implement template retrieval
        pass 