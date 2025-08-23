# Development Guide

This document provides information for developers who want to contribute to or modify the Guest List & Family Tree application.

## Development Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the application:
   ```bash
   streamlit run main.py
   ```

## Code Architecture

The application follows a modular architecture with clear separation of concerns:

### Core Modules

- **`models.py`**: Data models and structures
- **`data_manager.py`**: Data persistence and CRUD operations
- **`tree_utils.py`**: Tree layout algorithms and graph utilities
- **`ui_components.py`**: Reusable UI components
- **`app.py`**: Main application orchestration

### Design Patterns

- **Data Layer**: All data operations are centralized in `data_manager.py`
- **UI Layer**: UI components are modular and reusable
- **Separation of Concerns**: Business logic is separated from presentation
- **Session State Management**: Streamlit session state is managed centrally

## Adding New Features

### Adding a New Person Field

1. Update the `Person` dataclass in `models.py`
2. Modify the `add_person` function in `data_manager.py`
3. Update the form in `ui_components.py`
4. Adjust the table view columns

### Adding New Relationship Types

1. Extend the `Relationship` model if needed
2. Update relationship creation logic
3. Modify tree visualization if different styling is needed

### Adding New Export Formats

1. Add new export function to `data_manager.py`
2. Create UI component in `ui_components.py`
3. Integrate into main app

## Testing

Currently, the application relies on manual testing. To test:

1. Run the application
2. Add sample data using the UI
3. Test all features:
   - Adding/editing/deleting people
   - Creating relationships
   - Switching between views
   - Import/export functionality

## Code Style

- Follow PEP 8 conventions
- Use type hints where appropriate
- Document functions with docstrings
- Keep functions focused and single-purpose

## Deployment

The application can be deployed using various Streamlit hosting options:

- **Streamlit Cloud**: Connect your GitHub repository
- **Heroku**: Use the provided `setup.py` for deployment
- **Docker**: Create a Dockerfile for containerized deployment

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Known Limitations

- No user authentication (single-user application)
- Data is stored in browser session (not persistent across sessions)
- Limited to JSON import/export
- No database backend

## Future Enhancements

- Add user authentication
- Implement database storage
- Add more export formats (PDF, Excel)
- Enhanced tree visualization options
- Mobile-responsive design improvements
