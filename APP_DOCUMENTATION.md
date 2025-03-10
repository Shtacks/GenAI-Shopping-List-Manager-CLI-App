# Shopping List Organizer

A modern and intuitive command-line application for managing and organizing shopping lists, recipes, and pantry inventory with AI-powered categorization capabilities.

## Overview

The Shopping List Organizer is a feature-rich CLI application that helps users create, manage, and organize their shopping lists, recipes, and pantry inventory efficiently. It leverages AI technology to automatically categorize items and provides convenient export options for sharing and printing lists.

## Key Features

### 1. List Management
- Create multiple shopping lists with custom names
- Add, view, and remove items from lists
- Track creation and update timestamps for lists and items
- View all saved lists with item counts and last update times
- Mark items as purchased/unpurchased with easy tracking
- Easy list selection interface with numbered options
- Quick navigation with "Back" option in all submenus
- Organized data storage in SQLite database

### 2. Item Details
- Add quantities for each item
- Include optional notes for items
- Mark items as purchased/unpurchased
- Organize items by categories
- Track purchase status with visual indicators (✓)

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
- Exports stored in markdown directories

### 5. Recipe Management
- Create recipes manually with detailed information
- Generate recipes using AI assistance
- Convert recipes to shopping lists
- Export recipes to markdown format
- Combine multiple recipes into a single shopping list
- Create shopping lists from multiple recipes at once
- Automatic ingredient consolidation and quantity calculation

### 6. Pantry Management
- Track pantry inventory with quantities and units
- Monitor expiry dates for items
- Organize items by category
- Add notes and details for each item
- Convert purchased shopping list items to pantry inventory
- Edit and update pantry items easily
- Remove expired or depleted items

## Usage Guide

### Navigation

Every submenu in the application includes a "Back" option to return to the main menu at any time. This allows for easy navigation and prevents getting stuck in submenus.

### Data Storage

The application uses SQLite for efficient data storage:
- Shopping lists with items, quantities, categories, and purchase status
- Recipes with ingredients, instructions, and metadata
- Pantry inventory with quantities, units, and expiry dates
- All data is stored locally and persists between sessions

### Main Menu Options

#### Shopping List Manager

1. **Create new list**
   - Enter a name for your new shopping list
   - Start adding items immediately after creation
   - Specify quantities, categories, and notes for each item
   - View list contents after each addition
   - Type 'done' to finish or 'back' to return to menu

2. **Add item to list**
   - Choose from numbered list of available shopping lists
   - For each item, specify:
     - Name (required)
     - Quantity (defaults to 1)
     - Category (defaults to "Other")
     - Notes (optional)
   - View updated list after each addition
   - Type 'done' to finish or 'back' for main menu

3. **Show list**
   - Select a list from numbered options
   - View items grouped by category
   - See quantities, notes, and purchase status
   - Display creation and last update timestamps
   - Option to create shopping list from recipes

4. **List all saved lists**
   - View all shopping lists in a table format
   - See number of items in each list
   - View last update timestamp for each list

5. **Organize list**
   - Select a list to organize
   - AI automatically categorizes items
   - Items grouped into logical categories
   - Updates saved automatically
   - View organized list immediately

6. **Export to .md**
   - Select a list to export
   - Creates formatted markdown file
   - Includes all item details and categories
   - Shows purchase status for items
   - Includes timestamps and metadata

7. **Remove items from list**
   - Select a list to modify
   - View numbered list of items
   - Choose items to remove by number
   - Confirm removal of each item
   - View updated list after each removal

8. **Create list from Recipes**
   - Select multiple recipes to combine
   - Toggle recipes on/off in selection
   - Automatic ingredient consolidation
   - Smart quantity combination
   - Recipe source tracking in notes
   - View combined list by category

9. **Mark Items as Purchased**
   - Select a list to update
   - View items organized by category
   - Toggle individual items as purchased
   - Mark all items as purchased at once
   - Clear ✓ indicators for status
   - Option to add to pantry inventory

#### Recipe Manager

1. **Generate new recipe**
   - Enter meal name for AI generation
   - Get complete recipe with:
     - Description
     - Prep and cook times
     - Servings
     - Categorized ingredients
     - Step-by-step instructions
     - Notes
   - Option to create shopping list

2. **Create new recipe**
   - Enter recipe details:
     - Name and description
     - Prep and cook times
     - Number of servings
   - Add ingredients with:
     - Name
     - Quantity and unit
     - Category
     - Notes
   - Enter step-by-step instructions
   - Add additional notes
   - Option to create shopping list

3. **Show Recipe**
   - Select from available recipes
   - View complete recipe details:
     - Description and timing
     - Ingredients by category
     - Instructions
     - Notes
   - Option to create shopping list
   - Option to export to markdown

4. **Export recipe to .md**
   - Select recipe to export
   - Creates formatted markdown file
   - Includes all recipe details
   - Organized by sections
   - Clear instruction formatting

#### Pantry Manager

1. **Show Pantry Inventory**
   - View all items by category
   - See for each item:
     - Name
     - Quantity and unit
     - Category
     - Expiry date
     - Notes
   - Clear table format display

2. **Add Items to Pantry**
   - Add new items with:
     - Name (required)
     - Quantity (required)
     - Unit of measurement
     - Category (defaults to "Other")
     - Expiry date (optional)
     - Notes (optional)
   - Immediate database storage

3. **Edit Items in Pantry**
   - View all items in table format
   - Select items to edit by number
   - Update any item details:
     - Quantity and unit
     - Category
     - Expiry date
     - Notes
   - Option to remove items
   - Changes saved automatically

4. **Add Items to Pantry from Shopping List**
   - Select a list with purchased items
   - Choose items to transfer:
     - Individual items
     - All purchased items
   - Specify units for each item
   - Transfer categories and notes
   - Option to add custom notes

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

## Best Practices

1. **Naming Lists and Recipes**
   - Use descriptive names (e.g., "Weekly Groceries", "Party Supplies", "Grandma's Cookies")
   - Consider including dates for recurring lists
   - Avoid special characters in names

2. **Adding Items**
   - Be specific with item names
   - Include precise quantities
   - Use notes for brands or specifications
   - Categorize items appropriately
   - Mark purchase status while shopping

3. **Organization**
   - Use AI categorization for consistency
   - Review and verify categories
   - Keep lists current and organized
   - Maintain accurate pantry inventory
   - Regular cleanup of old lists

4. **Recipe Management**
   - Include all recipe details
   - Use precise measurements
   - Write clear instructions
   - Add helpful preparation notes
   - Consider serving size adjustments
   - Test generated recipes

5. **Shopping Workflow**
   - Create organized shopping lists
   - Mark items as purchased while shopping
   - Transfer purchased items to pantry
   - Update quantities after shopping
   - Remove completed lists

6. **Pantry Management**
   - Regular inventory updates
   - Monitor expiry dates
   - Remove expired items
   - Maintain consistent categories
   - Track item locations
   - Update after shopping trips
   - Note special storage requirements 