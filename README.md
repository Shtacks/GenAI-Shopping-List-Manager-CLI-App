# Shopping List Organizer

A command-line tool for managing and organizing shopping lists with AI-powered categorization.

## Features

- Create and manage multiple shopping lists
- Add items with quantities and notes
- AI-powered categorization of items using GPT-4-mini
- Export lists to markdown format
- Interactive CLI interface with rich formatting

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
   - Uses GPT-4-mini to categorize items intelligently
   - Automatically groups items into logical categories

6. **Export to .md**
   - Exports a shopping list to markdown format
   - Groups items by category
   - Includes timestamps and purchase status

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
└── tests/
    ├── __init__.py
    └── test_main.py      # Main test file
```

### Running Tests

```bash
pytest
```

## License

MIT License - feel free to use this project for your own purposes. 