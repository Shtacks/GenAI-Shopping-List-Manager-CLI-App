import json
from datetime import datetime
from typing import List, Optional, Dict
from pathlib import Path
import os
from dotenv import load_dotenv
from openai import OpenAI
from rich.prompt import Prompt
from rich.console import Console
from src.models import ShoppingList, ShoppingItem

# Load environment variables
load_dotenv()

# Initialize console for user input
console = Console()

# Global variable to store the API key
api_key = os.getenv("OPENAI_API_KEY")

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
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving list: {e}")
        return False

def load_list_from_file(filename: str) -> Optional[ShoppingList]:
    """Load a shopping list from a JSON file.
    
    Args:
        filename: The name of the file to load from
        
    Returns:
        Optional[ShoppingList]: The loaded shopping list, or None if loading failed
    """
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
        
        items = [
            ShoppingItem(
                name=item["name"],
                quantity=item["quantity"],
                category=item["category"],
                purchased=item["purchased"],
                notes=item["notes"],
                created_at=datetime.fromisoformat(item["created_at"]),
                updated_at=datetime.fromisoformat(item["updated_at"]),
            )
            for item in data["items"]
        ]
        
        shopping_list = ShoppingList(
            name=data["name"],
            items=items,
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
        )
        return shopping_list
    except Exception as e:
        print(f"Error loading list: {e}")
        return None

def get_saved_lists(directory: str = ".") -> List[str]:
    """Get a list of all saved shopping list files.
    
    Args:
        directory: The directory to search in (default: current directory)
        
    Returns:
        List[str]: List of shopping list filenames (without extension)
    """
    try:
        path = Path(directory)
        return [f.stem for f in path.glob("*.json")]
    except Exception as e:
        print(f"Error getting saved lists: {e}")
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
    prompt = f"""Categorize these shopping items into one of these categories: Produce, Frozen, Pantry, Meat, Dairy, Cold, Alcohol, or Household.
    
    Items:
    {items_text}
    
    Format your response as:
    Category:
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
                {"role": "system", "content": "You are a shopping list organizer. Categorize items into the specified categories."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,  # Lower temperature for more consistent results
            max_tokens=300,   # Reduced token limit
            n=1              # Single response
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
            console.print("[yellow]Falling back to simple categorization...[/yellow]")
        
        # Fallback to simple categorization if API call fails
        categories = {
            "Produce": ["apple", "banana", "lettuce", "tomato", "carrot", "onion", "potato", "fruit", "vegetable", "herb", "avocado", "cucumber", "pepper", "mushroom", "lemon", "lime", "orange", "grape", "berry"],
            "Frozen": ["frozen", "ice cream", "pizza", "french fries", "frozen dinner", "frozen vegetable", "frozen fruit", "frozen meat", "frozen fish", "frozen dessert"],
            "Pantry": ["rice", "pasta", "cereal", "flour", "sugar", "oil", "salt", "spice", "sauce", "canned", "dried", "nut", "seed", "grain", "bean", "soup", "snack", "cracker", "cookie", "chocolate", "coffee", "tea"],
            "Meat": ["chicken", "beef", "pork", "fish", "lamb", "turkey", "duck", "sausage", "bacon", "ham", "steak", "ground beef", "ground pork", "ground turkey", "seafood", "shrimp", "salmon", "tuna"],
            "Dairy": ["milk", "cheese", "yogurt", "butter", "cream", "sour cream", "cottage cheese", "whipping cream", "half and half", "heavy cream", "light cream"],
            "Cold": ["juice", "soda", "water", "energy drink", "sports drink", "iced tea", "iced coffee", "cold brew", "smoothie", "yogurt drink", "kombucha", "cold cuts", "deli meat", "sandwich meat"],
            "Alcohol": ["beer", "wine", "spirit", "liquor", "cocktail", "cider", "sake", "champagne", "vodka", "whiskey", "rum", "tequila", "gin"],
            "Household": ["paper towel", "toilet paper", "cleaning supply", "detergent", "soap", "shampoo", "conditioner", "toothpaste", "deodorant", "trash bag", "ziploc", "foil", "wrap", "battery", "light bulb", "air freshener"],
            "Other": []  # Default category
        }
        
        for item in shopping_list.items:
            item_name = item.name.lower()
            categorized = False
            
            for category, keywords in categories.items():
                if any(keyword in item_name for keyword in keywords):
                    item.category = category
                    categorized = True
                    break
            
            if not categorized:
                item.category = "Other"
        
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