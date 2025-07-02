from typing import List, Dict, Union
from models.paper import Paper
from services.arxiv_service import ArxivService
from services.pdf_service import PDFService
from services.vector_service import VectorService
from config.settings import Settings

class RAGService:
    """Service for RAG (Retrieval-Augmented Generation) operations"""
    
    def __init__(self):
        self.arxiv_service = ArxivService()
        self.pdf_service = PDFService()
        self.vector_service = VectorService()
    
    def assess_search_quality(self, results, query: str, threshold: float = None) -> tuple[bool, Union[str, Dict]]:
        """
        Assess if search results are good enough
        
        Args:
            results: QueryResponse from vector search
            query: Original query
            threshold: Similarity threshold
            
        Returns:
            Tuple of (is_good_enough, quality_metrics)
        """
        if threshold is None:
            threshold = Settings.DEFAULT_SIMILARITY_THRESHOLD
            
        if not results.matches:
            return False, "No results found"
        
        # Get similarity scores
        scores = [match.score for match in results.matches]
        avg_score = sum(scores) / len(scores)
        max_score = max(scores)
        
        # Quality criteria
        quality_metrics = {
            'avg_similarity': avg_score,
            'max_similarity': max_score,
            'num_results': len(results.matches),
            'threshold_met': max_score >= threshold
        }
        
        # Decision logic
        is_good_enough = (
            max_score >= threshold and  # At least one very relevant result
            avg_score >= Settings.MIN_AVERAGE_SCORE and  # Overall relevance is decent
            len(results.matches) >= Settings.MIN_RESULTS_COUNT  # Have multiple results
        )
        
        return is_good_enough, quality_metrics
    
    def rag_query(self, user_query: str, max_results: int = 5) -> List[Paper]:
        """
        Complete RAG query pipeline
        
        Args:
            user_query: User's query
            max_results: Maximum number of results
            
        Returns:
            List of relevant Paper objects
        """
        # Step 1: Search vector database first
        print(f"Searching vector database for: {user_query}")
        query_response = self.vector_service.search_vector_db(user_query, max_results)
        
        # Step 2: Assess quality of existing results
        is_good_enough, quality_metrics = self.assess_search_quality(query_response, user_query)
        print(f"Vector DB quality metrics: {quality_metrics}")
        print(f"is good enough: {is_good_enough}")
  
        
        if is_good_enough:
            # Use existing papers from vector database
            print("Using existing papers from vector database")
            papers = self.vector_service.query_response_to_papers(query_response)
            return papers
        else:
            # Search for new papers
            print("Searching arXiv for new papers...")
            
            # Step 3: Search arXiv
            papers = self.arxiv_service.search_papers(user_query, max_results)
            
            # Step 4: Process papers (download PDFs, extract text)
            processed_papers = self.pdf_service.process_papers(papers)
            
            # Step 5: Add to vector database
            if processed_papers:
                self.vector_service.add_papers_to_vector_db(processed_papers)
            
            return processed_papers
    
    def process_papers_for_rag(self, query: str, max_papers: int = 5) -> List[Paper]:
        """
        Process papers for RAG (legacy method for compatibility)
        
        Args:
            query: Search query
            max_papers: Maximum number of papers
            
        Returns:
            List of processed Paper objects
        """
        # Search arXiv
        papers = self.arxiv_service.search_papers(query, max_papers)
        
        # Process papers
        processed_papers = self.pdf_service.process_papers(papers)
        
        return processed_papers 