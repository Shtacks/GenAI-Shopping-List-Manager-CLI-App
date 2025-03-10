from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from src.models import ShoppingList, ShoppingItem
from src.utils import (
    organize_list,
    export_to_markdown,
    get_markdown_path,
    ensure_directories_exist,
    generate_ingredient_list,
    generate_recipe,
    export_recipe_to_markdown
)
from src.database import (
    save_shopping_list,
    load_shopping_list,
    get_shopping_list_names,
    save_recipe,
    load_recipe,
    get_recipe_names,
    delete_shopping_list,
    delete_recipe,
    get_pantry_items,
    add_pantry_item,
    remove_pantry_item
)

console = Console()

def display_shopping_menu() -> None:
    """Display the shopping list management menu options."""
    console.print("\n[bold cyan]Shopping List Manager[/bold cyan]")
    console.print("1. Create new list")
    console.print("2. Add item to list")
    console.print("3. Show list")
    console.print("4. List all saved lists")
    console.print("5. Organize list")
    console.print("6. Export list to .md")
    console.print("7. Remove items from list")
    console.print("8. Create list from Recipes")
    console.print("9. Mark Items as Purchased")
    console.print("10. Back to main menu")
    console.print()

def display_recipe_menu() -> None:
    """Display the recipe management menu options."""
    console.print("\n[bold cyan]Recipe Manager[/bold cyan]")
    console.print("1. Generate new recipe")
    console.print("2. Create new recipe")
    console.print("3. Show recipe")
    console.print("4. Export recipe to .md")
    console.print("5. Back to main menu")
    console.print()

def display_main_menu() -> None:
    """Display the main menu options."""
    console.print("\n[bold cyan]Kitchen Helper[/bold cyan]")
    console.print("1. Shopping List Manager")
    console.print("2. Recipe Manager")
    console.print("3. Pantry Manager")
    console.print("4. Quit")
    console.print()

def display_pantry_menu() -> None:
    """Display the pantry management menu options."""
    console.print("\n[bold cyan]Pantry Manager[/bold cyan]")
    console.print("1. Show Pantry Inventory")
    console.print("2. Add Items to Pantry")
    console.print("3. Edit Items in Pantry")
    console.print("4. Add Items to Pantry from Shopping List")
    console.print("5. Back to main menu")
    console.print()

def create_list() -> None:
    """Create a new shopping list and immediately start adding items."""
    name = Prompt.ask("Enter list name (or 'back' to return to main menu)")
    if name.lower() == 'back':
        return
    
    shopping_list = ShoppingList(name=name)
    if save_shopping_list(shopping_list):
        console.print(f"[green]Created new shopping list: {name}[/green]")
        
        # Start adding items immediately
        console.print("\n[bold cyan]Adding items to your new list. Type 'done' to finish or 'back' for main menu.[/bold cyan]")
        
        while True:
            # Get item name with validation
            while True:
                name = Prompt.ask("\nEnter item name (or 'done' to finish, 'back' for main menu)")
                if name.lower() in ['done', 'back']:
                    break
                # Check if name is blank or just whitespace
                if name.strip():
                    break
                console.print("[red]Item name cannot be blank. Please enter a valid name.[/red]")
            
            if name.lower() == 'back':
                return
            if name.lower() == 'done':
                break
                
            # Get quantity
            while True:
                try:
                    quantity = int(Prompt.ask("Enter quantity (or 'back' for main menu)", default="1"))
                    if str(quantity).lower() == 'back':
                        return
                    if quantity > 0:
                        break
                    console.print("[red]Quantity must be greater than 0.[/red]")
                except ValueError:
                    if str(quantity).lower() == 'back':
                        return
                    console.print("[red]Please enter a valid number.[/red]")
            
            # Get optional details
            category = Prompt.ask("Enter category (optional, or 'back' for main menu)", default="Other")
            if category.lower() == 'back':
                return
            notes = Prompt.ask("Enter notes (optional, or 'back' for main menu)", default="")
            if notes.lower() == 'back':
                return
            
            # Create and add the item
            item = ShoppingItem(
                name=name.strip(),
                quantity=quantity,
                category=category.strip() if category else "Other",
                notes=notes.strip() if notes else ""
            )
            shopping_list.add_item(item)
            
            # Save after each item
            if save_shopping_list(shopping_list):
                console.print(f"[green]Added {quantity}x {name} to {shopping_list.name}[/green]")
            else:
                console.print(f"[red]Error saving list: {shopping_list.name}[/red]")
            
            # Show current list
            console.print("\n[bold]Current list:[/bold]")
            table = Table(show_header=False)
            table.add_column("Item", style="cyan")
            table.add_column("Quantity", justify="right", style="green")
            table.add_column("Category", style="yellow")
            table.add_column("Notes", style="magenta")
            
            for item in sorted(shopping_list.items, key=lambda x: x.name.lower()):
                table.add_row(
                    item.name,
                    str(item.quantity) if item.quantity > 1 else "",
                    item.category,
                    item.notes or ""
                )
            console.print(table)
            console.print()
    else:
        console.print(f"[red]Error creating list: {name}[/red]")

def add_item() -> None:
    """Add items to an existing shopping list."""
    list_name, shopping_list = select_list("Select a list to add items to")
    if not shopping_list:
        return

    console.print("\n[bold cyan]Adding items to list. Type 'done' to finish or 'back' for main menu.[/bold cyan]")
    
    while True:
        # Get item name with validation
        while True:
            name = Prompt.ask("\nEnter item name (or 'done' to finish, 'back' for main menu)")
            if name.lower() in ['done', 'back']:
                break
            # Check if name is blank or just whitespace
            if name.strip():
                break
            console.print("[red]Item name cannot be blank. Please enter a valid name.[/red]")
        
        if name.lower() == 'back':
            return
        if name.lower() == 'done':
            break
            
        # Get quantity
        while True:
            try:
                quantity = int(Prompt.ask("Enter quantity (or 'back' for main menu)", default="1"))
                if str(quantity).lower() == 'back':
                    return
                if quantity > 0:
                    break
                console.print("[red]Quantity must be greater than 0.[/red]")
            except ValueError:
                if str(quantity).lower() == 'back':
                    return
                console.print("[red]Please enter a valid number.[/red]")
        
        # Get optional details
        category = Prompt.ask("Enter category (optional, or 'back' for main menu)", default="Other")
        if category.lower() == 'back':
            return
        notes = Prompt.ask("Enter notes (optional, or 'back' for main menu)", default="")
        if notes.lower() == 'back':
            return
        
        # Create and add the item
        item = ShoppingItem(
            name=name.strip(),
            quantity=quantity,
            category=category.strip() if category else "Other",
            notes=notes.strip() if notes else ""
        )
        shopping_list.add_item(item)
        
        # Save after each item
        if save_shopping_list(shopping_list):
            console.print(f"[green]Added {quantity}x {name} to {list_name}[/green]")
        else:
            console.print(f"[red]Error saving list: {list_name}[/red]")
        
        # Show current list
        console.print("\n[bold]Current list:[/bold]")
        table = Table(show_header=False)
        table.add_column("Item", style="cyan")
        table.add_column("Quantity", justify="right", style="green")
        table.add_column("Category", style="yellow")
        table.add_column("Notes", style="magenta")
        
        for item in sorted(shopping_list.items, key=lambda x: x.name.lower()):
            table.add_row(
                item.name,
                str(item.quantity) if item.quantity > 1 else "",
                item.category,
                item.notes or ""
            )
        console.print(table)
        console.print()

def show_list() -> None:
    """Display a shopping list."""
    list_name, shopping_list = select_list("Select a list to show")
    if not shopping_list:
        return

    # Group items by category
    items_by_category = {}
    for item in shopping_list.items:
        if item.category not in items_by_category:
            items_by_category[item.category] = []
        items_by_category[item.category].append(item)

    # Display header with list name and timestamps
    console.print(f"\n[bold cyan]Shopping List: {shopping_list.name}[/bold cyan]")
    console.print(f"[dim]Created: {shopping_list.created_at.strftime('%Y-%m-%d %H:%M')}[/dim]")
    console.print(f"[dim]Last Updated: {shopping_list.updated_at.strftime('%Y-%m-%d %H:%M')}[/dim]\n")

    # Display items by category
    for category in sorted(items_by_category.keys()):
        console.print(f"[bold]{category}[/bold]")
        table = Table(show_header=False)
        table.add_column("Item", style="cyan")
        table.add_column("Quantity", justify="right", style="green")
        table.add_column("Notes", style="yellow")
        table.add_column("Status", justify="center", style="magenta")
        
        for item in sorted(items_by_category[category], key=lambda x: x.name.lower()):
            status = "✓" if item.purchased else " "
            table.add_row(
                item.name,
                str(item.quantity) if item.quantity > 1 else "",
                item.notes or "",
                f"[{status}]"
            )
        console.print(table)
        console.print()

def list_all() -> None:
    """List all saved shopping lists."""
    lists = get_shopping_list_names()
    if not lists:
        console.print("[yellow]No shopping lists found[/yellow]")
        return

    table = Table(title="Saved Shopping Lists")
    table.add_column("Name", style="cyan")
    table.add_column("Items", justify="right")
    table.add_column("Last Updated", style="magenta")

    for list_name in lists:
        shopping_list = load_shopping_list(list_name)
        if shopping_list:
            table.add_row(
                list_name,
                str(len(shopping_list.items)),
                shopping_list.updated_at.strftime("%Y-%m-%d %H:%M")
            )

    console.print(table)

def select_list(prompt_text: str = "Select a list") -> tuple[str, ShoppingList]:
    """Helper function to select a list from available lists.
    
    Args:
        prompt_text: The text to show when prompting for list selection
        
    Returns:
        tuple[str, ShoppingList]: The selected list name and loaded shopping list object,
                                 or (None, None) if no list was selected or found
    """
    saved_lists = get_shopping_list_names()
    
    if not saved_lists:
        console.print("[red]No saved lists found. Please create a list first.[/red]")
        return None, None
    
    # Display available lists with numbers
    console.print("\n[cyan]Available lists:[/cyan]")
    for i, list_name in enumerate(saved_lists, 1):
        console.print(f"{i}. {list_name}")
    console.print(f"{len(saved_lists) + 1}. Back to main menu")
    
    # Get user's choice
    while True:
        try:
            choice = int(Prompt.ask(f"\n{prompt_text} (enter number)"))
            if choice == len(saved_lists) + 1:  # Back option selected
                return None, None
            if 1 <= choice <= len(saved_lists):
                break
            console.print("[red]Invalid choice. Please try again.[/red]")
        except ValueError:
            console.print("[red]Please enter a valid number.[/red]")
    
    # Get the selected list name and load the list
    list_name = saved_lists[choice - 1]
    shopping_list = load_shopping_list(list_name)
    
    if not shopping_list:
        console.print(f"[red]Error: List '{list_name}' not found[/red]")
        return None, None
        
    return list_name, shopping_list

def organize_list_items() -> None:
    """Organize items in a list using GPT-4-mini."""
    list_name, shopping_list = select_list("Select a list to organize")
    if not shopping_list:
        return

    console.print("[yellow]Organizing items...[/yellow]")
    try:
        organized_list = organize_list(shopping_list)
        save_shopping_list(organized_list)
        console.print("[green]Items organized successfully![/green]")
        show_list()  # Show the updated list
    except Exception as e:
        console.print(f"[red]Error organizing items: {str(e)}[/red]")

def export_to_markdown_file() -> None:
    """Export a shopping list to a markdown file."""
    list_name, shopping_list = select_list("Select a list to export")
    if not shopping_list:
        return

    try:
        markdown_content = export_to_markdown(shopping_list)
        filename = get_markdown_path(f"{list_name}.md", is_recipe=False)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        console.print(f"[green]List exported to {filename}[/green]")
    except Exception as e:
        console.print(f"[red]Error exporting list: {str(e)}[/red]")

def remove_items():
    """Remove items from an existing shopping list."""
    list_name, shopping_list = select_list("Select a list to remove items from")
    if not shopping_list:
        return
    
    if not shopping_list.items:
        console.print("[yellow]This list is empty. No items to remove.[/yellow]")
        return
    
    console.print("\n[bold cyan]Removing items from list. Type 'done' to finish or 'back' for main menu.[/bold cyan]")
    
    while True:
        # Show current list with numbers
        console.print("\n[bold]Current list:[/bold]")
        table = Table(show_header=False)
        table.add_column("#", justify="right", style="dim")
        table.add_column("Item", style="cyan")
        table.add_column("Quantity", justify="right")
        table.add_column("Category", style="magenta")
        table.add_column("Notes", style="yellow")
        
        for i, item in enumerate(shopping_list.items, 1):
            table.add_row(
                str(i),
                item.name,
                str(item.quantity),
                item.category,
                item.notes or ""
            )
        console.print(table)
        
        # Get item number to remove
        choice = Prompt.ask("\nEnter the number of the item to remove (or 'done' to finish, 'back' for main menu)")
        if choice.lower() == 'back':
            return
        if choice.lower() == 'done':
            break
            
        try:
            item_num = int(choice)
            if 1 <= item_num <= len(shopping_list.items):
                # Get confirmation
                item = shopping_list.items[item_num - 1]
                if Confirm.ask(f"Remove {item.quantity}x {item.name}?"):
                    shopping_list.items.pop(item_num - 1)
                    if save_shopping_list(shopping_list):
                        console.print(f"[green]Removed {item.quantity}x {item.name}[/green]")
                    else:
                        console.print(f"[red]Error saving list: {list_name}[/red]")
            else:
                console.print("[red]Invalid item number. Please try again.[/red]")
        except ValueError:
            console.print("[red]Please enter a valid number, 'done', or 'back'.[/red]")
    
    console.print(f"[green]Finished removing items from {list_name}[/green]")

def create_list_from_recipes() -> None:
    """Create a new shopping list from multiple recipes."""
    recipe_names = get_recipe_names()
    
    if not recipe_names:
        console.print("[yellow]No saved recipes found[/yellow]")
        return
    
    selected_recipes = []
    
    while True:
        # Display available recipes with numbers
        console.print("\n[cyan]Available recipes:[/cyan]")
        for i, name in enumerate(recipe_names, 1):
            # Mark already selected recipes
            if name in selected_recipes:
                console.print(f"{i}. [green]✓[/green] {name}")
            else:
                console.print(f"{i}. {name}")
        console.print(f"{len(recipe_names) + 1}. Done selecting")
        console.print(f"{len(recipe_names) + 2}. Back to main menu")
        
        # Get user's choice
        while True:
            try:
                choice = int(Prompt.ask("\nSelect a recipe to add to your list (enter number)"))
                if choice == len(recipe_names) + 2:  # Back option selected
                    return
                if choice == len(recipe_names) + 1:  # Done selecting
                    if not selected_recipes:
                        console.print("[red]Please select at least one recipe.[/red]")
                        continue
                    break
                if 1 <= choice <= len(recipe_names):
                    recipe_name = recipe_names[choice - 1]
                    if recipe_name in selected_recipes:
                        selected_recipes.remove(recipe_name)
                        console.print(f"[yellow]Removed {recipe_name} from selection[/yellow]")
                    else:
                        selected_recipes.append(recipe_name)
                        console.print(f"[green]Added {recipe_name} to selection[/green]")
                    break
                console.print("[red]Invalid choice. Please try again.[/red]")
            except ValueError:
                console.print("[red]Please enter a valid number.[/red]")
        
        if choice == len(recipe_names) + 1:  # Done selecting
            break
    
    # Create a new shopping list
    list_name = Prompt.ask("Enter a name for your shopping list", default="Combined Recipe List")
    shopping_list = ShoppingList(name=list_name)
    
    # Add ingredients from all selected recipes
    for recipe_name in selected_recipes:
        recipe = load_recipe(recipe_name)
        if not recipe:
            console.print(f"[red]Error: Could not load recipe '{recipe_name}'[/red]")
            continue
        
        # Add ingredients from this recipe
        for ingredient in recipe.ingredients:
            try:
                # Try to extract numeric quantity if possible
                quantity_parts = ingredient.quantity.split()
                try:
                    if '/' in quantity_parts[0]:  # Handle fractions
                        num, denom = quantity_parts[0].split('/')
                        quantity = int(num) / int(denom)
                    else:
                        quantity = float(quantity_parts[0])
                    quantity = max(1, round(quantity))  # Ensure at least 1, round to nearest whole number
                except (ValueError, IndexError):
                    quantity = 1
                
                item = ShoppingItem(
                    name=ingredient.name,
                    quantity=quantity,
                    category=ingredient.category,
                    notes=f"{ingredient.quantity}" + (f" - {ingredient.notes}" if ingredient.notes else "") + f" (from {recipe_name})"
                )
                
                # Check if item already exists
                existing_item = next((i for i in shopping_list.items if i.name.lower() == item.name.lower()), None)
                if existing_item:
                    # Update existing item
                    existing_item.quantity += item.quantity
                    existing_item.notes += f", {item.notes}"
                else:
                    shopping_list.add_item(item)
            except Exception as e:
                console.print(f"[red]Error adding ingredient {ingredient.name}: {str(e)}[/red]")
                continue
    
    # Save the list
    if save_shopping_list(shopping_list):
        console.print(f"[green]Created new shopping list: {list_name}[/green]")
        
        # Show the created list grouped by category
        console.print("\n[bold]Generated shopping list:[/bold]")
        
        # Group items by category
        items_by_category = shopping_list.get_items_by_category()
        
        for category in sorted(items_by_category.keys()):
            console.print(f"\n[bold]{category}[/bold]")
            table = Table(show_header=False)
            table.add_column("Item", style="cyan")
            table.add_column("Quantity", justify="right", style="green")
            table.add_column("Notes", style="yellow")
            
            for item in sorted(items_by_category[category], key=lambda x: x.name.lower()):
                table.add_row(
                    item.name,
                    str(item.quantity) if item.quantity > 1 else "",
                    item.notes or ""
                )
            console.print(table)
    else:
        console.print(f"[red]Error saving list: {list_name}[/red]")

def show_recipe() -> None:
    """Display a saved recipe."""
    recipe_names = get_recipe_names()
    
    if not recipe_names:
        console.print("[yellow]No saved recipes found[/yellow]")
        return
    
    # Display available recipes with numbers
    console.print("\n[cyan]Available recipes:[/cyan]")
    for i, name in enumerate(recipe_names, 1):
        console.print(f"{i}. {name}")
    console.print(f"{len(recipe_names) + 1}. Back to main menu")
    
    # Get user's choice
    while True:
        try:
            choice = int(Prompt.ask("\nSelect a recipe to view (enter number)"))
            if choice == len(recipe_names) + 1:  # Back option selected
                return
            if 1 <= choice <= len(recipe_names):
                break
            console.print("[red]Invalid choice. Please try again.[/red]")
        except ValueError:
            console.print("[red]Please enter a valid number.[/red]")
    
    # Get and display the selected recipe
    recipe_name = recipe_names[choice - 1]
    recipe = load_recipe(recipe_name)
    
    if not recipe:
        console.print(f"[red]Error: Recipe '{recipe_name}' not found[/red]")
        return
    
    # Display recipe header
    console.print(f"\n[bold cyan]{recipe.name}[/bold cyan]")
    if recipe.description:
        console.print(f"\n[italic]{recipe.description}[/italic]")
    
    # Display preparation details
    console.print("\n[bold]Details:[/bold]")
    if recipe.prep_time:
        console.print(f"Prep Time: {recipe.prep_time} minutes")
    if recipe.cook_time:
        console.print(f"Cook Time: {recipe.cook_time} minutes")
    if recipe.get_total_time():
        console.print(f"Total Time: {recipe.get_total_time()} minutes")
    console.print(f"Servings: {recipe.servings}")
    
    # Display ingredients by category
    console.print("\n[bold]Ingredients:[/bold]")
    ingredients_by_category = recipe.get_ingredients_by_category()
    
    for category in sorted(ingredients_by_category.keys()):
        console.print(f"\n[bold]{category}[/bold]")
        table = Table(show_header=False)
        table.add_column("Ingredient", style="cyan")
        table.add_column("Quantity", style="green")
        table.add_column("Notes", style="yellow")
        
        for ingredient in sorted(ingredients_by_category[category], key=lambda x: x.name.lower()):
            table.add_row(
                ingredient.name,
                ingredient.quantity,
                ingredient.notes or ""
            )
        console.print(table)
    
    # Display instructions
    console.print("\n[bold]Instructions:[/bold]")
    for i, instruction in enumerate(recipe.instructions, 1):
        console.print(f"\n{i}. {instruction}")
    
    # Display additional notes
    if recipe.notes:
        console.print(f"\n[bold]Notes:[/bold]\n{recipe.notes}")
    
    # Option to create shopping list
    if Confirm.ask("\nWould you like to create a shopping list from this recipe?"):
        shopping_list = recipe.to_shopping_list()
        if save_shopping_list(shopping_list):
            console.print(f"[green]Created shopping list: {shopping_list.name}[/green]")
        else:
            console.print("[red]Error creating shopping list[/red]")

def generate_new_recipe() -> None:
    """Generate a new recipe using GPT-4o-mini."""
    meal = Prompt.ask("Enter meal name (or 'back' to return to main menu)")
    if meal.lower() == 'back':
        return
        
    console.print(f"\n[yellow]Generating recipe for {meal}...[/yellow]")
    recipe = generate_recipe(meal)
    
    if not recipe:
        console.print("[red]Failed to generate recipe. Please try again.[/red]")
        return
    
    # Save the recipe
    if save_recipe(recipe):
        console.print(f"[green]Recipe saved successfully![/green]")
        
        # Display the generated recipe
        console.print("\n[bold]Generated Recipe:[/bold]")
        if recipe.description:
            console.print(f"\n[italic]{recipe.description}[/italic]")
        
        # Display preparation details
        console.print("\n[bold]Details:[/bold]")
        if recipe.prep_time:
            console.print(f"Prep Time: {recipe.prep_time} minutes")
        if recipe.cook_time:
            console.print(f"Cook Time: {recipe.cook_time} minutes")
        if recipe.get_total_time():
            console.print(f"Total Time: {recipe.get_total_time()} minutes")
        console.print(f"Servings: {recipe.servings}")
        
        # Display ingredients by category
        console.print("\n[bold]Ingredients:[/bold]")
        ingredients_by_category = recipe.get_ingredients_by_category()
        
        for category in sorted(ingredients_by_category.keys()):
            console.print(f"\n[bold]{category}[/bold]")
            table = Table(show_header=False)
            table.add_column("Ingredient", style="cyan")
            table.add_column("Quantity", style="green")
            table.add_column("Notes", style="yellow")
            
            for ingredient in sorted(ingredients_by_category[category], key=lambda x: x.name.lower()):
                table.add_row(
                    ingredient.name,
                    ingredient.quantity,
                    ingredient.notes or ""
                )
            console.print(table)
        
        # Display instructions
        console.print("\n[bold]Instructions:[/bold]")
        for i, instruction in enumerate(recipe.instructions, 1):
            console.print(f"\n{i}. {instruction}")
        
        # Display additional notes
        if recipe.notes:
            console.print(f"\n[bold]Notes:[/bold]\n{recipe.notes}")
        
        # Option to create shopping list
        if Confirm.ask("\nWould you like to create a shopping list from this recipe?"):
            shopping_list = recipe.to_shopping_list()
            if save_shopping_list(shopping_list):
                console.print(f"[green]Created shopping list: {shopping_list.name}[/green]")
            else:
                console.print("[red]Error creating shopping list[/red]")
    else:
        console.print("[red]Error saving recipe[/red]")

def export_recipe_to_markdown_file() -> None:
    """Export a recipe to a markdown file."""
    recipe_names = get_recipe_names()
    
    if not recipe_names:
        console.print("[yellow]No saved recipes found[/yellow]")
        return
    
    # Display available recipes with numbers
    console.print("\n[cyan]Available recipes:[/cyan]")
    for i, name in enumerate(recipe_names, 1):
        console.print(f"{i}. {name}")
    console.print(f"{len(recipe_names) + 1}. Back to main menu")
    
    # Get user's choice
    while True:
        try:
            choice = int(Prompt.ask("\nSelect a recipe to export (enter number)"))
            if choice == len(recipe_names) + 1:  # Back option selected
                return
            if 1 <= choice <= len(recipe_names):
                break
            console.print("[red]Invalid choice. Please try again.[/red]")
        except ValueError:
            console.print("[red]Please enter a valid number.[/red]")
    
    # Get and export the selected recipe
    recipe_name = recipe_names[choice - 1]
    recipe = load_recipe(recipe_name)
    
    if not recipe:
        console.print(f"[red]Error: Recipe '{recipe_name}' not found[/red]")
        return
    
    try:
        markdown_content = export_recipe_to_markdown(recipe)
        filename = get_markdown_path(f"{recipe_name}.md", is_recipe=True)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        console.print(f"[green]Recipe exported to {filename}[/green]")
    except Exception as e:
        console.print(f"[red]Error exporting recipe: {str(e)}[/red]")

def create_new_recipe() -> None:
    """Create a new recipe manually by entering ingredients and instructions."""
    # Get basic recipe information
    name = Prompt.ask("Enter recipe name (or 'back' to return to main menu)")
    if name.lower() == 'back':
        return
    
    description = Prompt.ask("Enter recipe description (optional)", default="")
    
    # Get preparation details
    while True:
        try:
            prep_time = int(Prompt.ask("Enter prep time in minutes", default="0"))
            if prep_time >= 0:
                break
            console.print("[red]Prep time cannot be negative.[/red]")
        except ValueError:
            console.print("[red]Please enter a valid number.[/red]")
    
    while True:
        try:
            cook_time = int(Prompt.ask("Enter cook time in minutes", default="0"))
            if cook_time >= 0:
                break
            console.print("[red]Cook time cannot be negative.[/red]")
        except ValueError:
            console.print("[red]Please enter a valid number.[/red]")
    
    while True:
        try:
            servings = int(Prompt.ask("Enter number of servings", default="4"))
            if servings > 0:
                break
            console.print("[red]Servings must be greater than 0.[/red]")
        except ValueError:
            console.print("[red]Please enter a valid number.[/red]")
    
    # Create recipe object
    from src.models import Recipe, RecipeIngredient
    recipe = Recipe(
        name=name,
        description=description,
        prep_time=prep_time,
        cook_time=cook_time,
        servings=servings
    )
    
    # Get ingredients
    console.print("\n[bold cyan]Adding ingredients. Type 'done' to finish or 'back' for main menu.[/bold cyan]")
    while True:
        name = Prompt.ask("\nEnter ingredient name (or 'done' to finish, 'back' for main menu)")
        if name.lower() == 'back':
            return
        if name.lower() == 'done':
            if not recipe.ingredients:
                console.print("[red]Recipe must have at least one ingredient.[/red]")
                continue
            break
        
        quantity = Prompt.ask("Enter quantity (e.g., '2 cups', '1/2 tsp')")
        category = Prompt.ask("Enter category", default="Other")
        notes = Prompt.ask("Enter notes (optional)", default="")
        
        ingredient = RecipeIngredient(
            name=name.strip(),
            quantity=quantity.strip(),
            category=category.strip(),
            notes=notes.strip()
        )
        recipe.add_ingredient(ingredient)
        
        # Show current ingredients
        console.print("\n[bold]Current ingredients:[/bold]")
        ingredients_by_category = recipe.get_ingredients_by_category()
        for category in sorted(ingredients_by_category.keys()):
            console.print(f"\n[bold]{category}[/bold]")
            table = Table(show_header=False)
            table.add_column("Ingredient", style="cyan")
            table.add_column("Quantity", style="green")
            table.add_column("Notes", style="yellow")
            
            for ingredient in sorted(ingredients_by_category[category], key=lambda x: x.name.lower()):
                table.add_row(
                    ingredient.name,
                    ingredient.quantity,
                    ingredient.notes or ""
                )
            console.print(table)
    
    # Get instructions
    console.print("\n[bold cyan]Adding instructions. Type 'done' to finish or 'back' for main menu.[/bold cyan]")
    step_number = 1
    while True:
        instruction = Prompt.ask(f"\nEnter step {step_number} (or 'done' to finish, 'back' for main menu)")
        if instruction.lower() == 'back':
            return
        if instruction.lower() == 'done':
            if not recipe.instructions:
                console.print("[red]Recipe must have at least one instruction.[/red]")
                continue
            break
        
        recipe.add_instruction(instruction.strip())
        step_number += 1
        
        # Show current instructions
        console.print("\n[bold]Current instructions:[/bold]")
        for i, step in enumerate(recipe.instructions, 1):
            console.print(f"\n{i}. {step}")
    
    # Get additional notes
    notes = Prompt.ask("\nEnter additional notes (optional)", default="")
    if notes:
        recipe.notes = notes
    
    # Save the recipe
    if save_recipe(recipe):
        console.print(f"[green]Recipe '{recipe.name}' saved successfully![/green]")
        
        # Option to create shopping list
        if Confirm.ask("\nWould you like to create a shopping list from this recipe?"):
            shopping_list = recipe.to_shopping_list()
            if save_shopping_list(shopping_list):
                console.print(f"[green]Created shopping list: {shopping_list.name}[/green]")
            else:
                console.print("[red]Error creating shopping list[/red]")
    else:
        console.print(f"[red]Error saving recipe: {recipe.name}[/red]")

def show_pantry_inventory() -> None:
    """Display all items in the pantry organized by category."""
    items = get_pantry_items()
    if not items:
        console.print("[yellow]No items in pantry[/yellow]")
        return

    # Group items by category
    items_by_category = {}
    for item in items:
        category = item['category']
        if category not in items_by_category:
            items_by_category[category] = []
        items_by_category[category].append(item)

    # Display items by category
    console.print("\n[bold cyan]Pantry Inventory[/bold cyan]")
    
    for category in sorted(items_by_category.keys()):
        console.print(f"\n[bold]{category}[/bold]")
        table = Table(show_header=True)
        table.add_column("Item", style="cyan")
        table.add_column("Quantity", justify="right", style="green")
        table.add_column("Unit", style="blue")
        table.add_column("Expiry Date", style="yellow")
        table.add_column("Notes", style="magenta")
        
        for item in sorted(items_by_category[category], key=lambda x: x['name'].lower()):
            expiry = item['expiry_date'].strftime("%Y-%m-%d") if item['expiry_date'] else ""
            table.add_row(
                item['name'],
                str(item['quantity']),
                item['unit'],
                expiry,
                item['notes'] or ""
            )
        console.print(table)

def add_items_to_pantry() -> None:
    """Add new items to the pantry."""
    console.print("\n[bold cyan]Adding items to pantry. Type 'done' to finish or 'back' for main menu.[/bold cyan]")
    
    while True:
        # Get item name
        name = Prompt.ask("\nEnter item name (or 'done' to finish, 'back' for main menu)")
        if name.lower() == 'back':
            return
        if name.lower() == 'done':
            break
        if not name.strip():
            console.print("[red]Item name cannot be blank.[/red]")
            continue
        
        # Get quantity and unit
        while True:
            try:
                quantity = float(Prompt.ask("Enter quantity"))
                if quantity > 0:
                    break
                console.print("[red]Quantity must be greater than 0.[/red]")
            except ValueError:
                console.print("[red]Please enter a valid number.[/red]")
        
        unit = Prompt.ask("Enter unit of measurement (e.g., g, ml, pieces)")
        
        # Get optional details
        category = Prompt.ask("Enter category", default="Other")
        
        expiry_str = Prompt.ask("Enter expiry date (YYYY-MM-DD) or leave blank", default="")
        expiry_date = None
        if expiry_str:
            try:
                expiry_date = datetime.strptime(expiry_str, "%Y-%m-%d")
            except ValueError:
                console.print("[red]Invalid date format. Using no expiry date.[/red]")
        
        notes = Prompt.ask("Enter notes (optional)", default="")
        
        # Add the item
        if add_pantry_item(
            name=name.strip(),
            quantity=quantity,
            unit=unit.strip(),
            category=category.strip(),
            expiry_date=expiry_date,
            notes=notes.strip()
        ):
            console.print(f"[green]Added {quantity} {unit} of {name} to pantry[/green]")
        else:
            console.print(f"[red]Error adding {name} to pantry[/red]")

def edit_pantry_items() -> None:
    """Edit or remove items in the pantry."""
    items = get_pantry_items()
    if not items:
        console.print("[yellow]No items in pantry[/yellow]")
        return
    
    while True:
        # Show current inventory with numbers
        console.print("\n[bold]Current Inventory:[/bold]")
        table = Table(show_header=True)
        table.add_column("#", justify="right", style="dim")
        table.add_column("Item", style="cyan")
        table.add_column("Quantity", justify="right", style="green")
        table.add_column("Unit", style="blue")
        table.add_column("Category", style="yellow")
        table.add_column("Expiry Date", style="magenta")
        
        for i, item in enumerate(items, 1):
            expiry = item['expiry_date'].strftime("%Y-%m-%d") if item['expiry_date'] else ""
            table.add_row(
                str(i),
                item['name'],
                str(item['quantity']),
                item['unit'],
                item['category'],
                expiry
            )
        console.print(table)
        
        # Get item selection
        choice = Prompt.ask(
            "\nEnter item number to edit, 'remove' to delete an item, 'done' to finish, or 'back' for main menu",
            choices=["remove", "done", "back"] + [str(i) for i in range(1, len(items) + 1)]
        )
        
        if choice.lower() == 'back':
            return
        if choice.lower() == 'done':
            break
        
        if choice.lower() == 'remove':
            remove_num = int(Prompt.ask("Enter number of item to remove"))
            if 1 <= remove_num <= len(items):
                item = items[remove_num - 1]
                if Confirm.ask(f"Remove {item['name']} from pantry?"):
                    if remove_pantry_item(item['name']):
                        console.print(f"[green]Removed {item['name']} from pantry[/green]")
                        items = get_pantry_items()  # Refresh the list
                    else:
                        console.print(f"[red]Error removing {item['name']} from pantry[/red]")
            else:
                console.print("[red]Invalid item number[/red]")
            continue
        
        # Edit selected item
        item_num = int(choice)
        if 1 <= item_num <= len(items):
            item = items[item_num - 1]
            console.print(f"\n[bold]Editing {item['name']}[/bold]")
            
            # Get new quantity
            while True:
                try:
                    quantity = float(Prompt.ask("Enter new quantity", default=str(item['quantity'])))
                    if quantity > 0:
                        break
                    console.print("[red]Quantity must be greater than 0.[/red]")
                except ValueError:
                    console.print("[red]Please enter a valid number.[/red]")
            
            unit = Prompt.ask("Enter unit of measurement", default=item['unit'])
            category = Prompt.ask("Enter category", default=item['category'])
            
            current_expiry = item['expiry_date'].strftime("%Y-%m-%d") if item['expiry_date'] else ""
            expiry_str = Prompt.ask("Enter expiry date (YYYY-MM-DD) or leave blank", default=current_expiry)
            expiry_date = None
            if expiry_str:
                try:
                    expiry_date = datetime.strptime(expiry_str, "%Y-%m-%d")
                except ValueError:
                    console.print("[red]Invalid date format. Using no expiry date.[/red]")
            
            notes = Prompt.ask("Enter notes", default=item['notes'] or "")
            
            # Update the item
            if add_pantry_item(
                name=item['name'],
                quantity=quantity,
                unit=unit.strip(),
                category=category.strip(),
                expiry_date=expiry_date,
                notes=notes.strip()
            ):
                console.print(f"[green]Updated {item['name']} in pantry[/green]")
                items = get_pantry_items()  # Refresh the list
            else:
                console.print(f"[red]Error updating {item['name']} in pantry[/red]")
        else:
            console.print("[red]Invalid item number[/red]")

def add_from_shopping_list() -> None:
    """Add items to pantry from a shopping list."""
    list_name, shopping_list = select_list("Select a shopping list to add items from")
    if not shopping_list:
        return
    
    if not shopping_list.items:
        console.print("[yellow]Selected list is empty[/yellow]")
        return
    
    # Show only purchased items
    purchased_items = [item for item in shopping_list.items if item.purchased]
    if not purchased_items:
        console.print("[yellow]No purchased items in the selected list[/yellow]")
        return
    
    console.print("\n[bold cyan]Select items to add to pantry:[/bold cyan]")
    for i, item in enumerate(purchased_items, 1):
        console.print(f"{i}. {item.name} ({item.quantity})")
    console.print(f"{len(purchased_items) + 1}. Add all items")
    console.print(f"{len(purchased_items) + 2}. Back to main menu")
    
    while True:
        try:
            choice = int(Prompt.ask("\nEnter item number"))
            if choice == len(purchased_items) + 2:  # Back option
                return
            if choice == len(purchased_items) + 1:  # Add all option
                items_to_add = purchased_items
                break
            if 1 <= choice <= len(purchased_items):
                items_to_add = [purchased_items[choice - 1]]
                break
            console.print("[red]Invalid choice[/red]")
        except ValueError:
            console.print("[red]Please enter a valid number[/red]")
    
    # Add selected items to pantry
    for item in items_to_add:
        # Get unit for the item
        unit = Prompt.ask(f"Enter unit of measurement for {item.name}", default="pieces")
        
        # Add to pantry
        if add_pantry_item(
            name=item.name,
            quantity=float(item.quantity),
            unit=unit.strip(),
            category=item.category,
            notes=item.notes
        ):
            console.print(f"[green]Added {item.quantity} {unit} of {item.name} to pantry[/green]")
        else:
            console.print(f"[red]Error adding {item.name} to pantry[/red]")

def pantry_menu_loop() -> None:
    """Pantry management menu loop."""
    while True:
        display_pantry_menu()
        choice = Prompt.ask("Enter your choice", choices=["1", "2", "3", "4", "5"])
        
        if choice == "1":
            show_pantry_inventory()
        elif choice == "2":
            add_items_to_pantry()
        elif choice == "3":
            edit_pantry_items()
        elif choice == "4":
            add_from_shopping_list()
        elif choice == "5":
            break

def mark_items_purchased() -> None:
    """Mark items in a shopping list as purchased."""
    list_name, shopping_list = select_list("Select a list to mark items as purchased")
    if not shopping_list:
        return
    
    if not shopping_list.items:
        console.print("[yellow]This list is empty. No items to mark.[/yellow]")
        return
    
    console.print("\n[bold cyan]Mark items as purchased. Type 'done' to finish or 'back' for main menu.[/bold cyan]")
    
    while True:
        # Group items by category
        items_by_category = {}
        for i, item in enumerate(shopping_list.items, 1):
            if item.category not in items_by_category:
                items_by_category[item.category] = []
            items_by_category[item.category].append((i, item))
        
        # Show current list with numbers and purchase status, grouped by category
        console.print("\n[bold]Current list:[/bold]")
        
        # Create a mapping of indices to items for easy lookup
        index_to_item = {}
        
        for category in sorted(items_by_category.keys()):
            console.print(f"\n[bold]{category}[/bold]")
            table = Table(show_header=True)
            table.add_column("#", justify="right", style="dim")
            table.add_column("Item", style="cyan")
            table.add_column("Quantity", justify="right", style="green")
            table.add_column("Notes", style="yellow")
            table.add_column("Status", justify="center", style="magenta")
            
            # Sort items within category by name
            for i, item in sorted(items_by_category[category], key=lambda x: x[1].name.lower()):
                status = "[✓]" if item.purchased else "[ ]"
                table.add_row(
                    str(i),
                    item.name,
                    str(item.quantity),
                    item.notes or "",
                    status
                )
                index_to_item[i] = item
            console.print(table)
        
        # Get item number to mark
        choice = Prompt.ask("\nEnter item number to toggle purchased status (or 'all' to mark all, 'done' to finish, 'back' for main menu)")
        if choice.lower() == 'back':
            return
        if choice.lower() == 'done':
            break
            
        if choice.lower() == 'all':
            # Get confirmation
            mark_all = Confirm.ask("Mark all items as purchased?")
            if mark_all:
                for item in shopping_list.items:
                    item.purchased = True
                if save_shopping_list(shopping_list):
                    console.print("[green]Marked all items as purchased[/green]")
                else:
                    console.print(f"[red]Error saving list: {list_name}[/red]")
            continue
            
        try:
            item_num = int(choice)
            if item_num in index_to_item:
                # Toggle the purchased status
                item = index_to_item[item_num]
                item.purchased = not item.purchased
                status = "purchased" if item.purchased else "unpurchased"
                if save_shopping_list(shopping_list):
                    console.print(f"[green]Marked {item.name} as {status}[/green]")
                else:
                    console.print(f"[red]Error saving list: {list_name}[/red]")
            else:
                console.print("[red]Invalid item number. Please try again.[/red]")
        except ValueError:
            if choice.lower() not in ['done', 'back', 'all']:
                console.print("[red]Please enter a valid number, 'all', 'done', or 'back'.[/red]")
    
    console.print(f"[green]Finished updating items in {list_name}[/green]")

def shopping_menu_loop() -> None:
    """Shopping list management menu loop."""
    while True:
        display_shopping_menu()
        choice = Prompt.ask("Enter your choice", choices=["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"])
        
        if choice == "1":
            create_list()
        elif choice == "2":
            add_item()
        elif choice == "3":
            show_list()
        elif choice == "4":
            list_all()
        elif choice == "5":
            organize_list_items()
        elif choice == "6":
            export_to_markdown_file()
        elif choice == "7":
            remove_items()
        elif choice == "8":
            create_list_from_recipes()
        elif choice == "9":
            mark_items_purchased()
        elif choice == "10":
            break

def recipe_menu_loop() -> None:
    """Recipe management menu loop."""
    while True:
        display_recipe_menu()
        choice = Prompt.ask("Enter your choice", choices=["1", "2", "3", "4", "5"])
        
        if choice == "1":
            generate_new_recipe()
        elif choice == "2":
            create_new_recipe()
        elif choice == "3":
            show_recipe()
        elif choice == "4":
            export_recipe_to_markdown_file()
        elif choice == "5":
            break

def main() -> None:
    """Main application loop."""
    # Ensure directories exist and handle migration at startup
    ensure_directories_exist()
    
    while True:
        display_main_menu()
        choice = Prompt.ask("Enter your choice", choices=["1", "2", "3", "4"])
        
        if choice == "1":
            shopping_menu_loop()
        elif choice == "2":
            recipe_menu_loop()
        elif choice == "3":
            pantry_menu_loop()
        elif choice == "4":
            if Confirm.ask("Are you sure you want to quit?"):
                console.print("[yellow]Goodbye![/yellow]")
                break

if __name__ == "__main__":
    main()
