from ragpipe.services.rag_service import RAGService
from ragpipe.services.vector_service import VectorService

def main():
    """Main function to test the refactored RAG pipeline"""
    print("=== Testing Refactored ArXiv RAG Pipeline ===\n")
    
    # Initialize services
    rag_service = RAGService()
    vector_service = VectorService()
    
    # Test 1: Vector Database Connection
    try:
        stats = vector_service.get_index_stats()
        print("✅ Vector database connected successfully!")
        print(f"   Index: {stats['dimension']} dimensions")
        print(f"   Total vectors: {stats['total_vector_count']}")
    except Exception as e:
        print(f"❌ Vector database connection failed: {e}")
        return
    
    # Test 2: ArXiv Search
    print("\n=== Testing ArXiv Search ===")
    papers = rag_service.arxiv_service.search_papers("transformer", max_results=3)
    print(f"Found {len(papers)} papers")
    for paper in papers:
        print(f"- {paper.get_short_title()}")
    
    # Test 3: PDF Processing
    print("\n=== Testing PDF Processing ===")
    processed_papers = rag_service.process_papers_for_rag("AI", max_papers=1)
    if processed_papers:
        paper = processed_papers[0]
        print(f"✅ Processed: {paper.title}")
        print(f"Text length: {len(paper.text_content)} characters")
        print(f"First 200 chars: {paper.text_content[:200]}...")
    
    # Test 4: Vector Database Operations
    print("\n=== Testing Vector Database ===")
    if processed_papers:
        vector_service.add_papers_to_vector_db(processed_papers)
        print("✅ Papers added to vector database")
        
        # Test search
        results = vector_service.search_vector_db("transformer architecture")
        print(f"✅ Vector search found {len(results.matches)} results")
        for match in results.matches:
            print(f"- {match.metadata['title'][:50]}... (score: {match.score:.3f})")
    
    # Test 5: Complete RAG Pipeline
    print("\n=== Testing Complete RAG Pipeline ===")
    results = rag_service.rag_query("transformer architecture improvements", max_results=3)
    print(f"✅ RAG query returned {len(results)} papers")
    for paper in results:
        print(f"- {paper.get_short_title()} (score: {paper.score:.3f})")
    
    print("\n=== Testing Complete ===")

if __name__ == "__main__":
    main() 