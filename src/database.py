import sqlite3
from datetime import datetime
from typing import List, Optional, Dict
from src.models import ShoppingList, ShoppingItem, Recipe, RecipeIngredient

DATABASE_FILE = "shopping_list.db"

def init_db():
    """Initialize the SQLite database with required tables."""
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    
    # Create shopping lists table
    c.execute('''
        CREATE TABLE IF NOT EXISTS shopping_lists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    ''')
    
    # Create shopping items table
    c.execute('''
        CREATE TABLE IF NOT EXISTS shopping_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            list_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            quantity INTEGER DEFAULT 1,
            category TEXT DEFAULT 'Uncategorized',
            purchased BOOLEAN DEFAULT 0,
            notes TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (list_id) REFERENCES shopping_lists (id)
        )
    ''')
    
    # Create recipes table
    c.execute('''
        CREATE TABLE IF NOT EXISTS recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT,
            prep_time INTEGER,
            cook_time INTEGER,
            servings INTEGER DEFAULT 4,
            notes TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    ''')
    
    # Create recipe ingredients table
    c.execute('''
        CREATE TABLE IF NOT EXISTS recipe_ingredients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipe_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            quantity TEXT NOT NULL,
            category TEXT DEFAULT 'Other',
            notes TEXT,
            FOREIGN KEY (recipe_id) REFERENCES recipes (id)
        )
    ''')
    
    # Create recipe instructions table
    c.execute('''
        CREATE TABLE IF NOT EXISTS recipe_instructions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipe_id INTEGER NOT NULL,
            step_number INTEGER NOT NULL,
            instruction TEXT NOT NULL,
            FOREIGN KEY (recipe_id) REFERENCES recipes (id)
        )
    ''')
    
    # Create pantry table
    c.execute('''
        CREATE TABLE IF NOT EXISTS pantry (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            quantity REAL NOT NULL,
            unit TEXT NOT NULL,
            category TEXT DEFAULT 'Other',
            expiry_date TEXT,
            notes TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()

def save_shopping_list(shopping_list: ShoppingList) -> bool:
    """Save a shopping list to the database."""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        c = conn.cursor()
        
        # Insert or update shopping list
        c.execute('''
            INSERT OR REPLACE INTO shopping_lists (name, created_at, updated_at)
            VALUES (?, ?, ?)
        ''', (shopping_list.name, shopping_list.created_at.isoformat(), shopping_list.updated_at.isoformat()))
        
        list_id = c.lastrowid or c.execute('SELECT id FROM shopping_lists WHERE name = ?', (shopping_list.name,)).fetchone()[0]
        
        # Delete existing items for this list
        c.execute('DELETE FROM shopping_items WHERE list_id = ?', (list_id,))
        
        # Insert new items
        for item in shopping_list.items:
            c.execute('''
                INSERT INTO shopping_items (list_id, name, quantity, category, purchased, notes, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                list_id,
                item.name,
                item.quantity,
                item.category,
                item.purchased,
                item.notes,
                item.created_at.isoformat(),
                item.updated_at.isoformat()
            ))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error saving shopping list: {e}")
        return False

def load_shopping_list(name: str) -> Optional[ShoppingList]:
    """Load a shopping list from the database."""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        c = conn.cursor()
        
        # Get shopping list
        c.execute('SELECT shopping_lists.created_at, shopping_lists.updated_at FROM shopping_lists WHERE shopping_lists.name = ?', (name,))
        list_data = c.fetchone()
        if not list_data:
            return None
        
        shopping_list = ShoppingList(
            name=name,
            created_at=datetime.fromisoformat(list_data[0]),
            updated_at=datetime.fromisoformat(list_data[1])
        )
        
        # Get items
        c.execute('''
            SELECT shopping_items.name, shopping_items.quantity, shopping_items.category, shopping_items.purchased, shopping_items.notes, shopping_items.created_at, shopping_items.updated_at
            FROM shopping_items
            JOIN shopping_lists ON shopping_items.list_id = shopping_lists.id
            WHERE shopping_lists.name = ?
        ''', (name,))
        
        for item_data in c.fetchall():
            item = ShoppingItem(
                name=item_data[0],
                quantity=item_data[1],
                category=item_data[2],
                purchased=bool(item_data[3]),
                notes=item_data[4],
                created_at=datetime.fromisoformat(item_data[5]),
                updated_at=datetime.fromisoformat(item_data[6])
            )
            shopping_list.items.append(item)
        
        conn.close()
        return shopping_list
    except Exception as e:
        print(f"Error loading shopping list: {e}")
        return None

def get_shopping_list_names() -> List[str]:
    """Get all shopping list names from the database."""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        c = conn.cursor()
        c.execute('SELECT name FROM shopping_lists ORDER BY name')
        names = [row[0] for row in c.fetchall()]
        conn.close()
        return names
    except Exception as e:
        print(f"Error getting shopping list names: {e}")
        return []

def save_recipe(recipe: Recipe) -> bool:
    """Save a recipe to the database."""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        c = conn.cursor()
        
        # Insert or update recipe
        c.execute('''
            INSERT OR REPLACE INTO recipes 
            (name, description, prep_time, cook_time, servings, notes, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            recipe.name,
            recipe.description,
            recipe.prep_time,
            recipe.cook_time,
            recipe.servings,
            recipe.notes,
            recipe.created_at.isoformat(),
            recipe.updated_at.isoformat()
        ))
        
        recipe_id = c.lastrowid or c.execute('SELECT id FROM recipes WHERE name = ?', (recipe.name,)).fetchone()[0]
        
        # Delete existing ingredients and instructions
        c.execute('DELETE FROM recipe_ingredients WHERE recipe_id = ?', (recipe_id,))
        c.execute('DELETE FROM recipe_instructions WHERE recipe_id = ?', (recipe_id,))
        
        # Insert ingredients
        for ingredient in recipe.ingredients:
            c.execute('''
                INSERT INTO recipe_ingredients (recipe_id, name, quantity, category, notes)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                recipe_id,
                ingredient.name,
                ingredient.quantity,
                ingredient.category,
                ingredient.notes
            ))
        
        # Insert instructions
        for i, instruction in enumerate(recipe.instructions, 1):
            c.execute('''
                INSERT INTO recipe_instructions (recipe_id, step_number, instruction)
                VALUES (?, ?, ?)
            ''', (recipe_id, i, instruction))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error saving recipe: {e}")
        return False

def load_recipe(name: str) -> Optional[Recipe]:
    """Load a recipe from the database."""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        c = conn.cursor()
        
        # Get recipe
        c.execute('''
            SELECT recipes.description, recipes.prep_time, recipes.cook_time, recipes.servings, recipes.notes, recipes.created_at, recipes.updated_at
            FROM recipes WHERE recipes.name = ?
        ''', (name,))
        recipe_data = c.fetchone()
        if not recipe_data:
            return None
        
        recipe = Recipe(
            name=name,
            description=recipe_data[0],
            prep_time=recipe_data[1],
            cook_time=recipe_data[2],
            servings=recipe_data[3],
            notes=recipe_data[4],
            created_at=datetime.fromisoformat(recipe_data[5]),
            updated_at=datetime.fromisoformat(recipe_data[6])
        )
        
        # Get ingredients
        c.execute('''
            SELECT recipe_ingredients.name, recipe_ingredients.quantity, recipe_ingredients.category, recipe_ingredients.notes
            FROM recipe_ingredients
            JOIN recipes ON recipe_ingredients.recipe_id = recipes.id
            WHERE recipes.name = ?
            ORDER BY recipe_ingredients.id
        ''', (name,))
        
        for ingredient_data in c.fetchall():
            ingredient = RecipeIngredient(
                name=ingredient_data[0],
                quantity=ingredient_data[1],
                category=ingredient_data[2],
                notes=ingredient_data[3]
            )
            recipe.ingredients.append(ingredient)
        
        # Get instructions
        c.execute('''
            SELECT recipe_instructions.instruction
            FROM recipe_instructions
            JOIN recipes ON recipe_instructions.recipe_id = recipes.id
            WHERE recipes.name = ?
            ORDER BY recipe_instructions.step_number
        ''', (name,))
        
        recipe.instructions = [row[0] for row in c.fetchall()]
        
        conn.close()
        return recipe
    except Exception as e:
        print(f"Error loading recipe: {e}")
        return None

def get_recipe_names() -> List[str]:
    """Get all recipe names from the database."""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        c = conn.cursor()
        c.execute('SELECT name FROM recipes ORDER BY name')
        names = [row[0] for row in c.fetchall()]
        conn.close()
        return names
    except Exception as e:
        print(f"Error getting recipe names: {e}")
        return []

def delete_shopping_list(name: str) -> bool:
    """Delete a shopping list from the database."""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        c = conn.cursor()
        c.execute('DELETE FROM shopping_lists WHERE name = ?', (name,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error deleting shopping list: {e}")
        return False

def delete_recipe(name: str) -> bool:
    """Delete a recipe from the database."""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        c = conn.cursor()
        c.execute('DELETE FROM recipes WHERE name = ?', (name,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error deleting recipe: {e}")
        return False

def get_pantry_items() -> List[Dict]:
    """Get all items from the pantry."""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        c = conn.cursor()
        c.execute('''
            SELECT name, quantity, unit, category, expiry_date, notes, created_at, updated_at
            FROM pantry
            ORDER BY category, name
        ''')
        
        items = []
        for row in c.fetchall():
            items.append({
                'name': row[0],
                'quantity': float(row[1]),
                'unit': row[2],
                'category': row[3],
                'expiry_date': datetime.fromisoformat(row[4]) if row[4] else None,
                'notes': row[5],
                'created_at': datetime.fromisoformat(row[6]),
                'updated_at': datetime.fromisoformat(row[7])
            })
        
        conn.close()
        return items
    except Exception as e:
        print(f"Error getting pantry items: {e}")
        return []

def add_pantry_item(name: str, quantity: float, unit: str, category: str = "Other",
                   expiry_date: Optional[datetime] = None, notes: str = "") -> bool:
    """Add or update an item in the pantry."""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        c = conn.cursor()
        
        now = datetime.now()
        
        # Check if item exists
        c.execute('SELECT quantity FROM pantry WHERE name = ?', (name,))
        existing = c.fetchone()
        
        if existing:
            # Update existing item
            c.execute('''
                UPDATE pantry
                SET quantity = ?, unit = ?, category = ?, expiry_date = ?, notes = ?, updated_at = ?
                WHERE name = ?
            ''', (
                quantity,
                unit,
                category,
                expiry_date.isoformat() if expiry_date else None,
                notes,
                now.isoformat(),
                name
            ))
        else:
            # Insert new item
            c.execute('''
                INSERT INTO pantry (name, quantity, unit, category, expiry_date, notes, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                name,
                quantity,
                unit,
                category,
                expiry_date.isoformat() if expiry_date else None,
                notes,
                now.isoformat(),
                now.isoformat()
            ))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error adding pantry item: {e}")
        return False

def remove_pantry_item(name: str) -> bool:
    """Remove an item from the pantry."""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        c = conn.cursor()
        
        c.execute('DELETE FROM pantry WHERE name = ?', (name,))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error removing pantry item: {e}")
        return False

def check_pantry_stock(recipe: Recipe) -> Dict[str, Dict]:
    """Check if there are enough ingredients in the pantry for a recipe.
    
    Args:
        recipe: Recipe object to check ingredients for
        
    Returns:
        Dict[str, Dict]: Dictionary mapping ingredient names to their status:
            {
                'ingredient_name': {
                    'required': float,
                    'available': float,
                    'unit': str,
                    'sufficient': bool
                }
            }
    """
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        c = conn.cursor()
        
        stock_status = {}
        
        for ingredient in recipe.ingredients:
            # Get the first number from the quantity string
            try:
                required_quantity = float(''.join(c for c in ingredient.quantity if c.isdigit() or c == '.'))
            except ValueError:
                required_quantity = 1.0
            
            # Get current stock
            c.execute('SELECT quantity, unit FROM pantry WHERE name = ?', (ingredient.name,))
            result = c.fetchone()
            
            if result:
                available_quantity, unit = result
                stock_status[ingredient.name] = {
                    'required': required_quantity,
                    'available': available_quantity,
                    'unit': unit,
                    'sufficient': available_quantity >= required_quantity
                }
            else:
                stock_status[ingredient.name] = {
                    'required': required_quantity,
                    'available': 0,
                    'unit': 'unknown',
                    'sufficient': False
                }
        
        conn.close()
        return stock_status
    except Exception as e:
        print(f"Error checking pantry stock: {e}")
        return {} 