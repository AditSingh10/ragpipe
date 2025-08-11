#!/usr/bin/env python3
"""
Test script to check PDF content extraction
"""

import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ragpipe.models.paper import Paper
from ragpipe.services.pdf_service import PDFService

def test_pdf_content():
    """Test what content is actually extracted from the PDF"""
    
    # Create a paper object with the attention paper
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
    
    print("=== Testing PDF Content Extraction ===\n")
    
    # Download and extract text
    pdf_service = PDFService()
    
    try:
        print("1. Downloading PDF...")
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
        
        print(f"✅ Text extracted: {len(text_content)} characters")
        
        # Show the first 1000 characters
        print("\n3. First 10000 characters of extracted text:")
        print("=" * 60)
        print(text_content[:10000])
        print("=" * 60)
        
        # Show the last 1000 characters
        print("\n4. Last 1000 characters of extracted text:")
        print("=" * 60)
        print(text_content[-1000:])
        print("=" * 60)
        
        # Count lines and show some middle content
        lines = text_content.split('\n')
        print(f"\n5. Total lines: {len(lines)}")
        
        if len(lines) > 10:
            print("\n6. Lines 5-15:")
            print("=" * 60)
            for i in range(5, min(15, len(lines))):
                print(f"Line {i}: {lines[i]}")
            print("=" * 60)
        
        # Check for specific keywords
        keywords = ['attention', 'transformer', 'self-attention', 'encoder', 'decoder']
        print("\n7. Keyword search:")
        for keyword in keywords:
            count = text_content.lower().count(keyword.lower())
            print(f"   '{keyword}': {count} occurrences")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_pdf_content() 