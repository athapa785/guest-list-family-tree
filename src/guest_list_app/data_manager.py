"""
Data management functions for the Guest List & Family Tree application.
Handles CRUD operations, state management, and JSON serialization.
"""

import json
from dataclasses import asdict
from typing import Dict, List, Optional, Set, Tuple
import streamlit as st

from .models import Person, Relationship


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


def add_relationship(parent_id: str, child_id: str):
    """Add a parent-child relationship between two people."""
    if parent_id == child_id:
        st.warning("Parent and child cannot be the same person.")
        return
    
    # Prevent duplicates
    for r in st.session_state.rels:
        if r.parent == parent_id and r.child == child_id:
            st.info("That relationship already exists.")
            return
    
    st.session_state.rels.append(Relationship(parent=parent_id, child=child_id))


def delete_person(pid: str):
    """Delete a person and all their relationships."""
    st.session_state.people.pop(pid, None)
    st.session_state.rels = [r for r in st.session_state.rels if r.parent != pid and r.child != pid]
    if st.session_state.root == pid:
        st.session_state.root = None


def edge_list() -> List[Tuple[str, str]]:
    """Get all relationships as a list of (parent, child) tuples."""
    return [(r.parent, r.child) for r in st.session_state.rels]


def children_of(pid: str) -> List[str]:
    """Get all children of a given person."""
    return [r.child for r in st.session_state.rels if r.parent == pid]


def parents_of(pid: str) -> List[str]:
    """Get all parents of a given person."""
    return [r.parent for r in st.session_state.rels if r.child == pid]


def compute_unique_guest_count() -> int:
    """Count unique people marked invited=True; add +1 for each plus_one."""
    total = sum(1 for p in st.session_state.people.values() if p.invited)
    total += sum(1 for p in st.session_state.people.values() if p.invited and p.plus_one)
    return total


def to_json() -> str:
    """Export current state to JSON string."""
    data = {
        "people": [asdict(p) for p in st.session_state.people.values()],
        "relationships": [asdict(r) for r in st.session_state.rels],
        "root": st.session_state.root,
        "id_counter": st.session_state.id_counter,
    }
    return json.dumps(data, indent=2, ensure_ascii=False)


def from_json(text: str):
    """Import state from JSON string."""
    raw = json.loads(text)
    st.session_state.people = {p["id"]: Person(**p) for p in raw.get("people", [])}
    st.session_state.rels = [Relationship(**r) for r in raw.get("relationships", [])]
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
