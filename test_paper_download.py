#!/usr/bin/env python3
"""
Test script to download a paper and test relevant parts extraction
"""

import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ragpipe.services.rag_service import RAGService
from llm_integration.services.relevant_parts_extractor import RelevantPartsExtractor

def test_paper_download_and_extraction():
    """Download a paper and test relevant parts extraction"""
    
    print("=== Testing Paper Download and Relevant Parts Extraction ===\n")
    
    # Initialize RAG service
    rag_service = RAGService()
    
    # Test query to find a paper
    test_query = "attention mechanism transformer"
    print(f"Searching for papers about: {test_query}")
    
    try:
        # Use RAG pipeline to find and download papers
        papers = rag_service.rag_query(test_query, max_results=1)
        
        if not papers:
            print("❌ No papers found!")
            return
        
        paper = papers[0]
        print(f"✅ Found paper: {paper.title}")
        print(f"Authors: {', '.join(paper.authors)}")
        print(f"PDF URL: {paper.pdf_url}")
        print(f"Has text content: {'Yes' if paper.text_content else 'No'}")
        print(f"Text length: {len(paper.text_content)} characters")
        
        if not paper.text_content:
            print("❌ Paper has no text content - download may have failed")
            return
        
        # Test relevant parts extraction
        print("\n=== Testing Relevant Parts Extraction ===")
        
        extractor = RelevantPartsExtractor(max_tokens=4000)
        
        # Test queries
        test_queries = [
            "What is the attention mechanism?",
            "How does self-attention work?",
            "What are the advantages of transformers?",
            "Explain the transformer architecture"
        ]
        
        for query in test_queries:
            print(f"\n--- Query: {query} ---")
            relevant_content = extractor.extract_relevant_parts(query, [paper])
            
            print(f"Extracted content length: {len(relevant_content)} characters")
            print(f"Estimated tokens: {len(relevant_content) // 4}")
            print("\nExtracted content:")
            print("-" * 50)
            print(relevant_content)
            print("-" * 50)
        
        print("\n✅ All tests completed! Evaluate the extraction quality above.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_paper_download_and_extraction() 