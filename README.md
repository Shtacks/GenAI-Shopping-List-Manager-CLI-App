# Shopping List Organizer

A command-line tool for managing and organizing shopping lists, recipes, and pantry inventory with AI-powered features.

## Features

- Create and manage multiple shopping lists and recipes
- Track pantry inventory with expiry dates and quantities
- Mark shopping list items as purchased
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

### Main Menu Options

1. **Shopping List Manager**
   - Manage your shopping lists
   - Mark items as purchased
   - Create lists from recipes

2. **Recipe Manager**
   - Create and manage recipes
   - Generate new recipes using AI
   - Export recipes to markdown

3. **Pantry Manager**
   - Track your pantry inventory
   - Monitor expiry dates
   - Add purchased items directly to pantry

### Shopping List Manager Features

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

8. **Create list from Recipes**
   - Create a shopping list from multiple recipes
   - Combine ingredients from different recipes
   - Smart quantity calculation and unit conversion

9. **Mark Items as Purchased**
   - Track purchased items in your lists
   - Mark individual or all items as purchased
   - Items organized by category for easy tracking

### Recipe Manager Features

1. **Generate new recipe**
   - Create a complete recipe using AI
   - Includes description, prep/cook times, ingredients, and instructions
   - Option to create a shopping list from the recipe

2. **Create new recipe**
   - Manually create recipes with detailed information
   - Add ingredients with quantities and categories
   - Write step-by-step instructions

3. **Show recipe**
   - View saved recipes with full details
   - Organized display of ingredients by category
   - Step-by-step instructions
   - Option to create shopping list from recipe

4. **Export recipe to .md**
   - Export recipes to markdown format
   - Beautiful, organized layout
   - Includes all recipe details and metadata

### Pantry Manager Features

1. **Show Pantry Inventory**
   - View all pantry items organized by category
   - Track quantities and units
   - Monitor expiry dates
   - View item notes and details

2. **Add Items to Pantry**
   - Add new items with quantities and units
   - Set expiry dates
   - Organize items by category
   - Add optional notes

3. **Edit Items in Pantry**
   - Update quantities and units
   - Modify expiry dates
   - Change categories
   - Remove items

4. **Add Items to Pantry from Shopping List**
   - Convert purchased items to pantry inventory
   - Specify units for each item
   - Maintain categories and notes
   - Add individual or all purchased items

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
│   ├── database.py       # SQLite database operations
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

- Shopping lists, recipes, and pantry data stored in SQLite database
- Markdown files provide formatted, readable exports
- All user data is stored in the local database
- Automatic database initialization and migration

### Running Tests

```bash
pytest
```

## License

MIT License - feel free to use this project for your own purposes. 