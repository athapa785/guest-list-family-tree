"""
UI components for the Guest List & Family Tree application.
Contains reusable Streamlit UI functions.
"""

import pandas as pd
import streamlit as st
from typing import Dict, List

from .data_manager import (
    add_person, add_relationship, delete_person, 
    compute_unique_guest_count, to_json, from_json,
    process_table_edits
)
from .tree_utils import create_family_tree_graph


def render_sidebar():
    """Render the sidebar with save/load functionality and root selection."""
    with st.sidebar:
        st.header("📁 Save / Load")
        
        # Export
        if st.session_state.people:
            json_data = to_json()
            st.download_button(
                "⬇️ Export JSON", 
                json_data, 
                "family_tree.json", 
                "application/json"
            )
        
        # Import
        uploaded = st.file_uploader("📤 Import JSON", type=["json"])
        if uploaded:
            try:
                content = uploaded.read().decode("utf-8")
                from_json(content)
                st.success("✅ Imported successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Import failed: {e}")
        
        st.markdown("---")
        
        # Root selection
        st.header("🌳 Tree Root")
        if st.session_state.people:
            all_opts = {"(auto)": None}
            all_opts.update({f"{p.name} ({pid})": pid for pid, p in st.session_state.people.items()})
            selected = st.selectbox("Choose a root for the tree (optional)", list(all_opts.keys()))
            st.session_state.root = all_opts[selected]


def render_add_person_form():
    """Render the form for adding new people."""
    st.subheader("➕ Add Person")
    with st.form("add_person_form", clear_on_submit=True):
        name = st.text_input("Full name *")
        side = st.text_input("Side / Group (e.g., Bride, Groom, Family, Friend)")
        col1, col2 = st.columns(2)
        with col1:
            invited = st.checkbox("On guest list", value=True)
        with col2:
            plus_one = st.checkbox("Plus one allowed")
        
        email = st.text_input("Email")
        phone = st.text_input("Phone")
        notes = st.text_area("Notes")
        
        if st.form_submit_button("Add Person"):
            if name.strip():
                add_person(name, side, notes, invited, plus_one, email, phone)
                st.success(f"Added {name}!")
            else:
                st.error("Name is required.")


def render_add_relationship_form():
    """Render the form for adding relationships."""
    st.subheader("👨‍👩‍👧‍👦 Add Relationship")
    
    if len(st.session_state.people) >= 2:
        people_opts = {f"{p.name} ({pid})": pid for pid, p in st.session_state.people.items()}
        
        parent_choice = st.selectbox("Parent", options=list(people_opts.keys()))
        child_choice = st.selectbox("Child", options=list(people_opts.keys()))
        
        if st.button("Add Relationship"):
            add_relationship(people_opts[parent_choice], people_opts[child_choice])
    else:
        st.info("Add people first to create relationships.")


def render_delete_person_section():
    """Render the section for deleting people."""
    st.markdown("---")
    st.subheader("🗑️ Delete Person")
    
    if st.session_state.people:
        del_choice = st.selectbox(
            "Choose person to delete", 
            options=["(none)"] + list(st.session_state.people.keys()),
            format_func=lambda pid: "(none)" if pid == "(none)" else f"{st.session_state.people[pid].name} ({pid})"
        )
        if del_choice != "(none)" and st.button("Delete Selected"):
            delete_person(del_choice)
            st.success("Deleted.")


def render_metrics():
    """Render the metrics display."""
    total_people = len(st.session_state.people)
    total_invited = sum(1 for p in st.session_state.people.values() if p.invited)
    total_with_plus_ones = compute_unique_guest_count()

    m1, m2, m3 = st.columns(3)
    m1.metric("Total People", total_people)
    m2.metric("On Guest List", total_invited)
    m3.metric("Guest Count (+1s)", total_with_plus_ones)


def render_tree_view():
    """Render the family tree visualization."""
    g = create_family_tree_graph()
    st.graphviz_chart(g)


def render_table_view():
    """Render the editable table view."""
    # Create DataFrame from people data
    df = pd.DataFrame([
        {
            "ID": p.id,
            "Name": p.name,
            "Side": p.side,
            "Invited": p.invited,
            "Plus One": p.plus_one,
            "Email": p.email,
            "Phone": p.phone,
            "Notes": p.notes
        } for p in st.session_state.people.values()
    ]).sort_values(by=["Side", "Name"]).reset_index(drop=True)

    # Render editable table
    edited = st.data_editor(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Invited": st.column_config.CheckboxColumn(),
            "Plus One": st.column_config.CheckboxColumn(),
            "Notes": st.column_config.TextColumn(width="medium"),
            "Email": st.column_config.TextColumn(width="medium"),
            "Phone": st.column_config.TextColumn(width="small"),
        },
        num_rows="dynamic",
    )

    # Process any edits
    process_table_edits(edited)


def render_guest_list_export():
    """Render the guest list export section."""
    st.markdown("---")
    st.subheader("📝 Quick Guest List Export")
    
    incl_only = st.checkbox("Include invited-only", value=True)
    data = []
    
    for p in st.session_state.people.values():
        if incl_only and not p.invited:
            continue
        data.append({
            "Name": p.name,
            "Side": p.side,
            "Email": p.email,
            "Phone": p.phone,
            "Notes": p.notes,
            "PlusOne": "Yes" if (p.invited and p.plus_one) else "No"
        })
    
    export_df = pd.DataFrame(data)
    if not export_df.empty:
        export_df = export_df.sort_values(by=["Side", "Name"]).reset_index(drop=True)
    st.dataframe(export_df, use_container_width=True)
    st.download_button(
        "⬇️ Download Guest List (CSV)", 
        export_df.to_csv(index=False), 
        "guest_list.csv", 
        "text/csv"
    )
