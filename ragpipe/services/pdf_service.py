import os
import urllib.request
import PyPDF2 as pypdf
from typing import List, Optional
from models.paper import Paper
from utils.text_cleaner import TextCleaner
from config.settings import Settings

class PDFService:
    """Service for handling PDF operations"""
    
    def __init__(self):
        self.download_dir = Settings.DOWNLOAD_DIR
        self.text_cleaner = TextCleaner()
    
    def download_paper_pdf(self, paper: Paper) -> Optional[str]:
        """
        Download the PDF of a paper
        
        Args:
            paper: Paper object
            
        Returns:
            Path to downloaded PDF or None if failed
        """
        # Create output directory if it doesn't exist
        os.makedirs(self.download_dir, exist_ok=True)
        
        output_path = os.path.join(self.download_dir, f"{paper.id}.pdf")
        
        try:
            print(f"Downloading PDF from: {paper.pdf_url}")
            print(f"Saving to: {output_path}")
            
            # Download the PDF
            urllib.request.urlretrieve(paper.pdf_url, output_path)
            
            # Check if file was downloaded successfully
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                print(f"Successfully downloaded: {output_path}")
                return output_path
            else:
                print("Download failed - file is empty or doesn't exist")
                return None
                
        except Exception as e:
            print(f"Error downloading PDF: {e}")
            return None
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text from PDF
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Extracted and cleaned text
        """
        try:
            with open(pdf_path, 'rb') as file:
                reader = pypdf.PdfReader(file)
                data = ""
                for page in reader.pages:
                    curr_text = page.extract_text()
                    data += curr_text
                
                # Clean the extracted text
                return self.text_cleaner.clean_pdf_text(data)
                
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            return ""
    
    def process_papers(self, papers: List[Paper]) -> List[Paper]:
        """
        Process multiple papers: download PDFs and extract text
        
        Args:
            papers: List of Paper objects
            
        Returns:
            List of Paper objects with text_content and pdf_path populated
        """
        processed_papers = []
        
        for paper in papers:
            # Download PDF
            pdf_path = self.download_paper_pdf(paper)
            if pdf_path:
                # Extract and clean text
                text_content = self.extract_text_from_pdf(pdf_path)
                
                # Update paper with extracted content
                paper.pdf_path = pdf_path
                paper.text_content = text_content
                processed_papers.append(paper)
            else:
                print(f"Failed to download PDF for paper {paper.id}")
        
        return processed_papers 