# Shopping List Organizer

A command-line tool for managing and organizing shopping lists and recipes with AI-powered features.

## Features

- Create and manage multiple shopping lists and recipes
- Add items with quantities and notes
- AI-powered categorization of items using GPT-3.5-turbo
- AI-powered recipe generation and ingredient list creation
- Export lists and recipes to markdown format
- Interactive CLI interface with rich formatting
- Organized file storage with separate JSON and markdown directories

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/shopping-list-organizer.git
cd shopping-list-organizer
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the package:
```bash
pip install -e .
```

4. Create a `.env` file in the project root and add your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

## Usage

Run the application:
```bash
shopping-list
```

### Available Commands

1. **Create new list**
   - Creates a new shopping list with a specified name

2. **Add item to list**
   - Adds items to an existing list
   - Specify quantity and optional notes
   - Type 'Done' when finished adding items

3. **Show list**
   - Displays a formatted view of a shopping list
   - Shows items, quantities, categories, and purchase status

4. **List all saved lists**
   - Shows all available shopping lists
   - Displays item count and last update time

5. **Organize list**
   - Uses GPT-3.5-turbo to categorize items intelligently
   - Automatically groups items into logical categories

6. **Export to .md**
   - Exports a shopping list to markdown format
   - Groups items by category
   - Includes timestamps and purchase status

7. **Remove items from list**
   - Remove specific items from a list
   - Select items by number for easy removal

8. **Create list from meal**
   - Generate a shopping list from a meal name
   - AI creates detailed ingredient list with quantities
   - Automatically categorizes ingredients

9. **Generate Recipe**
   - Create a complete recipe using AI
   - Includes description, prep/cook times, ingredients, and instructions
   - Option to create a shopping list from the recipe

10. **Show Recipe**
    - View saved recipes with full details
    - Organized display of ingredients by category
    - Step-by-step instructions
    - Option to create shopping list from recipe

11. **Export recipe to .md**
    - Export recipes to markdown format
    - Beautiful, organized layout
    - Includes all recipe details and metadata

## Development

### Project Structure

```
shopping-list-organizer/
├── .env                    # Environment variables
├── .gitignore             # Git ignore rules
├── README.md              # Project documentation
├── requirements.txt       # Project dependencies
├── setup.py              # Package setup
├── src/
│   ├── __init__.py
│   ├── main.py           # Main CLI entry point
│   ├── models.py         # Data models
│   └── utils.py          # Utility functions
├── lists/                # Data storage directory
│   ├── shopping/         # Shopping list storage
│   │   ├── JSON/        # Shopping list data files
│   │   └── MD/          # Shopping list markdown exports
│   └── recipes/         # Recipe storage
│       ├── JSON/        # Recipe data files
│       └── MD/          # Recipe markdown exports
└── tests/
    ├── __init__.py
    └── test_main.py      # Main test file
```

### Data Organization

- Shopping lists and recipes are stored in separate directories
- JSON files contain the raw data
- Markdown files provide formatted, readable exports
- All user data is stored in the `lists` directory
- Automatic directory creation and organization

### Running Tests

```bash
pytest
```

## License

MIT License - feel free to use this project for your own purposes. 