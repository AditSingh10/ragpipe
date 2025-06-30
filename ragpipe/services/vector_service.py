from typing import List, Dict, Union
from sentence_transformers import SentenceTransformer
from pinecone import QueryResponse, Pinecone
from models.paper import Paper
from config.settings import Settings

class VectorService:
    """Service for vector database operations"""
    
    def __init__(self):
        self.embedding_model = SentenceTransformer(Settings.EMBEDDING_MODEL)
        self.pc = Pinecone(api_key=Settings.PINECONE_API_KEY)
        self.index = self.pc.Index(Settings.PINECONE_INDEX_NAME)
    
    def add_papers_to_vector_db(self, papers: List[Paper]) -> None:
        """
        Add papers to vector database
        
        Args:
            papers: List of Paper objects
        """
        vectors = []
        
        for paper in papers:
            # Create embedding from text content
            embedding = self.embedding_model.encode(paper.text_content)
            
            # Prepare vector for upsert
            vectors.append((
                paper.id,  # Vector ID
                embedding.tolist(),  # Embedding vector
                {  # Metadata
                    'title': paper.title,
                    'authors': paper.authors,
                    'summary': paper.summary,
                    'pdf_url': paper.pdf_url
                }
            ))
        
        # Batch upsert
        self.index.upsert(vectors=vectors)
        print(f"Added {len(papers)} papers to vector database")
    
    def search_vector_db(self, query: str, max_results: int = 5) -> QueryResponse:
        """
        Search vector database
        
        Args:
            query: Search query
            max_results: Maximum number of results
            
        Returns:
            QueryResponse from Pinecone
        """
        # Convert query to embedding
        query_embedding = self.embedding_model.encode(query).tolist()
        
        # Search Pinecone
        results = self.index.query(
            vector=query_embedding,
            top_k=max_results,
            include_metadata=True
        )
        
        return results
    
    def query_response_to_papers(self, results: QueryResponse) -> List[Paper]:
        """
        Convert QueryResponse to list of Paper objects
        
        Args:
            results: QueryResponse from Pinecone
            
        Returns:
            List of Paper objects
        """
        papers = []
        
        for match in results.matches:
            paper = Paper(
                id=match.id,
                title=match.metadata['title'],
                authors=match.metadata['authors'],
                summary=match.metadata['summary'],
                published="",  # Not stored in vector DB
                pdf_url=match.metadata['pdf_url'],
                text_content='', # no longer stored in DB
                score=match.score
            )
            papers.append(paper)
        
        return papers
    
    def get_index_stats(self) -> Dict:
        """Get vector database statistics"""
        stats = self.index.describe_index_stats()
        return {
            'dimension': stats.dimension,
            'total_vector_count': stats.total_vector_count
        } 