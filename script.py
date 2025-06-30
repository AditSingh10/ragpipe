from dotenv import load_dotenv
import urllib.request as libreq
import urllib.parse
import xml.etree.ElementTree as ET
import os
import time
from typing import Optional, Dict, Any, List, Union
import PyPDF2 as pypdf
import re
import urllib.request
from pinecone import QueryResponse, Pinecone
from sentence_transformers import SentenceTransformer

# TODO ERROR HANDLING
class ArxivAPI:
    """A class to interact with the arXiv API for retrieving papers"""
    
    load_dotenv()
    PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
    PINECONE_ENVIRONMENT = os.getenv('ENVIRONMENT')
    PINECONE_INDEX_NAME = os.getenv('INDEX')

    def __init__(self):
        # stems for API urls
        self.base_url = "http://export.arxiv.org/api/query"
        self.pdf_base_url = "https://arxiv.org/pdf"
        
        # Initialize embedding model and Pinecone
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.pc = Pinecone(api_key=self.PINECONE_API_KEY)
        self.index = self.pc.Index(self.PINECONE_INDEX_NAME)
    
 
    def search_papers(self, query: str, max_results: int = 10, start: int = 0) -> List[Dict]:
        """
        Search for papers using arXiv API
        
        Args:
            query: Search query (e.g., "AI", "machine learning", "transformer")
            max_results: Maximum number of results to return
            start: Starting index for pagination
            
        Returns:
            List of paper dictionaries
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
            
            return papers
            
        except Exception as e:
            print(f"Error searching papers: {e}")
            return []
    
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
        
        if results:
            return results[0]
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
        """
        Process multiple papers and prepare them to augment prompt
        
        Args:
            query: Search query
            max_papers: max_papers to prepare and process
            
        Returns:
            List of papers and their contents
        """
        # 1. Search for papers
        # 2. For each paper: download → extract → clean → store
        # 3. Return list of papers with their text content and other metadata

        search_result = self.search_papers(query, max_papers)
        paper_list = []

        for paper in search_result:
            # download paper for processing using its id
            pdf_path = self.download_paper_pdf(paper['id'])
            # extract and clean
            cleaned_text  = self.extract_text_from_pdf_and_clean(pdf_path)
            paper['pdf_path'] = pdf_path
            paper['text_content'] = cleaned_text
            paper_list.append(paper)
        return paper_list
    
    def add_papers_to_pinecone(self, papers_list):
        '''
        Convert papers to embeddings and add to vector database

        Args:
            papers_list: List of Dicts with metadata for each paper
        '''
        # store vectors for upsert into vector db
        vectors = []
        # we are getting a list of dictionaries
        for paper in papers_list:
            # get the embedding
            embedding = self.embedding_model.encode(paper['text_content'])
            # prepare for upsert into vector database using paper id as vector ID
            vectors.append((paper['id'], embedding.tolist(),
                           {
                               'title': paper['title'],
                               'authors': paper['authors'],
                               'summary': paper['summary'],
                               'pdf_url': paper['pdf_url']
                           }))
        # batch upsert
        self.index.upsert(vectors=vectors)


    def search_pinecone(self, query: str, max_results: int=5) -> QueryResponse:
        """
        Search existing papers in vector db
        """
        # Search existing papers in Pinecone
        # Convert query to embedding
        query_embedding = self.embedding_model.encode(query).tolist()
        results = self.index.query(
            vector=query_embedding,
            top_k=max_results,
            include_metadata=True
        )

        return results

    def assess_search_quality(self, results: QueryResponse, query:str, threshold: float = 0.8) -> tuple[bool, Union[str, Dict]]:
        """
        Assess if search results are good enough
        """
        if not results.matches:
            return False, "No results found"
    
        # Get similarity scores
        scores = [match.score for match in results.matches]
        avg_score = sum(scores) / len(scores)
        max_score = max(scores)
        
        # Quality criteria
        quality_metrics = {
            'avg_similarity': avg_score,
            'max_similarity': max_score,
            'num_results': len(results.matches),
            'threshold_met': max_score >= threshold
        }
        
        # make the decision
        is_good_enough = (
            max_score >= threshold and  # At least one very relevant result
            avg_score >= 0.75 and       # Overall relevance is decent
            len(results.matches) >= 2   # Have multiple results
        )
        
        return is_good_enough, quality_metrics    

    
    def rag_query(self, user_query, max_results=5):
        # Search Pinecone first
        query_response = self.search_pinecone(user_query, max_results)
        eval = self.assess_search_quality(query_response, user_query)
        # If not enough results, search arXiv
        if eval[0] == False:
            #modify search_papers to do cleaning, processing etc
            papers_list=self.process_papers_for_rag(user_query, max_results)
            # Add new papers to Pinecone
            self.add_papers_to_pinecone(papers_list)
            return papers_list
        else:
            # use db papers for augmenting prompt
            papers_list = []
            for match in query_response.matches:
                paper = {
                    'id': match.id,
                    'score': match.score,
                    'title': match.metadata['title'],
                    'authors': match.metadata['authors'],
                    'summary': match.metadata['summary'],
                    'text_content': match.metadata['text_content'],
                    'pdf_url': match.metadata['pdf_url']
                }
                papers_list.append(paper)
            return papers_list
        
            
    

def main():
    """Main function to test all functionality"""
    print("=== Testing ArXiv RAG Pipeline ===\n")
    
    # Test 1: Connections
    api = ArxivAPI()
    print("✅ ArXiv API and Pinecone connections working")
    
    # Test 2: ArXiv Search
    print("\n=== Testing ArXiv Search ===")
    results = api.search_papers("transformer", max_results=3)
    print(f"Found {len(results)} papers")
    for paper in results:
        print(f"- {paper['title'][:50]}...")
    
    # Test 3: PDF Processing
    print("\n=== Testing PDF Processing ===")
    papers = api.process_papers_for_rag("AI", max_papers=1)
    if papers:
        paper = papers[0]
        print(f"✅ Processed: {paper['title']}")
        print(f"Text length: {len(paper['text_content'])} characters")
        print(f"First 200 chars: {paper['text_content'][:200]}...")
    
    # Test 4: Vector Database
    print("\n=== Testing Vector Database ===")
    if papers:
        api.add_papers_to_pinecone(papers)
        print("✅ Papers added to Pinecone")
        
        # Test search
        results = api.search_pinecone("transformer architecture")
        print(f"✅ Vector search found {len(results.matches)} results")
        for match in results.matches:
            print(f"- {match.metadata['title'][:50]}... (score: {match.score:.3f})")
    
    # Test 5: Complete RAG Pipeline
    print("\n=== Testing Complete RAG Pipeline ===")
    results = api.rag_query("transformer architecture improvements", max_results=3)
    print(f"✅ RAG query returned {len(results)} papers")
    for paper in results:
        print(f"- {paper['title'][:50]}... (score: {paper.get('score', 'N/A')})")
    
    print("\n=== Testing Complete ===")

if __name__ == "__main__":
    main()
