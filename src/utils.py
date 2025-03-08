import json
from datetime import datetime
from typing import List, Optional, Dict
from pathlib import Path
import os
from dotenv import load_dotenv
from openai import OpenAI
from rich.prompt import Prompt
from rich.console import Console
from src.models import ShoppingList, ShoppingItem, Recipe, RecipeIngredient

# Load environment variables
load_dotenv()

# Initialize console for user input
console = Console()

# Global variable to store the API key
api_key = os.getenv("OPENAI_API_KEY")

# Constants for file paths
LIST_DIR = "lists"
SHOPPING_DIR = os.path.join(LIST_DIR, "shopping")
RECIPES_DIR = os.path.join(LIST_DIR, "recipes")

# Constants for JSON and MD subdirectories
SHOPPING_JSON_DIR = os.path.join(SHOPPING_DIR, "JSON")
SHOPPING_MD_DIR = os.path.join(SHOPPING_DIR, "MD")
RECIPES_JSON_DIR = os.path.join(RECIPES_DIR, "JSON")
RECIPES_MD_DIR = os.path.join(RECIPES_DIR, "MD")

def ensure_directories_exist():
    """Ensure the required directories exist."""
    os.makedirs(SHOPPING_JSON_DIR, exist_ok=True)
    os.makedirs(SHOPPING_MD_DIR, exist_ok=True)
    os.makedirs(RECIPES_JSON_DIR, exist_ok=True)
    os.makedirs(RECIPES_MD_DIR, exist_ok=True)

def get_shopping_list_path(filename: str) -> str:
    """Get the full path for a shopping list JSON file.
    
    Args:
        filename: The name of the file (with or without .json extension)
        
    Returns:
        str: The full path to the JSON file
    """
    if not filename.endswith('.json'):
        filename += '.json'
    return os.path.join(SHOPPING_JSON_DIR, filename)

def get_recipe_path(filename: str) -> str:
    """Get the full path for a recipe JSON file.
    
    Args:
        filename: The name of the file (with or without .json extension)
        
    Returns:
        str: The full path to the JSON file
    """
    if not filename.endswith('.json'):
        filename += '.json'
    return os.path.join(RECIPES_JSON_DIR, filename)

def get_markdown_path(filename: str, is_recipe: bool = False) -> str:
    """Get the full path for a markdown file.
    
    Args:
        filename: The name of the file (with or without .md extension)
        is_recipe: Whether this is a recipe markdown file
        
    Returns:
        str: The full path to the markdown file
    """
    if not filename.endswith('.md'):
        filename += '.md'
    base_dir = RECIPES_MD_DIR if is_recipe else SHOPPING_MD_DIR
    return os.path.join(base_dir, filename)

def get_api_key() -> str:
    """Get the OpenAI API key, prompting the user if not set."""
    global api_key
    
    if not api_key:
        console.print("\n[yellow]No OpenAI API key found in .env file.[/yellow]")
        console.print("You can either:")
        console.print("1. Add your API key to the .env file")
        console.print("2. Enter your API key now")
        
        choice = Prompt.ask("Choose an option", choices=["1", "2"])
        
        if choice == "1":
            console.print("\n[cyan]Please add your API key to the .env file:[/cyan]")
            console.print("OPENAI_API_KEY=your_api_key_here")
            console.print("\n[yellow]After adding the key, restart the application.[/yellow]")
            raise ValueError("Please add your API key to the .env file and restart the application.")
        else:
            api_key = Prompt.ask("\n[cyan]Enter your OpenAI API key[/cyan]")
            if not api_key:
                raise ValueError("API key cannot be empty")
    
    return api_key

# Initialize OpenAI client with dynamic API key
def get_client() -> OpenAI:
    """Get an OpenAI client with the current API key."""
    return OpenAI(api_key=get_api_key())

def save_list_to_file(shopping_list: ShoppingList, filename: str) -> bool:
    """Save a shopping list to a JSON file.
    
    Args:
        shopping_list: The shopping list to save
        filename: The name of the file to save to
        
    Returns:
        bool: True if the save was successful, False otherwise
    """
    ensure_directories_exist()
    try:
        data = {
            "name": shopping_list.name,
            "items": [
                {
                    "name": item.name,
                    "quantity": item.quantity,
                    "category": item.category,
                    "purchased": item.purchased,
                    "notes": item.notes,
                    "created_at": item.created_at.isoformat(),
                    "updated_at": item.updated_at.isoformat(),
                }
                for item in shopping_list.items
            ],
            "created_at": shopping_list.created_at.isoformat(),
            "updated_at": shopping_list.updated_at.isoformat(),
        }
        
        filepath = get_shopping_list_path(filename)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        console.print(f"[red]Error saving list: {str(e)}[/red]")
        return False

def load_list_from_file(filename: str) -> Optional[ShoppingList]:
    """Load a shopping list from a JSON file.
    
    Args:
        filename: The name of the file to load from
        
    Returns:
        Optional[ShoppingList]: The loaded shopping list, or None if loading failed
    """
    try:
        filepath = get_shopping_list_path(filename)
        if not os.path.exists(filepath):
            return None
            
        with open(filepath, 'r') as f:
            data = json.load(f)
            
        shopping_list = ShoppingList(
            name=data["name"],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"])
        )
        
        for item_data in data["items"]:
            item = ShoppingItem(
                name=item_data["name"],
                quantity=item_data["quantity"],
                category=item_data["category"],
                purchased=item_data["purchased"],
                notes=item_data["notes"],
                created_at=datetime.fromisoformat(item_data["created_at"]),
                updated_at=datetime.fromisoformat(item_data["updated_at"])
            )
            shopping_list.items.append(item)
            
        return shopping_list
    except Exception as e:
        console.print(f"[red]Error loading list: {str(e)}[/red]")
        return None

def get_saved_lists() -> List[str]:
    """Get a list of all saved shopping list names.
    
    Returns:
        List[str]: List of shopping list names
    """
    ensure_directories_exist()
    try:
        files = os.listdir(SHOPPING_JSON_DIR)
        return [os.path.splitext(f)[0] for f in files if f.endswith('.json')]
    except Exception as e:
        console.print(f"[red]Error getting saved lists: {str(e)}[/red]")
        return []

def organize_list(shopping_list: ShoppingList) -> ShoppingList:
    """Organize items in a shopping list using GPT-3.5-turbo."""
    # Load environment variables
    load_dotenv()
    
    # Get API key from environment
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set. Please set your OpenAI API key in the .env file.")
    
    # Create a simpler prompt
    items_text = "\n".join([f"- {item.name}" for item in shopping_list.items])
    prompt = f"""Organize these shopping items into logical categories. Create appropriate categories based on the items.
    Group similar items together and give each group a clear, descriptive category name.
    
    Items:
    {items_text}
    
    Format your response as:
    Category Name:
    - Item1
    - Item2
    """
    
    try:
        # Create client with the provided API key
        client = OpenAI(api_key=api_key)
        
        # Call OpenAI API with simpler configuration
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a shopping list organizer. Create logical categories for items based on efficient store navigation and group them appropriately."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,  # Balance between consistency and flexibility
            max_tokens=500    # Increased token limit for more categories
        )
        
        # Parse the response
        categories_text = response.choices[0].message.content
        
        # Create a mapping of items to categories
        item_to_category = {}
        current_category = None
        
        for line in categories_text.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            if line.endswith(':'):
                current_category = line[:-1].strip()
                continue
                
            if line.startswith('- '):
                item_name = line[2:].strip()
                if current_category:
                    item_to_category[item_name] = current_category
        
        # Update item categories
        for item in shopping_list.items:
            # Try to find a match in the categorized items
            matched = False
            for categorized_name, category in item_to_category.items():
                if categorized_name.lower() in item.name.lower() or item.name.lower() in categorized_name.lower():
                    item.category = category
                    matched = True
                    break
            
            if not matched:
                item.category = "Other"
        
        return shopping_list
        
    except Exception as e:
        error_message = str(e)
        console.print(f"\n[red]Error using OpenAI API: {error_message}[/red]")
        
        # More detailed error handling
        if "401" in error_message:
            console.print("[yellow]Invalid API key. Please check your key in the .env file.[/yellow]")
        elif "429" in error_message:
            console.print("[yellow]Rate limit exceeded. Please try again later.[/yellow]")
        elif "500" in error_message:
            console.print("[yellow]OpenAI server error. Please try again later.[/yellow]")
            console.print("[yellow]If the error persists, try using a different API key or check your internet connection.[/yellow]")
        else:
            console.print("[yellow]Failed to organize items. Keeping original categories.[/yellow]")
        
        return shopping_list

def export_to_markdown(shopping_list: ShoppingList) -> str:
    """Export a shopping list to markdown format."""
    # Group items by category
    items_by_category: Dict[str, List[ShoppingItem]] = {}
    for item in shopping_list.items:
        if item.category not in items_by_category:
            items_by_category[item.category] = []
        items_by_category[item.category].append(item)
    
    # Create markdown content
    markdown = f"# {shopping_list.name}\n\n"
    markdown += f"*Created: {shopping_list.created_at.strftime('%Y-%m-%d %H:%M')}*\n"
    markdown += f"*Last Updated: {shopping_list.updated_at.strftime('%Y-%m-%d %H:%M')}*\n\n"
    
    # Add items by category
    for category, items in sorted(items_by_category.items()):
        markdown += f"## {category}\n"
        for item in sorted(items, key=lambda x: x.name.lower()):
            status = "✓" if item.purchased else " "
            markdown += f"- [{status}] {item.name}"
            if item.quantity > 1:
                markdown += f" ({item.quantity})"
            if item.notes:
                markdown += f" - {item.notes}"
            markdown += "\n"
        markdown += "\n"
    
    return markdown 

def load_all_lists() -> List[ShoppingList]:
    """Load all shopping lists from the JSON file.
    
    Returns:
        List[ShoppingList]: List of all shopping lists
    """
    filepath = get_shopping_list_path("shopping_lists.json")
    try:
        if not os.path.exists(filepath):
            return []
            
        with open(filepath, 'r') as f:
            data = json.load(f)
            if not isinstance(data, list):
                data = []
                
        shopping_lists = []
        for list_data in data:
            shopping_list = ShoppingList(
                name=list_data["name"],
                created_at=datetime.fromisoformat(list_data["created_at"]),
                updated_at=datetime.fromisoformat(list_data["updated_at"])
            )
            
            for item_data in list_data["items"]:
                item = ShoppingItem(
                    name=item_data["name"],
                    quantity=item_data["quantity"],
                    category=item_data["category"],
                    purchased=item_data["purchased"],
                    notes=item_data["notes"],
                    created_at=datetime.fromisoformat(item_data["created_at"]),
                    updated_at=datetime.fromisoformat(item_data["updated_at"])
                )
                shopping_list.items.append(item)
                
            shopping_lists.append(shopping_list)
            
        return shopping_lists
    except Exception as e:
        print(f"Error loading lists: {e}")
        return []

def save_all_lists(shopping_lists: List[ShoppingList]) -> bool:
    """Save all shopping lists to a single JSON file.
    
    Args:
        shopping_lists: List of shopping lists to save
        
    Returns:
        bool: True if the save was successful, False otherwise
    """
    ensure_directories_exist()
    try:
        data = []
        for shopping_list in shopping_lists:
            list_data = {
                "name": shopping_list.name,
                "items": [
                    {
                        "name": item.name,
                        "quantity": item.quantity,
                        "category": item.category,
                        "purchased": item.purchased,
                        "notes": item.notes,
                        "created_at": item.created_at.isoformat(),
                        "updated_at": item.updated_at.isoformat(),
                    }
                    for item in shopping_list.items
                ],
                "created_at": shopping_list.created_at.isoformat(),
                "updated_at": shopping_list.updated_at.isoformat(),
            }
            data.append(list_data)
            
        filepath = get_shopping_list_path("shopping_lists.json")
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving lists: {e}")
        return False

def save_list(shopping_list: ShoppingList) -> bool:
    """Save a single shopping list by updating the array of lists.
    
    Args:
        shopping_list: The shopping list to save
        
    Returns:
        bool: True if the save was successful, False otherwise
    """
    lists = load_all_lists()
    
    # Update existing list or add new one
    found = False
    for i, existing_list in enumerate(lists):
        if existing_list.name == shopping_list.name:
            lists[i] = shopping_list
            found = True
            break
    
    if not found:
        lists.append(shopping_list)
        
    return save_all_lists(lists)

def get_list(name: str) -> Optional[ShoppingList]:
    """Get a specific shopping list by name.
    
    Args:
        name: Name of the list to get
        
    Returns:
        Optional[ShoppingList]: The shopping list if found, None otherwise
    """
    lists = load_all_lists()
    for shopping_list in lists:
        if shopping_list.name == name:
            return shopping_list
    return None

def get_list_names() -> List[str]:
    """Get names of all saved shopping lists.
    
    Returns:
        List[str]: List of shopping list names
    """
    lists = load_all_lists()
    return [lst.name for lst in lists]

def delete_list(name: str) -> bool:
    """Delete a shopping list by name.
    
    Args:
        name: Name of the list to delete
        
    Returns:
        bool: True if the list was deleted, False otherwise
    """
    lists = load_all_lists()
    lists = [lst for lst in lists if lst.name != name]
    return save_all_lists(lists)

def generate_ingredient_list(meal: str) -> List[Dict[str, str]]:
    """Generate a list of ingredients for a meal using GPT-4o-mini.
    
    Args:
        meal: The name of the meal/dish to generate ingredients for
        
    Returns:
        List[Dict[str, str]]: List of ingredients with their quantities, categories, and notes
    """
    try:
        client = get_client()
        
        prompt = f"""Generate a detailed list of ingredients needed to make {meal}.
        For each ingredient, provide:
        1. The exact quantity with unit (e.g., "2 tablespoons", "1 cup", "3 medium")
        2. The category it belongs to (e.g., Produce, Dairy, Pantry, Meat, Spices)
        3. Any preparation notes or specifications
        
        Format your response as a list where each line follows this format:
        - ingredient | quantity | category | notes
        
        Example:
        - butter | 2 tablespoons | Dairy | unsalted, room temperature
        - onion | 1 medium | Produce | finely diced
        - flour | 1 cup | Pantry | all-purpose
        - chicken breast | 2 pieces | Meat | boneless, skinless
        - black pepper | 1/2 teaspoon | Spices | freshly ground
        """
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system", 
                    "content": """You are a professional chef's assistant. Generate detailed, accurate ingredient lists for recipes.
                    Always include:
                    - Precise measurements using standard kitchen units
                    - Clear categories for shopping organization
                    - Important preparation notes or specifications
                    - All necessary ingredients, including basics like salt and oil"""
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,  # Lower for more consistent formatting
            max_tokens=750    # Increased for more detailed responses
        )
        
        # Parse the response into a list of ingredients
        ingredients = []
        for line in response.choices[0].message.content.split('\n'):
            line = line.strip()
            if line.startswith('-'):
                # Remove the leading '-' and split by '|'
                parts = [part.strip() for part in line[1:].split('|')]
                
                if len(parts) >= 4:  # Full format: name, quantity, category, notes
                    ingredients.append({
                        "name": parts[0],
                        "quantity": parts[1],
                        "category": parts[2],
                        "notes": parts[3]
                    })
                elif len(parts) == 3:  # Missing notes
                    ingredients.append({
                        "name": parts[0],
                        "quantity": parts[1],
                        "category": parts[2],
                        "notes": ""
                    })
                elif len(parts) == 2:  # Missing category and notes
                    ingredients.append({
                        "name": parts[0],
                        "quantity": parts[1],
                        "category": "Other",
                        "notes": ""
                    })
                elif len(parts) == 1:  # Only name
                    ingredients.append({
                        "name": parts[0],
                        "quantity": "1",
                        "category": "Other",
                        "notes": ""
                    })
        
        return ingredients
        
    except Exception as e:
        error_message = str(e)
        console.print(f"\n[red]Error generating ingredient list: {error_message}[/red]")
        
        if "401" in error_message:
            console.print("[yellow]Invalid API key. Please check your key in the .env file.[/yellow]")
        elif "429" in error_message:
            console.print("[yellow]Rate limit exceeded. Please try again later.[/yellow]")
        elif "500" in error_message:
            console.print("[yellow]OpenAI server error. Please try again later.[/yellow]")
        else:
            console.print("[yellow]An unexpected error occurred while generating ingredients.[/yellow]")
        
        return [] 

def load_all_recipes() -> List[Recipe]:
    """Load all recipes from the recipes.json file.
    
    Returns:
        List[Recipe]: List of all recipes
    """
    filepath = os.path.join(RECIPES_JSON_DIR, "recipes.json")
    try:
        if not os.path.exists(filepath):
            return []
            
        with open(filepath, 'r') as f:
            data = json.load(f)
            if not isinstance(data, list):
                data = []
                
        recipes = []
        for recipe_data in data:
            recipe = Recipe(
                name=recipe_data["name"],
                description=recipe_data.get("description"),
                prep_time=recipe_data.get("prep_time"),
                cook_time=recipe_data.get("cook_time"),
                servings=recipe_data.get("servings", 4),
                notes=recipe_data.get("notes"),
                created_at=datetime.fromisoformat(recipe_data["created_at"]),
                updated_at=datetime.fromisoformat(recipe_data["updated_at"])
            )
            
            # Load ingredients
            for ingredient_data in recipe_data.get("ingredients", []):
                ingredient = RecipeIngredient(
                    name=ingredient_data["name"],
                    quantity=ingredient_data["quantity"],
                    category=ingredient_data.get("category", "Other"),
                    notes=ingredient_data.get("notes")
                )
                recipe.ingredients.append(ingredient)
            
            # Load instructions
            recipe.instructions = recipe_data.get("instructions", [])
            
            recipes.append(recipe)
            
        return recipes
    except Exception as e:
        console.print(f"[red]Error loading recipes: {str(e)}[/red]")
        return []

def save_all_recipes(recipes: List[Recipe]) -> bool:
    """Save all recipes to the recipes.json file.
    
    Args:
        recipes: List of recipes to save
        
    Returns:
        bool: True if the save was successful, False otherwise
    """
    ensure_directories_exist()
    try:
        data = []
        for recipe in recipes:
            recipe_data = {
                "name": recipe.name,
                "description": recipe.description,
                "prep_time": recipe.prep_time,
                "cook_time": recipe.cook_time,
                "servings": recipe.servings,
                "notes": recipe.notes,
                "ingredients": [
                    {
                        "name": ingredient.name,
                        "quantity": ingredient.quantity,
                        "category": ingredient.category,
                        "notes": ingredient.notes
                    }
                    for ingredient in recipe.ingredients
                ],
                "instructions": recipe.instructions,
                "created_at": recipe.created_at.isoformat(),
                "updated_at": recipe.updated_at.isoformat()
            }
            data.append(recipe_data)
            
        filepath = os.path.join(RECIPES_JSON_DIR, "recipes.json")
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        console.print(f"[red]Error saving recipes: {str(e)}[/red]")
        return False

def save_recipe(recipe: Recipe) -> bool:
    """Save a single recipe by updating the array of recipes.
    
    Args:
        recipe: The recipe to save
        
    Returns:
        bool: True if the save was successful, False otherwise
    """
    recipes = load_all_recipes()
    
    # Update existing recipe or add new one
    found = False
    for i, existing_recipe in enumerate(recipes):
        if existing_recipe.name == recipe.name:
            recipes[i] = recipe
            found = True
            break
    
    if not found:
        recipes.append(recipe)
        
    return save_all_recipes(recipes)

def get_recipe(name: str) -> Optional[Recipe]:
    """Get a specific recipe by name.
    
    Args:
        name: Name of the recipe to get
        
    Returns:
        Optional[Recipe]: The recipe if found, None otherwise
    """
    recipes = load_all_recipes()
    for recipe in recipes:
        if recipe.name == name:
            return recipe
    return None

def get_recipe_names() -> List[str]:
    """Get names of all saved recipes.
    
    Returns:
        List[str]: List of recipe names
    """
    recipes = load_all_recipes()
    return [recipe.name for recipe in recipes]

def delete_recipe(name: str) -> bool:
    """Delete a recipe by name.
    
    Args:
        name: Name of the recipe to delete
        
    Returns:
        bool: True if the recipe was deleted, False otherwise
    """
    recipes = load_all_recipes()
    recipes = [recipe for recipe in recipes if recipe.name != name]
    return save_all_recipes(recipes)

def generate_recipe(meal: str) -> Optional[Recipe]:
    """Generate a recipe for a meal using GPT-4o-mini.
    
    Args:
        meal: The name of the meal to generate a recipe for
        
    Returns:
        Optional[Recipe]: The generated recipe, or None if generation failed
    """
    try:
        client = get_client()
        
        prompt = f"""Generate a recipe for {meal} in valid JSON format.

        IMPORTANT: Your response must be ONLY the JSON object, with NO additional text or formatting.
        Use double quotes for all strings. Ensure all JSON keys and values are properly formatted.
        
        Required JSON structure:
        {{
            "description": "string: Brief description of the dish",
            "prep_time": number: preparation time in minutes,
            "cook_time": number: cooking time in minutes,
            "servings": number: number of servings (default 4),
            "ingredients": [
                {{
                    "name": "string: ingredient name",
                    "quantity": "string: exact quantity with unit (e.g., '2 tablespoons')",
                    "category": "string: one of [Produce, Dairy, Meat, Pantry, Spices, Other]",
                    "notes": "string: preparation notes (optional)"
                }}
            ],
            "instructions": [
                "string: Step 1",
                "string: Step 2",
                etc...
            ],
            "notes": "string: Additional tips or notes (optional)"
        }}

        Example of valid response format:
        {{
            "description": "A classic Italian pasta dish with rich tomato sauce",
            "prep_time": 15,
            "cook_time": 25,
            "servings": 4,
            "ingredients": [
                {{
                    "name": "spaghetti",
                    "quantity": "1 pound",
                    "category": "Pantry",
                    "notes": "dried"
                }},
                {{
                    "name": "olive oil",
                    "quantity": "2 tablespoons",
                    "category": "Pantry",
                    "notes": "extra virgin"
                }}
            ],
            "instructions": [
                "Bring a large pot of salted water to boil",
                "Cook pasta according to package directions"
            ],
            "notes": "For best results, use high-quality pasta"
        }}"""
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": """You are a professional chef creating recipes in JSON format.
                    IMPORTANT RULES:
                    1. Respond ONLY with the JSON object, no other text
                    2. Use proper JSON syntax with double quotes
                    3. Ensure all numbers are actual numbers (not strings)
                    4. Use consistent ingredient categories
                    5. Include exact measurements
                    6. Break instructions into clear, separate steps
                    7. Ensure all JSON is properly nested and formatted"""
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1000,
            response_format={ "type": "json_object" }  # Request JSON format
        )
        
        # Parse the response
        try:
            content = response.choices[0].message.content.strip()
            
            # Remove any potential markdown code block formatting
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            # Try to parse the JSON
            try:
                recipe_data = json.loads(content)
            except json.JSONDecodeError as e:
                console.print(f"[red]Error parsing JSON: {str(e)}[/red]")
                console.print("[yellow]Attempting to fix common JSON formatting issues...[/yellow]")
                
                # Try to fix common JSON formatting issues
                content = content.replace("'", '"')  # Replace single quotes with double quotes
                content = content.replace(""", '"').replace(""", '"')  # Replace smart quotes
                content = content.replace("\n", " ")  # Remove newlines
                
                # Try to parse again after fixes
                recipe_data = json.loads(content)
            
            # Validate required fields
            required_fields = ["description", "ingredients", "instructions"]
            missing_fields = [field for field in required_fields if not recipe_data.get(field)]
            if missing_fields:
                console.print(f"[red]Error: Missing required fields: {', '.join(missing_fields)}[/red]")
                return None
            
            # Create the recipe
            recipe = Recipe(
                name=meal,
                description=recipe_data["description"],
                prep_time=int(recipe_data.get("prep_time", 0)) if recipe_data.get("prep_time") else None,
                cook_time=int(recipe_data.get("cook_time", 0)) if recipe_data.get("cook_time") else None,
                servings=int(recipe_data.get("servings", 4)),
                notes=recipe_data.get("notes")
            )
            
            # Add ingredients
            for ingredient_data in recipe_data.get("ingredients", []):
                # Ensure required ingredient fields
                if not ingredient_data.get("name") or not ingredient_data.get("quantity"):
                    continue
                    
                ingredient = RecipeIngredient(
                    name=ingredient_data["name"],
                    quantity=ingredient_data["quantity"],
                    category=ingredient_data.get("category", "Other"),
                    notes=ingredient_data.get("notes")
                )
                recipe.add_ingredient(ingredient)
            
            # Add instructions
            for instruction in recipe_data.get("instructions", []):
                if instruction and isinstance(instruction, str):
                    recipe.add_instruction(instruction)
            
            # Validate the recipe has at least one ingredient and instruction
            if not recipe.ingredients or not recipe.instructions:
                console.print("[red]Error: Generated recipe must have at least one ingredient and one instruction[/red]")
                return None
            
            return recipe
            
        except Exception as e:
            console.print(f"[red]Error processing recipe: {str(e)}[/red]")
            console.print("[yellow]Raw response:[/yellow]")
            console.print(response.choices[0].message.content)
            return None
            
    except Exception as e:
        error_message = str(e)
        console.print(f"\n[red]Error generating recipe: {error_message}[/red]")
        
        if "401" in error_message:
            console.print("[yellow]Invalid API key. Please check your key in the .env file.[/yellow]")
        elif "429" in error_message:
            console.print("[yellow]Rate limit exceeded. Please try again later.[/yellow]")
        elif "500" in error_message:
            console.print("[yellow]OpenAI server error. Please try again later.[/yellow]")
        else:
            console.print("[yellow]An unexpected error occurred while generating the recipe.[/yellow]")
        
        return None 

def export_recipe_to_markdown(recipe: Recipe) -> str:
    """Export a recipe to markdown format.
    
    Args:
        recipe: The recipe to export
        
    Returns:
        str: The recipe in markdown format
    """
    # Create markdown content
    markdown = f"# {recipe.name}\n\n"
    
    # Add description
    if recipe.description:
        markdown += f"*{recipe.description}*\n\n"
    
    # Add preparation details
    markdown += "## Details\n\n"
    if recipe.prep_time:
        markdown += f"- **Prep Time:** {recipe.prep_time} minutes\n"
    if recipe.cook_time:
        markdown += f"- **Cook Time:** {recipe.cook_time} minutes\n"
    if recipe.get_total_time():
        markdown += f"- **Total Time:** {recipe.get_total_time()} minutes\n"
    markdown += f"- **Servings:** {recipe.servings}\n\n"
    
    # Add ingredients by category
    markdown += "## Ingredients\n\n"
    ingredients_by_category = recipe.get_ingredients_by_category()
    
    for category in sorted(ingredients_by_category.keys()):
        markdown += f"### {category}\n\n"
        for ingredient in sorted(ingredients_by_category[category], key=lambda x: x.name.lower()):
            markdown += f"- {ingredient.name} ({ingredient.quantity})"
            if ingredient.notes:
                markdown += f" - *{ingredient.notes}*"
            markdown += "\n"
        markdown += "\n"
    
    # Add instructions
    markdown += "## Instructions\n\n"
    for i, instruction in enumerate(recipe.instructions, 1):
        markdown += f"{i}. {instruction}\n"
    markdown += "\n"
    
    # Add notes if present
    if recipe.notes:
        markdown += "## Notes\n\n"
        markdown += f"{recipe.notes}\n\n"
    
    # Add metadata
    markdown += "---\n"
    markdown += f"*Created: {recipe.created_at.strftime('%Y-%m-%d %H:%M')}*\n"
    markdown += f"*Last Updated: {recipe.updated_at.strftime('%Y-%m-%d %H:%M')}*\n"
    
    return markdown 