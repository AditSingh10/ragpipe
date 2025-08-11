"""
RAG orchestrator for coordinating LLM and RAG pipeline
"""

from typing import List, Optional
import sys
import os

# Handle imports for both module and direct execution
try:
    from ragpipe.models.paper import Paper
    from ragpipe.services.pdf_service import PDFService
    from ..models.conversation import Conversation
except ImportError:
    # When running directly, add parent directories to path
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from ragpipe.models.paper import Paper
    from ragpipe.services.pdf_service import PDFService
    from llm_integration.models.conversation import Conversation

class RAGOrchestrator:
    """Orchestrates the interaction between LLM and RAG pipeline"""
    
    def __init__(self, rag_service, llm_service):
        """
        Initialize RAG orchestrator
        
        Args:
            rag_service: Your RAG pipeline service
            llm_service: LLM service
        """
        self.rag_service = rag_service
        self.llm_service = llm_service
        self.pdf_service = PDFService()
    
    def process_user_query(self, user_id: str, query: str, use_rag: bool = False) -> str:
        """
        Process a user query with optional RAG augmentation
        
        Args:
            user_id: User identifier
            query: User's question
            use_rag: Whether to use RAG
            
        Returns:
            LLM response
        """
        if use_rag:
            # Use RAG pipeline to get relevant papers
            relevant_papers = self.rag_service.rag_query(query)
            
            if relevant_papers:
                # Ensure papers have text content (download if needed)
                processed_papers = self._ensure_papers_have_content(relevant_papers)
                
                if processed_papers:
                    # Use new SectionChunker approach to get relevant chunks
                    relevant_chunks = self.rag_service.find_relevant_chunks(query, processed_papers)
                    
                    if relevant_chunks:
                        # Build prompt with chunked context
                        from .prompt_builder import PromptBuilder
                        prompt_builder = PromptBuilder()
                        prompt = prompt_builder.build_rag_prompt_from_chunks(query, relevant_chunks)
                        return self.llm_service.generate_response(prompt)
                    else:
                        # No relevant chunks found, use direct LLM response
                        return self.llm_service.generate_response(query)
                else:
                    # No papers with content, use direct LLM response
                    return self.llm_service.generate_response(query)
            else:
                # No relevant papers found, use direct LLM response
                return self.llm_service.generate_response(query)
        else:
            # Direct LLM response without RAG
            return self.llm_service.generate_response(query)
    
    def _ensure_papers_have_content(self, papers: List[Paper]) -> List[Paper]:
        """
        Ensure papers have text content by downloading PDFs if needed
        
        Args:
            papers: List of papers
            
        Returns:
            List of papers with text content
        """
        papers_with_content = []
        
        for paper in papers:
            if paper.text_content:
                # Paper already has content
                papers_with_content.append(paper)
            elif paper.pdf_url:
                # Paper needs to be downloaded and processed
                try:
                    # Download PDF
                    pdf_path = self.pdf_service.download_paper_pdf(paper)
                    if pdf_path:
                        # Extract text
                        text_content = self.pdf_service.extract_text_from_pdf(pdf_path)
                        if text_content:
                            paper.pdf_path = pdf_path
                            paper.text_content = text_content
                            papers_with_content.append(paper)
                        else:
                            print(f"Failed to extract text from PDF for paper {paper.id}")
                    else:
                        print(f"Failed to download PDF for paper {paper.id}")
                except Exception as e:
                    print(f"Error processing paper {paper.id}: {e}")
            else:
                print(f"Paper {paper.id} has no PDF URL or text content")
        
        return papers_with_content
    
    def handle_follow_up(self, user_id: str, query: str) -> str:
        """
        Handle follow-up questions using RAG pipeline
        
        Args:
            user_id: User identifier
            query: Follow-up question
            
        Returns:
            LLM response
        """
        # For follow-ups, we can use the same RAG pipeline
        # The vector DB will find relevant papers based on the follow-up query
        return self.process_user_query(user_id, query, use_rag=True) 