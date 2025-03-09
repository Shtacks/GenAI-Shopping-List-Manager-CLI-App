from datetime import datetime
from typing import List, Optional, Dict
import os
from dotenv import load_dotenv
from openai import OpenAI
from rich.prompt import Prompt
from rich.console import Console
from src.models import ShoppingList, ShoppingItem, Recipe, RecipeIngredient
from src.database import (
    init_db,
    save_shopping_list,
    load_shopping_list,
    get_shopping_list_names,
    save_recipe,
    load_recipe,
    get_recipe_names,
    delete_shopping_list,
    delete_recipe
)

# Load environment variables
load_dotenv()

# Initialize console for user input
console = Console()

# Global variable to store the API key
api_key = os.getenv("OPENAI_API_KEY")

# Constants for markdown export directories
LIST_DIR = "lists"
SHOPPING_DIR = os.path.join(LIST_DIR, "shopping")
RECIPES_DIR = os.path.join(LIST_DIR, "recipes")
SHOPPING_MD_DIR = os.path.join(SHOPPING_DIR, "MD")
RECIPES_MD_DIR = os.path.join(RECIPES_DIR, "MD")

def ensure_directories_exist():
    """Ensure the required directories exist and initialize the database."""
    # Create markdown export directories
    os.makedirs(SHOPPING_MD_DIR, exist_ok=True)
    os.makedirs(RECIPES_MD_DIR, exist_ok=True)
    # Initialize the database
    init_db()

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

def get_client() -> OpenAI:
    """Get an OpenAI client with the current API key."""
    return OpenAI(api_key=get_api_key())

def generate_ingredient_list(meal: str) -> Optional[List[Dict[str, str]]]:
    """Generate a list of ingredients for a meal using GPT-3.5-turbo.
    
    Args:
        meal: The name of the meal to generate ingredients for
        
    Returns:
        Optional[List[Dict[str, str]]]: A list of dictionaries containing ingredient details,
                                      or None if generation fails
    """
    try:
        client = get_client()
        
        # Create a more explicit prompt for the model
        prompt = f"""Generate a list of ingredients needed to make {meal}.
        Format your response as a list of Python dictionaries, one per line, with NO other text or formatting.
        Each ingredient must be in this exact format:
        {{"name": "ingredient name", "quantity": "specific amount with units", "category": "category name", "notes": "optional notes"}}

        Use these specific categories:
        - Produce (for fruits, vegetables, herbs)
        - Dairy (for milk, cheese, eggs, butter)
        - Meat (for all meats, poultry, fish)
        - Pantry (for dry goods, canned items, oils)
        - Spices (for seasonings, spices, extracts)
        - Other (for anything that doesn't fit above)

        Example response:
        {{"name": "chicken breast", "quantity": "2 pounds", "category": "Meat", "notes": "boneless, skinless"}}
        {{"name": "onion", "quantity": "1 large", "category": "Produce", "notes": "diced"}}
        {{"name": "flour", "quantity": "2 cups", "category": "Pantry", "notes": "all-purpose"}}
        """
        
        # Call OpenAI API with adjusted parameters
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a precise cooking assistant. Generate ingredient lists with exact measurements and clear categories. Only output valid Python dictionaries, one per line, with no additional text."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,  # Lower temperature for more consistent formatting
            max_tokens=500
        )
        
        # Extract and parse the response
        ingredients_text = response.choices[0].message.content
        
        # Convert the text response into a list of dictionaries
        # Remove any markdown formatting and split into lines
        lines = ingredients_text.replace("```", "").strip().split("\n")
        ingredients = []
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
                
            try:
                # Try to evaluate the line as a Python dictionary
                ingredient = eval(line)
                if isinstance(ingredient, dict):
                    # Validate required fields
                    if not all(key in ingredient for key in ["name", "quantity", "category"]):
                        console.print(f"[yellow]Warning: Skipping ingredient missing required fields: {line}[/yellow]")
                        continue
                    
                    # Validate category
                    valid_categories = {"Produce", "Dairy", "Meat", "Pantry", "Spices", "Other"}
                    if ingredient["category"] not in valid_categories:
                        ingredient["category"] = "Other"
                    
                    # Ensure all fields exist with default values
                    ingredient.setdefault("notes", "")
                    
                    # Clean up the data
                    ingredient["name"] = ingredient["name"].strip().lower()
                    ingredient["quantity"] = ingredient["quantity"].strip()
                    ingredient["category"] = ingredient["category"].strip()
                    ingredient["notes"] = ingredient["notes"].strip()
                    
                    ingredients.append(ingredient)
            except Exception as e:
                console.print(f"[yellow]Warning: Could not parse ingredient: {line}[/yellow]")
                console.print(f"[yellow]Error: {str(e)}[/yellow]")
                continue
        
        if not ingredients:
            console.print("[red]Error: No valid ingredients were generated[/red]")
            return None
            
        return ingredients
        
    except Exception as e:
        console.print(f"\n[red]Error generating ingredient list: {str(e)}[/red]")
        if "maximum context length" in str(e).lower():
            console.print("[yellow]The response was too long. Please try again.[/yellow]")
        elif "rate limit" in str(e).lower():
            console.print("[yellow]Rate limit exceeded. Please wait a moment and try again.[/yellow]")
        return None

def generate_recipe(meal: str) -> Optional[Recipe]:
    """Generate a complete recipe using GPT-3.5-turbo.
    
    Args:
        meal: The name of the meal to generate a recipe for
        
    Returns:
        Optional[Recipe]: A complete recipe object, or None if generation fails
    """
    try:
        client = get_client()
        
        # Create a detailed prompt for the recipe with explicit formatting
        prompt = f"""Generate a complete recipe for {meal}.
        Format your response exactly as follows, including all section headers:

        Description:
        [A brief description of the dish]

        Prep Time:
        [Number] minutes

        Cook Time:
        [Number] minutes

        Servings:
        [Number]

        Ingredients:
        {{"name": "ingredient1", "quantity": "amount with units", "category": "category name", "notes": "optional notes"}}
        {{"name": "ingredient2", "quantity": "amount with units", "category": "category name", "notes": "optional notes"}}
        [Add more ingredients as needed]

        Instructions:
        1. [First step]
        2. [Second step]
        [Add more steps as needed]

        Notes:
        [Additional cooking tips or notes]

        Please ensure each ingredient is formatted as a proper Python dictionary on a single line.
        Categories should be one of: Produce, Dairy, Meat, Pantry, Spices, Other
        """
        
        # Call OpenAI API with increased tokens and adjusted temperature
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a professional chef. Generate detailed, accurate recipes with clear instructions and measurements. Always format ingredients as proper Python dictionaries and follow the exact format specified."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1500  # Increased token limit for more detailed recipes
        )
        
        # Parse the response
        recipe_text = response.choices[0].message.content
        
        # Split the response into sections
        sections = recipe_text.split("\n\n")
        
        # Create a new recipe object
        recipe = Recipe(name=meal)
        
        # Track which sections we've found for validation
        found_sections = set()
        
        for section in sections:
            section = section.strip()
            if not section:
                continue
            
            # Try to identify and parse each section
            if section.lower().startswith("description:"):
                recipe.description = section.split(":", 1)[1].strip()
                found_sections.add("description")
            
            elif section.lower().startswith("prep time:"):
                try:
                    time_str = section.split(":", 1)[1].strip()
                    recipe.prep_time = int(''.join(filter(str.isdigit, time_str)))
                    found_sections.add("prep_time")
                except:
                    console.print("[yellow]Warning: Could not parse prep time, setting to None[/yellow]")
                    recipe.prep_time = None
            
            elif section.lower().startswith("cook time:"):
                try:
                    time_str = section.split(":", 1)[1].strip()
                    recipe.cook_time = int(''.join(filter(str.isdigit, time_str)))
                    found_sections.add("cook_time")
                except:
                    console.print("[yellow]Warning: Could not parse cook time, setting to None[/yellow]")
                    recipe.cook_time = None
            
            elif section.lower().startswith("servings:"):
                try:
                    servings_str = section.split(":", 1)[1].strip()
                    recipe.servings = int(''.join(filter(str.isdigit, servings_str)))
                    found_sections.add("servings")
                except:
                    recipe.servings = 4
            
            elif "ingredients:" in section.lower():
                ingredients_text = section.split(":", 1)[1].strip()
                ingredient_count = 0
                for line in ingredients_text.split("\n"):
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    
                    try:
                        # Try to parse ingredient dictionary
                        ingredient_dict = eval(line)
                        if isinstance(ingredient_dict, dict) and "name" in ingredient_dict and "quantity" in ingredient_dict:
                            ingredient = RecipeIngredient(
                                name=ingredient_dict["name"],
                                quantity=ingredient_dict["quantity"],
                                category=ingredient_dict.get("category", "Other"),
                                notes=ingredient_dict.get("notes", "")
                            )
                            recipe.add_ingredient(ingredient)
                            ingredient_count += 1
                    except Exception as e:
                        console.print(f"[yellow]Warning: Could not parse ingredient: {line}[/yellow]")
                        continue
                
                if ingredient_count > 0:
                    found_sections.add("ingredients")
            
            elif "instructions:" in section.lower():
                instructions_text = section.split(":", 1)[1].strip()
                instruction_count = 0
                for line in instructions_text.split("\n"):
                    line = line.strip()
                    if line and not line.startswith("#"):
                        # Remove any numbering at the start
                        instruction = line.lstrip("0123456789. ")
                        if instruction:  # Only add non-empty instructions
                            recipe.add_instruction(instruction)
                            instruction_count += 1
                
                if instruction_count > 0:
                    found_sections.add("instructions")
            
            elif "notes:" in section.lower() or "tips:" in section.lower():
                recipe.notes = section.split(":", 1)[1].strip()
                found_sections.add("notes")
        
        # Validate the recipe has all required components
        required_sections = {"description", "ingredients", "instructions"}
        if not required_sections.issubset(found_sections):
            missing = required_sections - found_sections
            console.print(f"[red]Error: Recipe is missing required sections: {', '.join(missing)}[/red]")
            return None
            
        if not recipe.ingredients:
            console.print("[red]Error: No valid ingredients were parsed[/red]")
            return None
            
        if not recipe.instructions:
            console.print("[red]Error: No valid instructions were parsed[/red]")
            return None
        
        return recipe
        
    except Exception as e:
        console.print(f"\n[red]Error generating recipe: {str(e)}[/red]")
        if "maximum context length" in str(e).lower():
            console.print("[yellow]The recipe was too long. Try requesting a simpler recipe.[/yellow]")
        elif "rate limit" in str(e).lower():
            console.print("[yellow]Rate limit exceeded. Please wait a moment and try again.[/yellow]")
        return None

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

def export_recipe_to_markdown(recipe: Recipe) -> str:
    """Export a recipe to markdown format."""
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