from typing import List, Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class Paper:
    """A class to represent an academic paper"""
    
    id: str
    title: str
    authors: List[str]
    summary: str
    published: str
    pdf_url: str
    text_content: str = ""
    pdf_path: str = ""
    score: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert paper to dictionary format"""
        return {
            'id': self.id,
            'title': self.title,
            'authors': self.authors,
            'summary': self.summary,
            'published': self.published,
            'pdf_url': self.pdf_url,
            'text_content': self.text_content,
            'pdf_path': self.pdf_path,
            'score': self.score
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Paper':
        """Create paper from dictionary"""
        return cls(
            id=data['id'],
            title=data['title'],
            authors=data['authors'],
            summary=data['summary'],
            published=data['published'],
            pdf_url=data['pdf_url'],
            text_content=data.get('text_content', ''),
            pdf_path=data.get('pdf_path', ''),
            score=data.get('score', 0.0)
        )
    
    def get_short_title(self, max_length: int = 50) -> str:
        """Get truncated title for display"""
        return self.title[:max_length] + "..." if len(self.title) > max_length else self.title
    
    def get_authors_string(self) -> str:
        """Get authors as comma-separated string"""
        return ", ".join(self.authors) 