#!/usr/bin/env python3
"""
Test script for paper structure detection
"""

import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ragpipe.services.paper_structure_detector import PaperStructureDetector
from ragpipe.services.pdf_service import PDFService
from ragpipe.models.paper import Paper

def test_structure_detection():
    """Test the paper structure detection with the attention paper"""
    
    print("=== Testing Paper Structure Detection ===\n")
    
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
    
    # Initialize services
    pdf_service = PDFService()
    structure_detector = PaperStructureDetector()
    
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
        
        print("\n3. Detecting paper structure...")
        structure = structure_detector.detect_structure(text_content)
        
        print(f"   ✅ Structure detected!")
        print(f"   Title: {structure.title}")
        print(f"   Abstract: {'Found' if structure.abstract else 'Not found'}")
        print(f"   Sections: {len(structure.sections)}")
        print(f"   References: {'Found' if structure.references else 'Not found'}")
        print(f"   Appendices: {len(structure.appendices)}")
        
        if structure.sections:
            print("\n4. Detected sections:")
            for i, section in enumerate(structure.sections[:10]):  # Show first 10
                print(f"   {i+1}. Level {section.level}: {section.title}")
                print(f"      Content preview: {section.content[:100]}...")
                print(f"      Position: {section.start_index} - {section.end_index}")
                print()
        
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
        
        3. Model Architecture
        Most competitive neural sequence transduction models have an encoder-decoder structure.
        """
        
        sample_structure = structure_detector.detect_structure(sample_text)
        print(f"   Sample text sections: {len(sample_structure.sections)}")
        for section in sample_structure.sections:
            print(f"     Level {section.level}: {section.title}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_structure_detection()
