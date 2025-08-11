#!/usr/bin/env python3
"""
Test script to verify SectionChunker integration with RAG pipeline
"""

import os
import sys
sys.path.append('.')

from ragpipe.services.rag_service import RAGService
from ragpipe.services.pdf_service import PDFService

def test_chunked_rag():
    """Test the new chunked RAG approach"""
    
    print("=== Testing Chunked RAG Integration ===\n")
    
    # Initialize services
    rag_service = RAGService()
    pdf_service = PDFService()
    
    try:
        # 1. Check if attention paper exists
        pdf_path = "downloads/attention-paper.pdf"
        if not os.path.exists(pdf_path):
            print("❌ Attention paper not found. Please run test_section_chunker.py first.")
            return
        
        print("1. Testing with Attention Paper...")
        
        # 2. Extract both raw and cleaned text from PDF
        text_content = pdf_service.extract_text_from_pdf(pdf_path)
        raw_text = pdf_service.extract_raw_text_from_pdf(pdf_path)
        print(f"   Cleaned text length: {len(text_content)} characters")
        print(f"   Raw text length: {len(raw_text)} characters")
        
        # 3. Create a test paper object with both text versions
        from ragpipe.models.paper import Paper
        test_paper = Paper(
            id="test-attention",
            title="Attention Is All You Need",
            authors=["Vaswani", "Shazeer", "Parmar"],
            summary="Transformer architecture paper",
            published="2017",
            pdf_url="test",
            text_content=text_content,
            score=0.0
        )
        # Add raw text and PDF path for better section detection
        test_paper.pdf_path = pdf_path
        test_paper.raw_text = raw_text
        
        # 4. Test the new chunking approach
        print("\n2. Testing SectionChunker Integration...")
        
        # Test with different queries
        test_queries = [
            "How does attention work in transformers?",
            "What is the model architecture?",
            "How does multi-head attention work?",
            "What are the key innovations?"
        ]
        
        for query in test_queries:
            print(f"\n   Query: '{query}'")
            
            # Use the new chunking method
            relevant_chunks = rag_service.find_relevant_chunks(query, [test_paper], max_chunks=5)
            
            print(f"   Found {len(relevant_chunks)} relevant chunks:")
            
            for i, chunk in enumerate(relevant_chunks[:3], 1):  # Show top 3
                print(f"     Chunk {i}:")
                print(f"       Section: {chunk['section_header']}")
                print(f"       Level: {chunk['section_level']}")
                print(f"       Size: {chunk['chunk_size']} chars")
                print(f"       Relevance Score: {chunk.get('relevance_score', 'N/A'):.3f}")
                print(f"       Preview: {chunk['content'][:100]}...")
        
        # 5. Test chunk formatting for LLM
        print("\n3. Testing Chunk Formatting for LLM...")
        
        # Get chunks for a specific query
        query = "How does attention work in transformers?"
        relevant_chunks = rag_service.find_relevant_chunks(query, [test_paper], max_chunks=3)
        
        if relevant_chunks:
            print(f"   Formatting {len(relevant_chunks)} chunks for LLM...")
            
            # Test the prompt builder formatting
            from llm_integration.services.prompt_builder import PromptBuilder
            prompt_builder = PromptBuilder()
            
            # Format chunks into context
            chunk_context = prompt_builder._format_chunks_for_context(relevant_chunks)
            
            print(f"   Formatted context length: {len(chunk_context)} characters")
            print(f"   Context preview:")
            print("   " + "="*50)
            print(chunk_context[:500] + "..." if len(chunk_context) > 500 else chunk_context)
            print("   " + "="*50)
        
        print("\n✅ Chunked RAG integration test complete!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_chunked_rag()
