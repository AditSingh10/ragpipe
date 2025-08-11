"""
Prompt builder service for constructing LLM prompts
"""

from typing import List, Dict
import sys
import os

try:
    from ragpipe.models.paper import Paper
except ImportError:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from ragpipe.models.paper import Paper

class PromptBuilder:
    """Service for building prompts for LLM"""
    
    def __init__(self, max_context_length: int = 4000):
        self.max_context_length = max_context_length
    
    def build_rag_prompt_from_chunks(self, query: str, chunks: List[Dict]) -> str:
        """Build a prompt for RAG-augmented queries using chunked content"""
        if not chunks:
            return query
        
        # Format chunks into context
        chunk_context = self._format_chunks_for_context(chunks)
        
        # Use the template from settings
        from ..config.llm_settings import LLMSettings
        prompt = LLMSettings.RAG_PROMPT_TEMPLATE.format(
            paper_context=chunk_context,
            user_query=query
        )
        
        return prompt
    
    def _format_chunks_for_context(self, chunks: List[Dict]) -> str:
        """
        Format chunks into a readable context string
        
        Args:
            chunks: List of chunk dictionaries
            
        Returns:
            Formatted context string
        """
        if not chunks:
            return ""
        
        context_parts = []
        total_length = 0
        max_context_length = 8000  # Limit context for 5 chunks to prevent timeouts
        
        for i, chunk in enumerate(chunks, 1):
            # Format each chunk with metadata
            chunk_text = f"""
--- Chunk {i} ---
Paper: {chunk['paper_title']}
Authors: {', '.join(chunk['paper_authors'])}
Section: {chunk['section_header']} (Level {chunk['section_level']})
Content: {chunk['content']}
--- End Chunk {i} ---
"""
            
            # Check if adding this chunk would exceed the limit
            if total_length + len(chunk_text) > max_context_length:
                print(f"   ⚠️  Truncating context at chunk {i} to prevent timeout")
                break
                
            context_parts.append(chunk_text)
            total_length += len(chunk_text)
        
        return "\n".join(context_parts)
    
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
    
    def format_paper_context(self, papers: List[Paper]) -> str:
        """
        Format papers into context string (legacy method)
        
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