"""
Main Streamlit application for the Guest List & Family Tree.
This is the entry point that orchestrates all UI components.
"""

import streamlit as st

from .data_manager import init_state
from .ui_components import (
    render_sidebar, render_add_person_form, render_add_relationship_form,
    render_delete_person_section, render_metrics, render_tree_view,
    render_table_view, render_guest_list_export
)


def main():
    """Main application function."""
    # Page configuration
    st.set_page_config(page_title="Guest List & Family Tree", layout="wide")
    
    # Initialize session state
    init_state()
    
    # Page title
    st.title("👪 Guest List & Family Tree")
    
    # Render sidebar
    render_sidebar()
    
    # Main layout: Left column for forms, Right column for visualization
    left, right = st.columns([1, 2], gap="large")
    
    with left:
        render_add_person_form()
        render_add_relationship_form()
        render_delete_person_section()
    
    with right:
        # Metrics display
        render_metrics()
        
        # View selector
        view = st.radio("View", options=["Tree", "Table"], horizontal=True)
        
        if view == "Tree":
            render_tree_view()
        else:
            render_table_view()
    
    # Export section
    render_guest_list_export()
    
    # Footer
    st.caption("Tip: Use the sidebar to save/load JSON. Switch between Tree and Table views above. Add relationships as Parent ➜ Child to build generations.")


if __name__ == "__main__":
    main()
