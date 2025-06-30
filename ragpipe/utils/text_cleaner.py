import re

class TextCleaner:
    """Utility class for cleaning extracted text from PDFs"""
    
    @staticmethod
    def clean_pdf_text(text: str) -> str:
        """
        Clean extracted text from PDF
        
        Args:
            text: Raw text from PDF
            
        Returns:
            Cleaned text
        """
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove page numbers and headers
        text = re.sub(r'\bpage\s+\d+\b', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\b\d+\s*of\s*\d+\b', '', text)
        
        # Remove unreadable characters, keep only readable ones
        text = re.sub(r'[^\w\s\.\,\;\:\!\?\-\(\)\[\]\{\}]', ' ', text)
        
        # Clean up whitespace again
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        return text 