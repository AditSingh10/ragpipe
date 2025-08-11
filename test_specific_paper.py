#!/usr/bin/env python3
"""
Test script for specific paper extraction
"""

import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ragpipe.models.paper import Paper
from ragpipe.services.pdf_service import PDFService
from llm_integration.services.relevant_parts_extractor import RelevantPartsExtractor

def test_specific_paper():
    """Test extraction with a specific paper"""
    
    # Create a paper object with a specific URL
    paper = Paper(
        id="attention-paper",
        title="Attention Is All You Need",
        authors=["Vaswani, Ashish", "Shazeer, Noam", "Parmar, Niki", "Uszkoreit, Jakob", "Jones, Llion", "Gomez, Aidan N.", "Kaiser, Lukasz", "Polosukhin, Illia"],
        summary="We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely.",
        published="2017",
        pdf_url="https://arxiv.org/pdf/1706.03762.pdf",
        text_content="",  # Will be filled after download
        pdf_path="",
        score=0.0
    )
    
    print("=== Testing Specific Paper Extraction ===\n")
    print(f"Paper: {paper.title}")
    print(f"PDF URL: {paper.pdf_url}")
    
    # Download and extract text
    pdf_service = PDFService()
    
    try:
        print("\n1. Downloading PDF...")
        pdf_path = pdf_service.download_paper_pdf(paper)
        
        if not pdf_path:
            print("❌ Failed to download PDF")
            return
        
        print("✅ PDF downloaded successfully")
        
        print("\n2. Extracting text...")
        text_content = pdf_service.extract_text_from_pdf(pdf_path)
        
        if not text_content:
            print("❌ Failed to extract text")
            return
        
        paper.text_content = text_content
        paper.pdf_path = pdf_path
        
        print(f"✅ Text extracted: {len(text_content)} characters")
        
        # Test relevant parts extraction
        print("\n3. Testing Relevant Parts Extraction")
        extractor = RelevantPartsExtractor(max_tokens=4000)
        
        # Test queries
        test_queries = [
            "What is the attention mechanism?",
            "How does self-attention work?",
            "What are the advantages of transformers?",
            "Explain the transformer architecture",
            "What is the difference between RNN and transformer?"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n--- Test {i}: {query} ---")
            relevant_content = extractor.extract_relevant_parts(query, [paper])
            
            print(f"Content length: {len(relevant_content)} characters")
            print(f"Estimated tokens: {len(relevant_content) // 4}")
            print("\nExtracted content:")
            print("=" * 60)
            print(relevant_content)
            print("=" * 60)
        
        print("\n✅ All tests completed! Evaluate the extraction quality above.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_specific_paper() 