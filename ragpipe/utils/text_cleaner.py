import re

class TextCleaner:
    """Utility class for cleaning extracted text from PDFs"""
    
    @staticmethod
    def clean_pdf_text(text: str) -> str:
        """
        Clean extracted text from PDF with robust formatting fixes
        
        Args:
            text: Raw text from PDF
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Step 1: Normalize line breaks
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        
        # Step 2: Remove page numbers and headers
        text = re.sub(r'\bpage\s+\d+\b', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\b\d+\s*of\s*\d+\b', '', text)
        
        # Step 3: Fix broken words (words split across lines)
        # Look for patterns like "word\nword" and join them
        text = re.sub(r'(\w+)\n(\w+)', r'\1\2', text)
        
        # Step 4: Fix hyphenated words at line breaks
        text = re.sub(r'(\w+)-\n(\w+)', r'\1\2', text)
        
        # Step 5: Remove excessive whitespace and normalize spacing
        # Replace multiple spaces/tabs with single space
        text = re.sub(r'[ \t]+', ' ', text)
        
        # Step 6: Fix broken sentences and paragraphs
        # Join lines that end with lowercase letters (likely broken sentences)
        text = re.sub(r'([a-z])\n([a-z])', r'\1 \2', text)
        
        # Step 7: Clean up punctuation spacing
        # Fix spacing around punctuation
        text = re.sub(r'\s+([.,;:!?])', r'\1', text)
        text = re.sub(r'([.,;:!?])\s*([A-Z])', r'\1 \2', text)
        
        # Step 8: Remove unreadable characters but keep important ones
        # Keep letters, numbers, spaces, punctuation, and newlines
        text = re.sub(r'[^\w\s\.\,\;\:\!\?\-\(\)\[\]\{\}\n]', ' ', text)
        
        # Step 9: Fix common PDF artifacts
        # Remove single characters on their own line (likely artifacts)
        text = re.sub(r'\n\s*\w\s*\n', '\n', text)
        
        # Step 10: Clean up paragraph structure
        # Replace multiple newlines with double newlines (paragraph breaks)
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        
        # Step 11: Fix spacing around newlines
        text = re.sub(r'\n\s+', '\n', text)
        text = re.sub(r'\s+\n', '\n', text)
        
        # Step 12: Remove empty lines at start and end
        text = re.sub(r'^\s*\n+', '', text)
        text = re.sub(r'\n+\s*$', '', text)
        
        # Step 13: Final cleanup - normalize spaces and trim
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        # Step 14: Fix common academic paper formatting issues
        # Remove figure/table references that are on their own line
        text = re.sub(r'\n\s*(Figure|Table)\s+\d+.*?\n', '\n', text, flags=re.IGNORECASE)
        
        # Step 15: Fix broken mathematical expressions
        # Join broken mathematical terms
        text = re.sub(r'(\w+)\s*\n\s*(\d+)', r'\1\2', text)
        
        return text
    
    @staticmethod
    def clean_for_display(text: str) -> str:
        """
        Additional cleaning for display purposes
        
        Args:
            text: Already cleaned text
            
        Returns:
            Text ready for display
        """
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Fix sentence endings
        text = re.sub(r'\s+([.!?])\s*([A-Z])', r'\1 \2', text)
        
        # Clean up bullet points and lists
        text = re.sub(r'\s*\•\s*', '\n• ', text)
        
        return text.strip() 