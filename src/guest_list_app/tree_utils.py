"""
Tree-specific utilities for the Guest List & Family Tree application.
Handles tree layout computation and graph operations.
"""

from typing import Dict, List, Optional
import streamlit as st

from .data_manager import edge_list, parents_of


def compute_layout_levels(root_id: Optional[str]) -> Dict[str, int]:
    """
    Simple BFS levels from root to help group nodes in Graphviz rank by generation.
    If root is None, try to infer nodes with no parents as roots and choose arbitrarily.
    """
    graph = edge_list()
    rev_parents = {}
    for p, c in graph:
        rev_parents.setdefault(c, []).append(p)

    nodes = list(st.session_state.people.keys())
    if not nodes:
        return {}

    roots: List[str] = []
    for n in nodes:
        if len(rev_parents.get(n, [])) == 0:
            roots.append(n)

    if root_id and root_id in nodes:
        start = root_id
    elif roots:
        start = roots[0]
    else:
        start = nodes[0]

    # BFS from start
    levels = {start: 0}
    queue = [start]
    while queue:
        current = queue.pop(0)
        current_level = levels[current]
        
        # Find children
        for parent, child in graph:
            if parent == current and child not in levels:
                levels[child] = current_level + 1
                queue.append(child)

    # Handle disconnected components
    for n in nodes:
        if n not in levels:
            levels[n] = 0

    return levels


def create_family_tree_graph() -> 'graphviz.Digraph':
    """Create a Graphviz digraph for the family tree visualization."""
    import graphviz
    
    g = graphviz.Digraph("FamilyTree", format="svg")
    g.attr(rankdir="TB", fontsize="10")

    # Add nodes with styling
    for pid, person in st.session_state.people.items():
        label = f"{person.name}"
        if person.side:
            label += f"\\n({person.side})"
        
        # Color coding
        if person.invited:
            color = "lightblue" if not person.plus_one else "lightgreen"
        else:
            color = "lightgray"
        
        g.node(pid, label=label, style="filled", fillcolor=color, fontsize="9")

    # Add edges
    for rel in st.session_state.rels:
        g.edge(rel.parent, rel.child)

    # Rank by levels to keep generations aligned
    levels = compute_layout_levels(st.session_state.root)
    by_level: Dict[int, List[str]] = {}
    for nid, lvl in levels.items():
        by_level.setdefault(lvl, []).append(nid)

    for lvl, nodes in by_level.items():
        with g.subgraph() as s:
            s.attr(rank="same")
            for n in nodes:
                s.node(n)

    return g
