"""
Data models for the Guest List & Family Tree application.
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Any


class RelationshipType(Enum):
    """Types of relationships between people."""
    PARENT_CHILD = "parent_child"
    PARTNER = "partner"
    SPOUSE = "spouse"
    FRIEND = "friend"
    ACQUAINTANCE = "acquaintance"
    SIBLING = "sibling"
    
    @classmethod
    def get_display_names(cls) -> Dict[str, str]:
        return {
            cls.PARENT_CHILD.value: "Parent-Child",
            cls.PARTNER.value: "Partner",
            cls.SPOUSE.value: "Spouse",
            cls.FRIEND.value: "Friend",
            cls.ACQUAINTANCE.value: "Acquaintance",
            cls.SIBLING.value: "Sibling"
        }


@dataclass
class Person:
    """Represents a person in the guest list and family tree."""
    id: str
    name: str
    side: str = ""          # e.g., "Bride", "Groom", "Family", "Friend"
    notes: str = ""
    invited: bool = True    # on the guest list toggle
    plus_one: bool = False
    email: str = ""
    phone: str = ""
    expanded: bool = False  # for table expand/collapse functionality
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert person to dictionary for table display."""
        return {
            "ID": self.id,
            "Name": self.name,
            "Side": self.side,
            "Invited": self.invited,
            "Plus One": self.plus_one,
            "Email": self.email,
            "Phone": self.phone,
            "Notes": self.notes,
            "Expanded": self.expanded
        }


@dataclass
class Relationship:
    """Represents a relationship between two people."""
    person1_id: str
    person2_id: str
    relationship_type: RelationshipType
    notes: str = ""
    
    def __post_init__(self):
        if isinstance(self.relationship_type, str):
            self.relationship_type = RelationshipType(self.relationship_type)
    
    def get_display_name(self) -> str:
        """Get human-readable relationship name."""
        return RelationshipType.get_display_names()[self.relationship_type.value]
    
    def is_directed(self) -> bool:
        """Check if relationship is directed (parent-child)."""
        return self.relationship_type == RelationshipType.PARENT_CHILD
    
    def get_parent_child_pair(self) -> tuple:
        """For parent-child relationships, return (parent_id, child_id)."""
        if self.relationship_type == RelationshipType.PARENT_CHILD:
            return (self.person1_id, self.person2_id)
        return None
