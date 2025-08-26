"""
Data management functions for the Guest List & Family Tree application.
Handles CRUD operations, state management, and JSON serialization.
"""

import json
from dataclasses import asdict
from typing import Dict, List, Optional, Set, Tuple
import streamlit as st

from .models import Person, Relationship, RelationshipType


def init_state():
    """Initialize Streamlit session state with default values."""
    if "people" not in st.session_state:
        st.session_state.people: Dict[str, Person] = {}
    if "rels" not in st.session_state:
        st.session_state.rels: List[Relationship] = []
    if "root" not in st.session_state:
        st.session_state.root: Optional[str] = None
    if "id_counter" not in st.session_state:
        st.session_state.id_counter = 1


def new_person_id() -> str:
    """Generate a new unique person ID."""
    i = st.session_state.id_counter
    st.session_state.id_counter += 1
    return f"P{i:04d}"


def add_person(name: str, side: str = "", notes: str = "", invited: bool = True, 
               plus_one: bool = False, email: str = "", phone: str = "") -> str:
    """Add a new person to the system and return their ID."""
    pid = new_person_id()
    st.session_state.people[pid] = Person(
        id=pid, 
        name=name.strip(), 
        side=side.strip(), 
        notes=notes.strip(), 
        invited=invited, 
        plus_one=plus_one, 
        email=email.strip(), 
        phone=phone.strip()
    )
    return pid


def add_relationship(person1_id: str, person2_id: str, relationship_type: RelationshipType, notes: str = ""):
    """Add a relationship between two people."""
    if person1_id in st.session_state.people and person2_id in st.session_state.people:
        # Avoid duplicates
        for rel in st.session_state.rels:
            if ((rel.person1_id == person1_id and rel.person2_id == person2_id) or 
                (not rel.is_directed() and rel.person1_id == person2_id and rel.person2_id == person1_id)) and \
               rel.relationship_type == relationship_type:
                return
        st.session_state.rels.append(Relationship(person1_id, person2_id, relationship_type, notes))


def add_parent_child_relationship(parent_id: str, child_id: str):
    """Add a parent-child relationship (backward compatibility)."""
    add_relationship(parent_id, child_id, RelationshipType.PARENT_CHILD)


def delete_person(pid: str):
    """Delete a person and all their relationships."""
    st.session_state.people.pop(pid, None)
    st.session_state.rels = [r for r in st.session_state.rels if r.person1_id != pid and r.person2_id != pid]
    if st.session_state.root == pid:
        st.session_state.root = None


def edge_list() -> List[Tuple[str, str]]:
    """Get all parent-child relationships as a list of (parent, child) tuples."""
    return [r.get_parent_child_pair() for r in st.session_state.rels if r.is_directed() and r.get_parent_child_pair()]


def children_of(pid: str) -> List[str]:
    """Get all children of a given person."""
    return [r.person2_id for r in st.session_state.rels if r.person1_id == pid and r.is_directed()]


def parents_of(pid: str) -> List[str]:
    """Get all parents of a given person."""
    return [r.person1_id for r in st.session_state.rels if r.person2_id == pid and r.is_directed()]


def get_relationships_for_person(pid: str) -> List[Relationship]:
    """Get all relationships involving a person."""
    return [r for r in st.session_state.rels if r.person1_id == pid or r.person2_id == pid]


def get_related_people(pid: str, relationship_type: RelationshipType = None) -> List[str]:
    """Get all people related to a person, optionally filtered by relationship type."""
    related = []
    for r in st.session_state.rels:
        if relationship_type and r.relationship_type != relationship_type:
            continue
        if r.person1_id == pid:
            related.append(r.person2_id)
        elif r.person2_id == pid:
            related.append(r.person1_id)
    return related


def compute_unique_guest_count() -> int:
    """Count unique people marked invited=True; add +1 for each plus_one."""
    total = sum(1 for p in st.session_state.people.values() if p.invited)
    total += sum(1 for p in st.session_state.people.values() if p.invited and p.plus_one)
    return total


def to_json() -> str:
    """Export current state to JSON string."""
    # Convert relationships to dict with enum values as strings
    relationships_data = []
    for r in st.session_state.rels:
        rel_dict = asdict(r)
        rel_dict['relationship_type'] = r.relationship_type.value  # Convert enum to string
        relationships_data.append(rel_dict)
    
    data = {
        "people": [asdict(p) for p in st.session_state.people.values()],
        "relationships": relationships_data,
        "root": st.session_state.root,
        "id_counter": st.session_state.id_counter,
    }
    return json.dumps(data, indent=2, ensure_ascii=False)


def from_json(text: str):
    """Import state from JSON string."""
    raw = json.loads(text)
    
    # Load people
    st.session_state.people = {p["id"]: Person(**p) for p in raw.get("people", [])}
    
    # Load relationships with proper enum conversion
    st.session_state.rels = []
    for r_data in raw.get("relationships", []):
        # Handle both old and new relationship formats
        if "parent" in r_data and "child" in r_data:
            # Old format - convert to new format
            rel = Relationship(
                person1_id=r_data["parent"],
                person2_id=r_data["child"],
                relationship_type=RelationshipType.PARENT_CHILD,
                notes=r_data.get("notes", "")
            )
        else:
            # New format
            rel_type = RelationshipType(r_data["relationship_type"]) if isinstance(r_data["relationship_type"], str) else r_data["relationship_type"]
            rel = Relationship(
                person1_id=r_data["person1_id"],
                person2_id=r_data["person2_id"],
                relationship_type=rel_type,
                notes=r_data.get("notes", "")
            )
        st.session_state.rels.append(rel)
    
    st.session_state.root = raw.get("root")
    st.session_state.id_counter = int(raw.get("id_counter", max([int(pid[1:]) for pid in st.session_state.people.keys()], default=0) + 1))


def update_person_from_table_row(person: Person, row) -> None:
    """Update a person's attributes from a table row."""
    person.name = str(row.get("Name", "")).strip()
    person.side = str(row.get("Side", "")).strip()
    person.invited = bool(row.get("Invited", False))
    person.plus_one = bool(row.get("Plus One", False))
    person.email = str(row.get("Email", "")).strip()
    person.phone = str(row.get("Phone", "")).strip()
    person.notes = str(row.get("Notes", "")).strip()


def process_table_edits(edited_df) -> None:
    """Process edits from the data editor table."""
    existing_ids = set(st.session_state.people.keys())
    seen_ids: Set[str] = set()

    for _, row in edited_df.iterrows():
        rid = str(row.get("ID", "")).strip()
        name = str(row.get("Name", "")).strip()
        if not name:
            continue  # ignore incomplete rows

        if rid and rid in st.session_state.people:
            # Update existing person
            update_person_from_table_row(st.session_state.people[rid], row)
            seen_ids.add(rid)
        else:
            # New row -> add new person
            pid = add_person(
                name=name,
                side=str(row.get("Side", "")).strip(),
                invited=bool(row.get("Invited", True)),
                plus_one=bool(row.get("Plus One", False)),
                email=str(row.get("Email", "")).strip(),
                phone=str(row.get("Phone", "")).strip(),
                notes=str(row.get("Notes", "")).strip(),
            )
            seen_ids.add(pid)

    # Remove any people that were deleted in the editor
    to_remove = existing_ids - seen_ids
    if to_remove:
        for rid in to_remove:
            delete_person(rid)
        st.info(f"Removed {len(to_remove)} entr{'y' if len(to_remove)==1 else 'ies'} based on table edits.")
