from datetime import datetime
from typing import List, Optional, Dict
import os
from pathlib import Path
from src.models import ShoppingList, Recipe

# Constants for markdown export directories
MARKDOWN_DIR = "markdown"
SHOPPING_MD_DIR = os.path.join(MARKDOWN_DIR, "shopping")
RECIPES_MD_DIR = os.path.join(MARKDOWN_DIR, "recipes")

def ensure_directories_exist() -> None:
    """Ensure all required directories exist."""
    # Create data directory if it doesn't exist
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # Create markdown directories if they don't exist
    markdown_dir = Path(MARKDOWN_DIR)
    markdown_dir.mkdir(exist_ok=True)
    
    shopping_md_dir = Path(SHOPPING_MD_DIR)
    shopping_md_dir.mkdir(exist_ok=True)
    
    recipes_md_dir = Path(RECIPES_MD_DIR)
    recipes_md_dir.mkdir(exist_ok=True)

def get_markdown_path(filename: str, is_recipe: bool = False) -> Path:
    """Get the full path for a markdown file.
    
    Args:
        filename: Name of the markdown file
        is_recipe: Whether this is a recipe file (True) or shopping list file (False)
        
    Returns:
        Path: Full path to the markdown file
    """
    base_dir = RECIPES_MD_DIR if is_recipe else SHOPPING_MD_DIR
    return Path(base_dir) / filename

def export_to_markdown(shopping_list: ShoppingList) -> str:
    """Export a shopping list to markdown format."""
    # Create markdown content
    markdown = f"# {shopping_list.name}\n\n"
    
    # Group items by category
    items_by_category = {}
    for item in shopping_list.items:
        if item.category not in items_by_category:
            items_by_category[item.category] = []
        items_by_category[item.category].append(item)
    
    # Add items by category
    for category in sorted(items_by_category.keys()):
        markdown += f"## {category}\n\n"
        for item in sorted(items_by_category[category], key=lambda x: x.name.lower()):
            markdown += f"- {item.name}"
            if item.quantity:
                markdown += f" ({item.quantity} {item.quantity_unit_of_measure})"
            if item.notes:
                markdown += f" - {item.notes}"
            markdown += "\n"
        markdown += "\n"
    
    return markdown

def export_recipe_to_markdown(recipe: Recipe) -> str:
    """Export a recipe to markdown format."""
    # Create markdown content
    markdown = f"# {recipe.name}\n\n"
    
    if recipe.description:
        markdown += f"*{recipe.description}*\n\n"
    
    # Add preparation details
    markdown += "## Details\n\n"
    if recipe.prep_time:
        markdown += f"- Prep Time: {recipe.prep_time} minutes\n"
    if recipe.cook_time:
        markdown += f"- Cook Time: {recipe.cook_time} minutes\n"
    if recipe.get_total_time():
        markdown += f"- Total Time: {recipe.get_total_time()} minutes\n"
    markdown += f"- Servings: {recipe.servings}\n\n"
    
    # Add ingredients by category
    markdown += "## Ingredients\n\n"
    ingredients_by_category = recipe.get_ingredients_by_category()
    
    for category in sorted(ingredients_by_category.keys()):
        markdown += f"### {category}\n\n"
        for ingredient in sorted(ingredients_by_category[category], key=lambda x: x.name.lower()):
            markdown += f"- {ingredient.name}"
            if ingredient.quantity:
                markdown += f" ({ingredient.quantity})"
            if ingredient.notes:
                markdown += f" - {ingredient.notes}"
            markdown += "\n"
        markdown += "\n"
    
    # Add instructions
    markdown += "## Instructions\n\n"
    for i, instruction in enumerate(recipe.instructions, 1):
        markdown += f"{i}. {instruction}\n\n"
    
    # Add notes if any
    if recipe.notes:
        markdown += f"## Notes\n\n{recipe.notes}\n"
    
    return markdown 