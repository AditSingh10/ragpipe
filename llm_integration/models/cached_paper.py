"""
Cached paper model for storing retrieved papers
"""

from dataclasses import dataclass, field
from typing import List
from datetime import datetime

@dataclass
class CachedPaper:
    """Represents a paper cached for quick access"""
    paper_id: str
    title: str
    authors: List[str]
    summary: str
    text_content: str
    pdf_path: str
    relevance_score: float
    cached_at: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    last_accessed: datetime = field(default_factory=datetime.now)
    
    def increment_access(self):
        """Increment access count and update last accessed time"""
        # TODO: Implement access tracking
        pass
    
    def get_formatted_authors(self) -> str:
        """Get authors as formatted string"""
        # TODO: Implement author formatting
        pass
    
    def get_short_title(self, max_length: int = 50) -> str:
        """Get truncated title for display"""
        # TODO: Implement title truncation
        pass 