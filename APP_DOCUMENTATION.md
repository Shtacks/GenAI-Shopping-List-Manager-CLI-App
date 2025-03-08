# Shopping List Organizer

A modern and intuitive command-line application for managing and organizing shopping lists and recipes with AI-powered categorization capabilities.

## Overview

The Shopping List Organizer is a feature-rich CLI application that helps users create, manage, and organize their shopping lists and recipes efficiently. It leverages AI technology to automatically categorize items and provides convenient export options for sharing and printing lists.

## Key Features

### 1. List Management
- Create multiple shopping lists with custom names
- Add, view, and remove items from lists
- Track creation and update timestamps for lists and items
- View all saved lists with item counts and last update times
- Easy list selection interface with numbered options
- Quick navigation with "Back" option in all submenus
- Organized file storage in dedicated directories

### 2. Item Details
- Add quantities for each item
- Include optional notes for items
- Mark items as purchased/unpurchased
- Organize items by categories

### 3. AI-Powered Organization
- Automatic categorization of items using GPT-3.5-turbo
- Smart grouping into logical categories:
  - Produce
  - Frozen
  - Pantry
  - Meat
  - Dairy
  - Cold
  - Alcohol
  - Household
  - Other

### 4. Export Capabilities
- Export lists and recipes to markdown format
- Organized view with categories
- Include purchase status (✓ for purchased items)
- Timestamps for creation and last update
- Quantities and notes included in export
- Exports stored in dedicated markdown directories

### 5. Recipe Management
- Create and store recipes with detailed information
- Generate recipes using AI assistance
- Convert recipes to shopping lists
- Export recipes to markdown format
- Organize recipes in dedicated directories

## Usage Guide

### Navigation

Every submenu in the application includes a "Back" option to return to the main menu at any time. This allows for easy navigation and prevents getting stuck in submenus.

### File Organization

The application organizes files in a structured directory layout:
```
lists/
├── shopping/
│   ├── JSON/    # Stores shopping list data files
│   └── MD/      # Stores shopping list markdown exports
└── recipes/
    ├── JSON/    # Stores recipe data files
    └── MD/      # Stores recipe markdown exports
```

This organization helps keep your shopping lists, recipes, and their exports neatly separated and easy to find.

### Main Menu Options

1. **Create new list**
   - Enter a name for your new shopping list
   - Type 'back' to return to main menu
   - Lists are automatically saved in the shopping/JSON directory

2. **Add item to list**
   - Choose from numbered list of available shopping lists (includes Back option)
   - For each item, you can specify:
     - Name
     - Quantity (defaults to 1)
     - Category (optional, can be auto-categorized)
     - Notes (optional)
   - Type 'done' to finish adding items
   - Type 'back' at any prompt to return to main menu
   - View current list contents after each addition

3. **Show list**
   - Select a list from numbered options (includes Back option)
   - Items are grouped by category
   - Shows quantities, notes, and purchase status
   - Displays creation and last update times

4. **List all saved lists**
   - See all your shopping lists in one view
   - Shows the number of items in each list
   - Displays when each list was last updated

5. **Organize list**
   - Select a list from numbered options (includes Back option)
   - AI automatically categorizes items
   - Items are grouped into logical categories
   - Updates are saved automatically

6. **Export to .md**
   - Select a list from numbered options (includes Back option)
   - Converts list to markdown format
   - Saves the export in the shopping/MD directory
   - Perfect for sharing or printing
   - Maintains all item details and organization
   - Creates a clean, readable format

7. **Remove items from list**
   - Select a list from numbered options (includes Back option)
   - Choose items to remove by number
   - Type 'done' to finish removing items
   - Type 'back' at any prompt to return to main menu
   - List is automatically updated

8. **Create list from meal**
   - Enter a meal name to generate ingredients
   - AI generates a detailed list of ingredients
   - Creates a new shopping list with the ingredients
   - Items are automatically categorized
   - Quantities and notes are included

9. **Generate Recipe**
   - Enter a meal name to generate a recipe
   - AI creates a complete recipe with:
     - Description
     - Prep and cook times
     - Ingredients with quantities
     - Step-by-step instructions
     - Additional notes
   - Option to create a shopping list from the recipe

10. **Show Recipe**
    - View saved recipes with full details
    - Organized display of ingredients by category
    - Clear step-by-step instructions
    - Option to create a shopping list from the recipe

11. **Export recipe to .md**
    - Select a recipe to export
    - Converts recipe to markdown format
    - Saves in the recipes/MD directory
    - Includes all recipe details and formatting

## Sample Export Formats

### Shopping List
```markdown
# Shopping List Name

*Created: YYYY-MM-DD HH:MM*
*Last Updated: YYYY-MM-DD HH:MM*

## Produce
- [ ] Apples (6)
- [✓] Bananas - organic

## Dairy
- [ ] Milk (2) - 2% fat
- [ ] Yogurt

## Pantry
- [ ] Bread
- [ ] Cereal - whole grain
```

### Recipe
```markdown
# Recipe Name

*A delicious description of the dish*

## Details
- **Prep Time:** 20 minutes
- **Cook Time:** 30 minutes
- **Total Time:** 50 minutes
- **Servings:** 4

## Ingredients

### Produce
- Onion (1 medium) - finely diced
- Garlic (3 cloves) - minced

### Pantry
- Olive oil (2 tablespoons)
- Salt (1 teaspoon)

## Instructions
1. First step of the recipe
2. Second step of the recipe

## Notes
Additional tips and suggestions
```

## Data Storage

- Shopping lists are saved in JSON format in the `lists/shopping/JSON` directory
- Shopping list exports are saved as markdown in the `lists/shopping/MD` directory
- Recipes are saved in JSON format in the `lists/recipes/JSON` directory
- Recipe exports are saved as markdown in the `lists/recipes/MD` directory
- Each list and recipe maintains:
  - Name
  - Creation timestamp
  - Last update timestamp
  - Full details of items/ingredients
- Data persists between sessions
- Lists and recipes can be accessed and modified at any time

## Best Practices

1. **Naming Lists and Recipes**
   - Use descriptive names (e.g., "Weekly Groceries", "Party Supplies", "Grandma's Cookies")
   - Consider including dates for recurring lists
   - Avoid special characters that might cause issues with file names

2. **Adding Items**
   - Be specific with item names for better categorization
   - Include quantities for precise shopping
   - Use notes for brands or specific requirements
   - Use 'back' option if you need to return to main menu

3. **Organization**
   - Use the AI categorization for consistent organization
   - Review categorized items to ensure accuracy
   - Export lists and recipes before shopping for offline access
   - Keep your directories organized by removing old or unused items

4. **List and Recipe Management**
   - Regular cleanup of completed lists
   - Update quantities as needed
   - Mark items as purchased while shopping
   - Use 'back' option to switch between lists easily
   - Check both JSON and MD directories when backing up your data 