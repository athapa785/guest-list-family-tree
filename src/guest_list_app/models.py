"""
Data models for the Guest List & Family Tree application.
"""

from dataclasses import dataclass


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


@dataclass
class Relationship:
    """Represents a parent-child relationship (directed edge)."""
    parent: str
    child: str
