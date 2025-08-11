#!/usr/bin/env python3
"""
Test script for section chunker
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ragpipe.services.section_chunker import SectionChunker
from ragpipe.services.pdf_service import PDFService
from ragpipe.models.paper import Paper

def test_section_chunker():
    """Test the section chunker with the attention paper"""
    
    print("=== Testing Section Chunker ===\n")
    
    paper = Paper(
        id="attention-paper",
        title="Attention Is All You Need",
        authors=["Vaswani, Ashish", "Shazeer, Noam", "Parmar, Niki", "Uszkoreit, Jakob", "Jones, Llion", "Gomez, Aidan N.", "Kaiser, Lukasz", "Polosukhin, Illia"],
        summary="We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely.",
        published="2017",
        pdf_url="https://arxiv.org/pdf/1706.03762.pdf",
        text_content="",
        pdf_path="",
        score=0.0
    )
    
    # Initialize services
    pdf_service = PDFService()
    chunker = SectionChunker(max_chunk_size=2000)
    
    try:
        print("1. Checking if PDF already exists...")
        pdf_path = "downloads/attention-paper.pdf"
        
        if not os.path.exists(pdf_path):
            print("   PDF not found, downloading...")
            pdf_path = pdf_service.download_paper_pdf(paper)
            if not pdf_path:
                print("❌ Failed to download PDF")
                return
            print("   ✅ PDF downloaded successfully")
        else:
            print("   ✅ PDF already exists")
        
        print("\n2. Extracting text from PDF...")
        text_content = pdf_service.extract_text_from_pdf(pdf_path)
        
        if not text_content:
            print("❌ Failed to extract text")
            return
        
        print(f"   ✅ Text extracted: {len(text_content)} characters")
        
        print("\n3. Chunking paper into sections...")
        # Use raw text for better section detection
        raw_text = pdf_service.extract_raw_text_from_pdf(pdf_path)
        print(f"   Raw text length: {len(raw_text)} characters")
        
        # Test with different minimum chunk sizes
        print("\n   Testing with min_chunk_size=50:")
        chunker = SectionChunker(max_chunk_size=2000, min_chunk_size=50)
        chunks = chunker.chunk_paper(raw_text)
        
        print(f"\n   Testing with min_chunk_size=100:")
        chunker_larger = SectionChunker(max_chunk_size=2000, min_chunk_size=100)
        chunks_larger = chunker_larger.chunk_paper(raw_text)
        
        print(f"   ✅ Created {len(chunks)} chunks (min size 50)")
        print(f"   ✅ Created {len(chunks_larger)} chunks (min size 100)")
        
        # Show chunk details for min size 50
        print("\n4. Chunk details (min size 50):")
        total_chars = 0
        for i, chunk in enumerate(chunks[:15]):  # Show first 15 chunks
            print(f"   {i+1}. {chunk.section_header}")
            print(f"      Level: {chunk.section_level}")
            print(f"      Size: {chunk.chunk_size} chars")
            print(f"      Position: {chunk.start_index} - {chunk.end_index}")
            print(f"      Preview: {chunk.content[:150]}...")
            print()
            total_chars += chunk.chunk_size
        
        print(f"   Total characters in chunks: {total_chars}")
        print(f"   Original text length: {len(text_content)}")
        print(f"   Coverage: {(total_chars / len(text_content)) * 100:.1f}%")
        
        # Show comparison with larger minimum size
        print(f"\n   Comparison with min size 100:")
        total_chars_larger = sum(chunk.chunk_size for chunk in chunks_larger)
        print(f"   Total characters in chunks: {total_chars_larger}")
        print(f"   Coverage: {(total_chars_larger / len(text_content)) * 100:.1f}%")
        print(f"   Chunks removed: {len(chunks) - len(chunks_larger)}")
        
        # Test with a smaller sample first
        print("\n5. Testing with sample text...")
        sample_text = """
        Attention Is All You Need
        
        Abstract
        The dominant sequence transduction models are based on complex recurrent or
        convolutional neural networks that include an encoder and a decoder.
        
        1. Introduction
        Recurrent neural networks, long short-term memory and gated recurrent neural networks
        in particular, have been firmly established as state of the art approaches.
        
        2. Background
        The goal of reducing sequential computation also forms the foundation.
        
        2.1 Neural Networks
        Neural networks have been used for various tasks.
        
        3. Model Architecture
        Most competitive neural sequence transduction models have an encoder-decoder structure.
        """
        
        sample_chunks = chunker.chunk_paper(sample_text)
        print(f"   Sample text chunks: {len(sample_chunks)}")
        for chunk in sample_chunks:
            print(f"     {chunk.section_header} (Level {chunk.section_level}): {chunk.chunk_size} chars")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_section_chunker()
