"""
User session model for managing user state
"""

from dataclasses import dataclass, field
from typing import Dict, Any
from datetime import datetime
from .conversation import Conversation

@dataclass
class UserSession:
    """Represents a user session with conversation and preferences"""
    user_id: str
    current_conversation: Conversation
    preferences: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    last_active: datetime = field(default_factory=datetime.now)
    
    def update_activity(self):
        """Update last active timestamp"""
        # TODO: Implement activity tracking
        pass
    
    def get_preference(self, key: str, default: Any = None) -> Any:
        """Get a user preference"""
        # TODO: Implement preference retrieval
        pass
    
    def set_preference(self, key: str, value: Any):
        """Set a user preference"""
        # TODO: Implement preference setting
        pass 