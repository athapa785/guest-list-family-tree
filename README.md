# Guest List & Family Tree Application

A modern, interactive Streamlit application for managing wedding guest lists and visualizing family trees. Perfect for wedding planners, event organizers, or anyone who needs to track relationships and guest information.

## Features

- 👥 **Guest Management**: Add, edit, and delete guests with detailed information
- 🌳 **Family Tree Visualization**: Interactive tree view with Graphviz
- 📊 **Table View**: Editable spreadsheet-like interface for bulk editing
- 📁 **Import/Export**: Save and load data in JSON format
- 📝 **Guest List Export**: Export filtered guest lists to CSV
- ✅ **RSVP Tracking**: Track invitations and plus-ones
- 🎨 **Visual Coding**: Color-coded nodes based on invitation status

## Installation

1. Clone or download this repository
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Running the Application

To start the application, run:

```bash
streamlit run main.py
```

Or alternatively:

```bash
python main.py
```

The application will open in your default web browser at `http://localhost:8501`.

### Basic Workflow

1. **Add People**: Use the left sidebar to add guests with their details
2. **Create Relationships**: Define parent-child relationships to build the family tree
3. **Visualize**: Switch between Tree and Table views to see your data
4. **Export**: Download guest lists as CSV or save the entire dataset as JSON

## Project Structure

```
guest-list-family-tree/
├── main.py                    # Main entry point
├── requirements.txt           # Python dependencies
├── README.md                 # This file
└── src/
    └── guest_list_app/
        ├── __init__.py       # Package initialization
        ├── models.py         # Data models (Person, Relationship)
        ├── data_manager.py   # Data management and CRUD operations
        ├── tree_utils.py     # Tree layout and graph utilities
        ├── ui_components.py  # Streamlit UI components
        └── app.py           # Main application logic
```

## Module Overview

### `models.py`
Defines the core data structures:
- `Person`: Represents an individual with contact info and invitation status
- `Relationship`: Represents parent-child relationships

### `data_manager.py`
Handles all data operations:
- CRUD operations for people and relationships
- JSON import/export functionality
- Session state management
- Table editing processing

### `tree_utils.py`
Tree-specific utilities:
- Layout computation using BFS algorithm
- Graphviz graph generation
- Level-based node positioning

### `ui_components.py`
Reusable Streamlit UI components:
- Forms for adding people and relationships
- Tree and table visualization
- Export functionality
- Sidebar controls

### `app.py`
Main application orchestration:
- Page configuration
- Component integration
- Layout management

## Data Format

The application uses JSON for data persistence with the following structure:

```json
{
  "people": [
    {
      "id": "P0001",
      "name": "John Doe",
      "side": "Groom",
      "notes": "Best man",
      "invited": true,
      "plus_one": false,
      "email": "john@example.com",
      "phone": "555-0123"
    }
  ],
  "relationships": [
    {
      "parent": "P0001",
      "child": "P0002"
    }
  ],
  "root": "P0001",
  "id_counter": 3
}
```

## Tips for Use

- **Tree Root**: Select a root person in the sidebar to control tree layout
- **Color Coding**: 
  - Light blue: Invited guests
  - Light green: Invited guests with plus-ones
  - Light gray: Not invited
- **Bulk Editing**: Use the Table view for quick edits to multiple people
- **Relationships**: Add relationships as Parent → Child to build generations
- **Export**: Use "Include invited-only" to filter your final guest list

## Requirements

- Python 3.7+
- Streamlit 1.28.0+
- Pandas 2.0.0+
- Graphviz 0.20.0+

## License

This project is open source and available under the MIT License.

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve the application.
