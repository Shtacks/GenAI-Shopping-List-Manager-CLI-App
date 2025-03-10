from typing import List, Dict, Optional
import os
from openai import OpenAI
from rich.console import Console
from src.models import ShoppingList, Recipe, RecipeIngredient
from dotenv import load_dotenv

console = Console()

# Load environment variables
load_dotenv()

def get_client() -> OpenAI:
    """Get OpenAI client with API key from environment variables."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")
    return OpenAI(api_key=api_key)

def generate_recipe_from_ingredients(ingredients_text: str) -> Optional[Recipe]:
    """Generate a recipe using available ingredients.
    
    Args:
        ingredients_text: Formatted text of available ingredients
        
    Returns:
        Optional[Recipe]: Generated recipe object or None if generation fails
    """
    try:
        client = get_client()
        
        # Create a detailed prompt for the recipe with explicit formatting
        prompt = f"""Generate a creative and delicious recipe using these available ingredients:

{ingredients_text}

Format your response exactly as follows, including all section headers:

Recipe Name:
[Creative and descriptive name for the dish]

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
Only use ingredients from the provided list, adjusting quantities as needed.
Make the recipe name creative and appetizing based on the available ingredients.
"""
        
        # Call OpenAI API with increased tokens and adjusted temperature
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a professional chef. Generate creative and delicious recipes using only the provided ingredients. Always format ingredients as proper Python dictionaries and follow the exact format specified."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1500
        )
        
        # Parse the response
        recipe_text = response.choices[0].message.content
        
        # Split the response into sections
        sections = recipe_text.split("\n\n")
        
        # Get recipe name from the first section
        recipe_name = None
        for section in sections:
            if section.lower().startswith("recipe name:"):
                recipe_name = section.split(":", 1)[1].strip()
                break
        
        if not recipe_name:
            console.print("[red]Error: Could not find recipe name in generated content[/red]")
            return None
        
        # Create a new recipe object
        recipe = Recipe(name=recipe_name)
        
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

def generate_recipe_from_name(meal: str) -> Optional[Recipe]:
    """Generate a recipe from a meal name.
    
    Args:
        meal: Name of the meal to generate a recipe for
        
    Returns:
        Optional[Recipe]: Generated recipe object or None if generation fails
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
            max_tokens=1500
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

def generate_recipe_by_meal_type(meal_type: str) -> Optional[Recipe]:
    """Generate a recipe based on meal type.
    
    Args:
        meal_type: Type of meal (e.g., "Breakfast", "Lunch", "Dinner", etc.)
        
    Returns:
        Optional[Recipe]: Generated recipe object or None if generation fails
    """
    try:
        client = get_client()
        
        # Create a detailed prompt for the recipe with explicit formatting
        prompt = f"""Generate a creative and delicious {meal_type} recipe.
        Format your response exactly as follows, including all section headers:

        Recipe Name:
        [Creative and descriptive name for the {meal_type.lower()} dish]

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
        Make the recipe name creative and appetizing.
        """
        
        # Call OpenAI API with increased tokens and adjusted temperature
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"You are a professional chef specializing in {meal_type.lower()} recipes. Generate creative and delicious recipes that are appropriate for {meal_type.lower()}. Always format ingredients as proper Python dictionaries and follow the exact format specified."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1500
        )
        
        # Parse the response
        recipe_text = response.choices[0].message.content
        
        # Split the response into sections
        sections = recipe_text.split("\n\n")
        
        # Get recipe name from the first section
        recipe_name = None
        for section in sections:
            if section.lower().startswith("recipe name:"):
                recipe_name = section.split(":", 1)[1].strip()
                break
        
        if not recipe_name:
            console.print("[red]Error: Could not find recipe name in generated content[/red]")
            return None
        
        # Create a new recipe object
        recipe = Recipe(name=recipe_name)
        
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

def organize_shopping_list(shopping_list: ShoppingList) -> ShoppingList:
    """Organize items in a shopping list using GPT-3.5-turbo."""
    try:
        client = get_client()
        
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

def convert_to_shopping_quantities(ingredients: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Convert recipe quantities to practical shopping quantities.
    
    Args:
        ingredients: List of dictionaries containing ingredient details with recipe quantities
        
    Returns:
        List[Dict[str, str]]: List of ingredients with converted shopping quantities
    """
    try:
        client = get_client()
        
        # Create a prompt for converting quantities
        ingredients_text = "\n".join([
            f"- {ing['name']}: {ing['quantity']}"
            for ing in ingredients
        ])
        
        prompt = f"""Convert these recipe quantities into practical shopping quantities.
        For example:
        - 1/3 cup milk -> {{"name": "milk", "quantity": 0.5, "quantity_unit_of_measure": "gallon", "category": "Dairy", "notes": "recipe needs: 1/3 cup"}}
        - 2 tbsp olive oil -> {{"name": "olive oil", "quantity": 16.0, "quantity_unit_of_measure": "oz", "category": "Pantry", "notes": "recipe needs: 2 tbsp"}}
        - 1/4 tsp salt -> {{"name": "salt", "quantity": 1.0, "quantity_unit_of_measure": "container", "category": "Spices", "notes": "recipe needs: 1/4 tsp"}}
        - 2 eggs -> {{"name": "eggs", "quantity": 12.0, "quantity_unit_of_measure": "pieces", "category": "Dairy", "notes": "recipe needs: 2 eggs"}}
        
        Recipe ingredients:
        {ingredients_text}
        
        Format your response as a list of Python dictionaries, one per line, with NO other text or formatting.
        Each ingredient must be in this exact format:
        {{"name": "ingredient name", "quantity": float_value, "quantity_unit_of_measure": "shopping unit", "category": "category name", "notes": "original recipe quantity"}}
        
        Use these specific categories:
        - Produce (for fruits, vegetables, herbs)
        - Dairy (for milk, cheese, eggs, butter)
        - Meat (for all meats, poultry, fish)
        - Pantry (for dry goods, canned items, oils)
        - Spices (for seasonings, spices, extracts)
        - Other (for anything that doesn't fit above)
        
        Make quantities practical for shopping. For example:
        - Small amounts of spices should be converted to standard container sizes
        - Liquid ingredients should be converted to standard bottle sizes
        - Perishable items should be converted to standard package sizes
        
        IMPORTANT:
        - quantity must be a float value (e.g., 0.5, 1.0, 2.5)
        - quantity_unit_of_measure must be a text string (e.g., "pieces", "kg", "gallon")
        - Do not include units in the quantity field
        - Always specify both quantity and quantity_unit_of_measure separately
        """
        
        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a shopping assistant. Convert recipe quantities into practical shopping quantities that make sense for grocery shopping. Only output valid Python dictionaries, one per line, with no additional text. Always separate quantity (as float) and unit of measure (as text)."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1000
        )
        
        # Parse the response
        converted_text = response.choices[0].message.content
        
        # Convert the text response into a list of dictionaries
        lines = converted_text.replace("```", "").strip().split("\n")
        converted_ingredients = []
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
                
            try:
                # Try to evaluate the line as a Python dictionary
                ingredient = eval(line)
                if isinstance(ingredient, dict):
                    # Validate required fields
                    required_fields = ["name", "quantity", "quantity_unit_of_measure", "category"]
                    if not all(key in ingredient for key in required_fields):
                        console.print(f"[yellow]Warning: Skipping ingredient missing required fields: {line}[/yellow]")
                        continue
                    
                    # Validate category
                    valid_categories = {"Produce", "Dairy", "Meat", "Pantry", "Spices", "Other"}
                    if ingredient["category"] not in valid_categories:
                        ingredient["category"] = "Other"
                    
                    # Ensure quantity is float
                    try:
                        ingredient["quantity"] = float(ingredient["quantity"])
                    except (ValueError, TypeError):
                        console.print(f"[yellow]Warning: Invalid quantity value for {ingredient['name']}, setting to 1.0[/yellow]")
                        ingredient["quantity"] = 1.0
                    
                    # Ensure quantity_unit_of_measure is text
                    if not isinstance(ingredient["quantity_unit_of_measure"], str):
                        ingredient["quantity_unit_of_measure"] = str(ingredient["quantity_unit_of_measure"])
                    
                    # Ensure all fields exist with default values
                    ingredient.setdefault("notes", "")
                    
                    # Clean up the data
                    ingredient["name"] = ingredient["name"].strip()
                    ingredient["quantity_unit_of_measure"] = ingredient["quantity_unit_of_measure"].strip()
                    ingredient["category"] = ingredient["category"].strip()
                    ingredient["notes"] = ingredient["notes"].strip()
                    
                    # Validate the cleaned data
                    if not ingredient["quantity_unit_of_measure"]:
                        ingredient["quantity_unit_of_measure"] = "pieces"
                    
                    converted_ingredients.append(ingredient)
            except Exception as e:
                console.print(f"[yellow]Warning: Could not parse ingredient: {line}[/yellow]")
                console.print(f"[yellow]Error: {str(e)}[/yellow]")
                continue
        
        if not converted_ingredients:
            console.print("[red]Error: No valid ingredients were converted[/red]")
            return ingredients
            
        return converted_ingredients
        
    except Exception as e:
        console.print(f"\n[red]Error converting quantities: {str(e)}[/red]")
        if "maximum context length" in str(e).lower():
            console.print("[yellow]The response was too long. Please try again.[/yellow]")
        elif "rate limit" in str(e).lower():
            console.print("[yellow]Rate limit exceeded. Please wait a moment and try again.[/yellow]")
        return ingredients 