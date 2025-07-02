"""
Conversation model for managing chat history
"""

from dataclasses import dataclass, field
from typing import List
from datetime import datetime

@dataclass
class Message:
    """Represents a single message in a conversation"""
    content: str
    sender: str  # 'user' or 'assistant'
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class Conversation:
    """Represents a conversation between user and assistant"""
    user_id: str
    messages: List[Message] = field(default_factory=list)
    cached_papers: List['CachedPaper'] = field(default_factory=list)  # Forward reference
    use_rag: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def add_message(self, content: str, sender: str):
        """Add a new message to the conversation"""
        # TODO: Implement message addition logic
        pass
    
    def get_recent_messages(self, count: int = 10) -> List[Message]:
        """Get the most recent messages"""
        # TODO: Implement recent messages retrieval
        pass 