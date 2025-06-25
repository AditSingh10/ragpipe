import urllib.request as libreq
import urllib.parse
import xml.etree.ElementTree as ET
import os
import time
from typing import Optional, Dict, Any
import PyPDF2 as pypdf
import re

class ArxivAPI:
    """A class to interact with the arXiv API for retrieving papers"""
    
    def __init__(self):
        # stems for API urls
        self.base_url = "http://export.arxiv.org/api/query"
        self.pdf_base_url = "https://arxiv.org/pdf"
    
 
    def search_papers(self, query: str, max_results: int = 10, start: int = 0) -> Dict[str, Any]:
        """
        Search for papers using arXiv API
        
        Args:
            query: Search query (e.g., "AI", "machine learning", "transformer")
            max_results: Maximum number of results to return
            start: Starting index for pagination
            
        Returns:
            Dictionary containing search results
        """
        # Build the query URL
        params = {
            'search_query': query,
            'start': start,
            'max_results': max_results,
            'sortBy': 'relevance',
            'sortOrder': 'descending'
        }
        
        query_string = urllib.parse.urlencode(params)
        url = f"{self.base_url}?{query_string}"
        
        try:
            with libreq.urlopen(url) as response:
                xml_data = response.read()
                
            # Parse XML response
            root = ET.fromstring(xml_data)
            
            # Extract papers
            papers = []
            for entry in root.findall('.//{http://www.w3.org/2005/Atom}entry'):
                paper = {
                    'title': entry.find('.//{http://www.w3.org/2005/Atom}title').text.strip(),
                    'authors': [author.find('.//{http://www.w3.org/2005/Atom}name').text 
                               for author in entry.findall('.//{http://www.w3.org/2005/Atom}author')],
                    'summary': entry.find('.//{http://www.w3.org/2005/Atom}summary').text.strip(),
                    'id': entry.find('.//{http://www.w3.org/2005/Atom}id').text.split('/')[-1],
                    'published': entry.find('.//{http://www.w3.org/2005/Atom}published').text,
                    'pdf_url': f"{self.pdf_base_url}/{entry.find('.//{http://www.w3.org/2005/Atom}id').text.split('/')[-1]}.pdf"
                }
                papers.append(paper)
            
            return {
                'total_results': len(papers),
                'papers': papers
            }
            
        except Exception as e:
            print(f"Error searching papers: {e}")
            return {'total_results': 0, 'papers': []}
    
    def get_paper_by_id(self, paper_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific paper by its arXiv ID
        
        Args:
            paper_id: arXiv paper ID (e.g., "2303.08774")
            
        Returns:
            Paper information or None if not found
        """
        query = f"id:{paper_id}"
        results = self.search_papers(query, max_results=1)
        
        if results['papers']:
            return results['papers'][0]
        return None
    
    def download_paper_pdf(self, paper_id: str, output_dir: str = "downloads") -> Optional[str]:
        """
        Download the PDF of a paper
        
        Args:
            paper_id: arXiv paper ID
            output_dir: Directory to save the PDF
            
        Returns:
            Path to downloaded PDF or None if failed
        """
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        pdf_url = f"{self.pdf_base_url}/{paper_id}.pdf"
        output_path = os.path.join(output_dir, f"{paper_id}.pdf")
        
        try:
            print(f"Downloading PDF from: {pdf_url}")
            print(f"Saving to: {output_path}")
            
            # Download the PDF
            urllib.request.urlretrieve(pdf_url, output_path)
            
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
        
        # TODO ERROR HANDLING
    def extract_text_from_pdf_and_clean(self, pdf_path: str) -> str:
        """
        Extract texts from pdf 
        
        Args:
            pdf_path: Path to pdf
            
        Returns:
            String containing text from all pages 
        """
        # Open pdf from path parameter and create text string
        with open(pdf_path, 'rb') as file:
            reader = pypdf.PdfReader(file)
            data = ""
            for page in reader.pages:
                curr_text = page.extract_text()
                data += curr_text
             
            # Cleaning
            data = re.sub(r'\s+', ' ', data)
            # Remove page numbers and headers, footers, unreadable chars, etc
            data = re.sub(r'\bpage\s+\d+\b', '', data, flags=re.IGNORECASE)
            data = re.sub(r'\b\d+\s*of\s*\d+\b', '', data)
            data = re.sub(r'[^\w\s\.\,\;\:\!\?\-\(\)\[\]\{\}]', ' ', data)
            data = re.sub(r'\s+', ' ', data)
            data = data.strip()

            return data
    def process_papers_for_rag(self, query: str, max_papers: int = 5) -> List[Dict]:
        pass

def main():
    """Main function to demonstrate example arXiv API usage"""
    api = ArxivAPI()
    
    print("=== arXiv API Paper Retrieval for AI Testing ===\n")
    
    # Example 1: Search for recent AI papers
    print("1. Searching for recent AI papers...")
    ai_papers = api.search_papers("AI", max_results=5)
    
    if ai_papers['papers']:
        print(f"Found {ai_papers['total_results']} papers:")
        for i, paper in enumerate(ai_papers['papers'], 1):
            print(f"\n{i}. {paper['title']}")
            print(f"   Authors: {', '.join(paper['authors'])}")
            print(f"   ID: {paper['id']}")
            print(f"   Published: {paper['published'][:10]}")
            print(f"   PDF: {paper['pdf_url']}")

if __name__ == "__main__":
    main()
