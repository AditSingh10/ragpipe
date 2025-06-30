import urllib.request as libreq
import urllib.parse
import xml.etree.ElementTree as ET
from typing import List, Optional
from models.paper import Paper
from config.settings import Settings

class ArxivService:
    """Service for interacting with ArXiv API"""
    
    def __init__(self):
        self.base_url = Settings.ARXIV_BASE_URL
        self.pdf_base_url = Settings.ARXIV_PDF_BASE_URL
    
    def search_papers(self, query: str, max_results: int = 10, start: int = 0) -> List[Paper]:
        """
        Search for papers using arXiv API
        
        Args:
            query: Search query (e.g., "AI", "machine learning", "transformer")
            max_results: Maximum number of results to return
            start: Starting index for pagination
            
        Returns:
            List of Paper objects
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
                paper = Paper(
                    id=entry.find('.//{http://www.w3.org/2005/Atom}id').text.split('/')[-1],
                    title=entry.find('.//{http://www.w3.org/2005/Atom}title').text.strip(),
                    authors=[author.find('.//{http://www.w3.org/2005/Atom}name').text 
                             for author in entry.findall('.//{http://www.w3.org/2005/Atom}author')],
                    summary=entry.find('.//{http://www.w3.org/2005/Atom}summary').text.strip(),
                    published=entry.find('.//{http://www.w3.org/2005/Atom}published').text,
                    pdf_url=f"{self.pdf_base_url}/{entry.find('.//{http://www.w3.org/2005/Atom}id').text.split('/')[-1]}.pdf"
                )
                papers.append(paper)
            
            return papers
            
        except Exception as e:
            print(f"Error searching papers: {e}")
            return []
    
    def get_paper_by_id(self, paper_id: str) -> Optional[Paper]:
        """
        Get a specific paper by its arXiv ID
        
        Args:
            paper_id: arXiv paper ID (e.g., "2303.08774")
            
        Returns:
            Paper object or None if not found
        """
        query = f"id:{paper_id}"
        results = self.search_papers(query, max_results=1)
        
        if results:
            return results[0]
        return None 