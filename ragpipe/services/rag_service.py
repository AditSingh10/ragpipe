from typing import List, Dict, Union
from ..models.paper import Paper
from .arxiv_service import ArxivService
from .pdf_service import PDFService
from .vector_service import VectorService
from .section_chunker import SectionChunker
from ..config.settings import Settings

class RAGService:
    """Service for RAG (Retrieval-Augmented Generation) operations"""
    
    def __init__(self):
        self.arxiv_service = ArxivService()
        self.pdf_service = PDFService()
        self.vector_service = VectorService()
    
    def assess_search_quality(self, results, query: str, threshold: float = None) -> tuple[bool, Union[str, Dict]]:
        """Assess if search results are good enough for the query"""
        if threshold is None:
            threshold = Settings.DEFAULT_SIMILARITY_THRESHOLD
            
        if not results.matches:
            return False, "No results found"
        
        # Get similarity scores
        scores = [match.score for match in results.matches]
        avg_score = sum(scores) / len(scores)
        max_score = max(scores)
        
        quality_metrics = {
            'avg_similarity': avg_score,
            'max_similarity': max_score,
            'num_results': len(results.matches),
            'threshold_met': max_score >= threshold
        }
        
        is_good_enough = (
            max_score >= threshold and
            avg_score >= Settings.MIN_AVERAGE_SCORE and
            len(results.matches) >= Settings.MIN_RESULTS_COUNT
        )
        
        return is_good_enough, quality_metrics
    
    def rag_query(self, user_query: str, max_results: int = 5) -> List[Paper]:
        """Complete RAG query pipeline - search vector DB first, then arXiv if needed"""
        print(f"Searching vector database for: {user_query}")
        query_response = self.vector_service.search_vector_db(user_query, max_results)
        
        is_good_enough, quality_metrics = self.assess_search_quality(query_response, user_query)
        print(f"Vector DB quality metrics: {quality_metrics}")
        print(f"is good enough: {is_good_enough}")
        
        if is_good_enough:
            print("Using existing papers from vector database")
            papers = self.vector_service.query_response_to_papers(query_response)
            return papers
        else:
            print("Searching arXiv for new papers...")
            papers = self.arxiv_service.search_papers(user_query, max_results)
            processed_papers = self.pdf_service.process_papers(papers)
            
            if processed_papers:
                self.vector_service.add_papers_to_vector_db(processed_papers)
            
            return processed_papers
    
    def find_relevant_chunks(self, query: str, papers: List[Paper], max_chunks: int = 5) -> List[Dict]:
        """Find relevant chunks from papers using SectionChunker and semantic relevance"""
        if not papers:
            return []
        
        chunker = SectionChunker(max_chunk_size=2000, min_chunk_size=100)
        all_chunks = []
        
        for paper in papers:
            if not paper.text_content:
                continue
                
            # Use raw text for better section detection
            # First try to get raw text if available, otherwise use cleaned text
            if hasattr(paper, 'raw_text') and paper.raw_text:
                # Use stored raw text
                raw_text = paper.raw_text
            elif hasattr(paper, 'pdf_path') and paper.pdf_path:
                try:
                    # Get raw text from PDF for better section detection
                    raw_text = self.pdf_service.extract_raw_text_from_pdf(paper.pdf_path)
                except:
                    raw_text = paper.text_content
            else:
                raw_text = paper.text_content
            
            # Chunk the paper
            chunks = chunker.chunk_paper(raw_text)
            
            # Add paper metadata to each chunk
            for chunk in chunks:
                chunk_data = {
                    'paper_id': paper.id,
                    'paper_title': paper.title,
                    'paper_authors': paper.authors,
                    'paper_summary': paper.summary,
                    'pdf_url': paper.pdf_url,
                    'section_header': chunk.section_header,
                    'section_level': chunk.section_level,
                    'content': chunk.content,
                    'chunk_size': chunk.chunk_size,
                    'start_index': chunk.start_index,
                    'end_index': chunk.end_index
                }
                all_chunks.append(chunk_data)
        
        # Score chunks by relevance to the query
        scored_chunks = self._score_chunks_by_relevance(query, all_chunks)
        
        # Sort by relevance score (highest first)
        scored_chunks.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        # Return top relevant chunks
        selected_chunks = self._select_diverse_top_chunks(scored_chunks, max_chunks)
        return selected_chunks
    
    def _select_diverse_top_chunks(self, scored_chunks: List[Dict], max_chunks: int) -> List[Dict]:
        """
        Select diverse top chunks across papers to avoid overwhelming the LLM
        
        Args:
            scored_chunks: List of scored chunks
            max_chunks: Maximum number of chunks to return
            
        Returns:
            List of diverse, relevant chunks
        """
        if len(scored_chunks) <= max_chunks:
            return scored_chunks
        
        selected_chunks = []
        paper_ids_seen = set()
        
        # First pass: Get top chunks from different papers
        for chunk in scored_chunks:
            if len(selected_chunks) >= max_chunks:
                break
                
            paper_id = chunk['paper_id']
            
            # If we haven't seen this paper yet, add the chunk
            if paper_id not in paper_ids_seen:
                selected_chunks.append(chunk)
                paper_ids_seen.add(paper_id)
        
        # Second pass: Fill remaining slots with highest scoring chunks
        remaining_slots = max_chunks - len(selected_chunks)
        if remaining_slots > 0:
            # Get chunks we haven't selected yet
            unselected_chunks = [c for c in scored_chunks if c not in selected_chunks]
            # Add top remaining chunks
            selected_chunks.extend(unselected_chunks[:remaining_slots])
        
        # Sort by relevance score to maintain quality order
        selected_chunks.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return selected_chunks
    
    def _score_chunks_by_relevance(self, query: str, chunks: List[Dict]) -> List[Dict]:
        """
        Score chunks by their relevance to the query
        
        Args:
            query: User's query
            chunks: List of chunks to score
            
        Returns:
            List of chunks with relevance scores
        """
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        scored_chunks = []
        
        for chunk in chunks:
            relevance_score = 0.0
            
            # 1. Section header relevance (highest weight)
            header_lower = chunk['section_header'].lower()
            header_words = set(header_lower.split())
            
            # Count matching words in header
            header_matches = len(query_words.intersection(header_lower.split()))
            relevance_score += header_matches * 0.4  # 40% weight for header matches
            
            # 2. Content relevance (medium weight)
            content_lower = chunk['content'].lower()
            content_words = set(content_lower.split())
            
            # Count matching words in content
            content_matches = len(query_words.intersection(content_words))
            relevance_score += content_matches * 0.01  # 1% weight per content word match
            
            # 3. Section level bonus (lower level = more specific = higher relevance)
            level_bonus = max(0, 3 - chunk['section_level']) * 0.1
            relevance_score += level_bonus
            
            # 4. Length penalty (very long chunks might be too broad)
            if chunk['chunk_size'] > 3000:
                relevance_score *= 0.8
            
            # 5. Ensure minimum relevance
            relevance_score = max(0.0, relevance_score)
            
            # Add score to chunk data
            chunk_with_score = chunk.copy()
            chunk_with_score['relevance_score'] = relevance_score
            scored_chunks.append(chunk_with_score)
        
        return scored_chunks
    
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