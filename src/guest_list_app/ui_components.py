"""
UI components for the Guest List & Family Tree application.
Contains reusable Streamlit UI functions.
"""

import pandas as pd
import streamlit as st
from typing import Dict, List
from st_aggrid import AgGrid, GridOptionsBuilder, DataReturnMode, GridUpdateMode, ColumnsAutoSizeMode

from .data_manager import (
    add_person, add_relationship, add_parent_child_relationship, delete_person, 
    compute_unique_guest_count, to_json, from_json,
    process_table_edits, get_relationships_for_person, get_related_people
)
from .models import RelationshipType
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
        
        # Relationship type selection
        relationship_types = RelationshipType.get_display_names()
        rel_type_display = st.selectbox("Relationship Type", list(relationship_types.values()))
        rel_type = next(k for k, v in relationship_types.items() if v == rel_type_display)
        
        # Person selection based on relationship type
        if RelationshipType(rel_type) == RelationshipType.PARENT_CHILD:
            person1_label = "Parent"
            person2_label = "Child"
        else:
            person1_label = "Person 1"
            person2_label = "Person 2"
            
        person1_choice = st.selectbox(person1_label, options=list(people_opts.keys()))
        person2_choice = st.selectbox(person2_label, options=list(people_opts.keys()))
        
        notes = st.text_area("Notes (optional)", placeholder="Additional notes about this relationship...")
        
        if st.button("Add Relationship"):
            if people_opts[person1_choice] == people_opts[person2_choice]:
                st.error("Cannot create a relationship between the same person.")
            else:
                add_relationship(people_opts[person1_choice], people_opts[person2_choice], RelationshipType(rel_type), notes)
                st.success(f"✅ {rel_type_display} relationship added!")
                st.rerun()
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
    """Render the enhanced editable table view with AgGrid."""
    st.subheader("📊 People & Relationships Table")
    
    if not st.session_state.people:
        st.info("No people added yet. Add some people to see the table.")
        return
    
    # Create enhanced DataFrame with relationship information
    table_data = []
    for person in st.session_state.people.values():
        # Get relationships for this person
        relationships = get_relationships_for_person(person.id)
        rel_summary = []
        for rel in relationships:
            other_person_id = rel.person2_id if rel.person1_id == person.id else rel.person1_id
            other_person = st.session_state.people.get(other_person_id)
            if other_person:
                rel_summary.append(f"{rel.get_display_name()}: {other_person.name}")
        
        table_data.append({
            "ID": person.id,
            "Name": person.name,
            "Side": person.side,
            "Invited": person.invited,
            "Plus One": person.plus_one,
            "Email": person.email,
            "Phone": person.phone,
            "Notes": person.notes,
            "Relationships": "; ".join(rel_summary) if rel_summary else "None",
            "Expanded": person.expanded
        })
    
    df = pd.DataFrame(table_data).sort_values(by=["Side", "Name"]).reset_index(drop=True)
    
    # Configure AgGrid
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_default_column(editable=True, groupable=True, value=True, enableRowGroup=True, aggFunc='sum', enableRangeSelection=True, enablePivot=True)
    gb.configure_column("ID", editable=False, width=80)
    gb.configure_column("Name", editable=True, width=150)
    gb.configure_column("Side", editable=True, width=100)
    gb.configure_column("Invited", editable=True, width=80, cellRenderer="agCheckboxCellRenderer")
    gb.configure_column("Plus One", editable=True, width=80, cellRenderer="agCheckboxCellRenderer")
    gb.configure_column("Email", editable=True, width=200)
    gb.configure_column("Phone", editable=True, width=120)
    gb.configure_column("Notes", editable=True, width=200)
    gb.configure_column("Relationships", editable=False, width=300)
    gb.configure_column("Expanded", editable=True, width=80, cellRenderer="agCheckboxCellRenderer")
    
    # Enable selection and editing
    gb.configure_selection(selection_mode="single", use_checkbox=True)
    gb.configure_grid_options(domLayout='normal')
    gb.configure_grid_options(enableRangeSelection=True)
    gb.configure_grid_options(rowHeight=35)
    
    # Add double-click functionality for expand/collapse
    gb.configure_grid_options(onCellDoubleClicked="function(params) { if(params.colDef.field === 'Expanded') { params.node.setDataValue('Expanded', !params.data.Expanded); } }")
    
    grid_options = gb.build()
    
    # Render AgGrid
    grid_response = AgGrid(
        df,
        gridOptions=grid_options,
        data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
        update_mode=GridUpdateMode.MODEL_CHANGED,
        columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,
        height=400,
        allow_unsafe_jscode=True,
        key="people_table"
    )
    
    # Process any edits
    if grid_response['data'] is not None and not grid_response['data'].empty:
        process_aggrid_edits(grid_response['data'])
    
    # Show relationship management for selected person
    if grid_response['selected_rows'] is not None and len(grid_response['selected_rows']) > 0:
        selected_person_id = grid_response['selected_rows'][0]['ID']
        render_relationship_manager(selected_person_id)


def process_aggrid_edits(edited_df):
    """Process edits from the AgGrid table."""
    for _, row in edited_df.iterrows():
        person_id = row['ID']
        if person_id in st.session_state.people:
            person = st.session_state.people[person_id]
            person.name = str(row['Name'])
            person.side = str(row['Side'])
            person.invited = bool(row['Invited'])
            person.plus_one = bool(row['Plus One'])
            person.email = str(row['Email'])
            person.phone = str(row['Phone'])
            person.notes = str(row['Notes'])
            person.expanded = bool(row['Expanded'])


def render_relationship_manager(person_id: str):
    """Render relationship management for a selected person."""
    person = st.session_state.people.get(person_id)
    if not person:
        return
    
    st.markdown("---")
    st.subheader(f"🔗 Relationships for {person.name}")
    
    # Display current relationships
    relationships = get_relationships_for_person(person_id)
    if relationships:
        st.write("**Current Relationships:**")
        for rel in relationships:
            other_person_id = rel.person2_id if rel.person1_id == person_id else rel.person1_id
            other_person = st.session_state.people.get(other_person_id)
            if other_person:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"• {rel.get_display_name()}: {other_person.name}")
                    if rel.notes:
                        st.write(f"  *{rel.notes}*")
                with col2:
                    if st.button(f"🗑️ Remove", key=f"remove_{rel.person1_id}_{rel.person2_id}_{rel.relationship_type.value}"):
                        st.session_state.rels.remove(rel)
                        st.rerun()
    else:
        st.write("No relationships found.")
    
    # Quick add relationship form
    st.write("**Add New Relationship:**")
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        other_people = {f"{p.name} ({pid})": pid for pid, p in st.session_state.people.items() if pid != person_id}
        if other_people:
            other_person_choice = st.selectbox("Connect to", list(other_people.keys()), key=f"rel_person_{person_id}")
    
    with col2:
        relationship_types = RelationshipType.get_display_names()
        rel_type_display = st.selectbox("Relationship", list(relationship_types.values()), key=f"rel_type_{person_id}")
        rel_type = next(k for k, v in relationship_types.items() if v == rel_type_display)
    
    with col3:
        if other_people and st.button("Add", key=f"add_rel_{person_id}"):
            other_person_id = other_people[other_person_choice]
            add_relationship(person_id, other_person_id, RelationshipType(rel_type))
            st.success("Relationship added!")
            st.rerun()


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
