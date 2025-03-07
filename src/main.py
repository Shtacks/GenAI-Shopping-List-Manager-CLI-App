from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from src.models import ShoppingList, ShoppingItem
from src.utils import save_list_to_file, load_list_from_file, get_saved_lists, organize_list, export_to_markdown

console = Console()

def display_menu() -> None:
    """Display the main menu options."""
    console.print("\n[bold cyan]Shopping List Organizer[/bold cyan]")
    console.print("1. Create new list")
    console.print("2. Add item to list")
    console.print("3. Show list")
    console.print("4. List all saved lists")
    console.print("5. Organize list")
    console.print("6. Export to .md")
    console.print("7. Remove items from list")
    console.print("8. Quit")
    console.print()

def create_list() -> None:
    """Create a new shopping list."""
    name = Prompt.ask("Enter list name")
    shopping_list = ShoppingList(name=name)
    save_list_to_file(shopping_list, f"{name}.json")
    console.print(f"[green]Created new shopping list: {name}[/green]")

def add_item():
    """Add items to an existing shopping list."""
    # Get list of saved lists
    saved_lists = get_saved_lists()
    
    if not saved_lists:
        console.print("[red]No saved lists found. Please create a list first.[/red]")
        return
    
    # Display available lists with numbers
    console.print("\n[cyan]Available lists:[/cyan]")
    for i, list_name in enumerate(saved_lists, 1):
        console.print(f"{i}. {list_name}")
    
    # Get user's choice
    while True:
        try:
            choice = int(Prompt.ask("\nEnter the number of the list to add items to"))
            if 1 <= choice <= len(saved_lists):
                break
            console.print("[red]Invalid choice. Please try again.[/red]")
        except ValueError:
            console.print("[red]Please enter a valid number.[/red]")
    
    # Get the selected list name
    list_name = saved_lists[choice - 1]
    filename = f"{list_name}.json"
    
    # Load the list
    shopping_list = load_list_from_file(filename)
    if not shopping_list:
        console.print(f"[red]Error loading list: {list_name}[/red]")
        return
    
    console.print("\n[bold cyan]Adding items to list. Type 'done' when finished.[/bold cyan]")
    
    while True:
        # Get item name with validation
        while True:
            name = Prompt.ask("\nEnter item name (or 'done' to finish)")
            if name.lower() == "done":
                break
            # Check if name is blank or just whitespace
            if name.strip():
                break
            console.print("[red]Item name cannot be blank. Please enter a valid name.[/red]")
        
        if name.lower() == "done":
            break
            
        # Get quantity
        while True:
            try:
                quantity = int(Prompt.ask("Enter quantity", default="1"))
                if quantity > 0:
                    break
                console.print("[red]Quantity must be greater than 0.[/red]")
            except ValueError:
                console.print("[red]Please enter a valid number.[/red]")
        
        # Get optional details
        category = Prompt.ask("Enter category (optional)", default="Other")
        notes = Prompt.ask("Enter notes (optional)", default="")
        
        # Create and add the item
        item = ShoppingItem(
            name=name.strip(),  # Ensure no leading/trailing whitespace
            quantity=quantity,
            category=category.strip() if category else "Other",  # Ensure no leading/trailing whitespace
            notes=notes.strip() if notes else ""  # Ensure no leading/trailing whitespace
        )
        shopping_list.add_item(item)
        
        # Save after each item
        if save_list_to_file(shopping_list, filename):
            console.print(f"[green]Added {quantity}x {name} to {list_name}[/green]")
        else:
            console.print(f"[red]Error saving list: {list_name}[/red]")
        
        # Show current list
        console.print("\n[bold]Current list:[/bold]")
        table = Table(show_header=False)
        table.add_column("Item", style="cyan")
        table.add_column("Quantity", justify="right")
        table.add_column("Category", style="magenta")
        table.add_column("Notes", style="yellow")
        
        for item in shopping_list.items:
            table.add_row(
                item.name,
                str(item.quantity),
                item.category,
                item.notes or ""
            )
        console.print(table)
        console.print()
    
    console.print(f"[green]Finished adding items to {list_name}[/green]")

def show_list() -> None:
    """Display a shopping list."""
    # Get list of saved lists
    saved_lists = get_saved_lists()
    
    if not saved_lists:
        console.print("[red]No saved lists found. Please create a list first.[/red]")
        return
    
    # Display available lists with numbers
    console.print("\n[cyan]Available lists:[/cyan]")
    for i, list_name in enumerate(saved_lists, 1):
        console.print(f"{i}. {list_name}")
    
    # Get user's choice
    while True:
        try:
            choice = int(Prompt.ask("\nEnter the number of the list to show"))
            if 1 <= choice <= len(saved_lists):
                break
            console.print("[red]Invalid choice. Please try again.[/red]")
        except ValueError:
            console.print("[red]Please enter a valid number.[/red]")
    
    # Get the selected list name
    list_name = saved_lists[choice - 1]
    shopping_list = load_list_from_file(f"{list_name}.json")
    if not shopping_list:
        console.print(f"[red]Error: List '{list_name}' not found[/red]")
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

    # Display items grouped by category
    for category, items in sorted(items_by_category.items()):
        # Create a table for each category
        table = Table(title=f"[bold]{category}[/bold]", show_header=True)
        table.add_column("Item", style="cyan")
        table.add_column("Quantity", justify="right")
        table.add_column("Status", style="green")
        table.add_column("Notes", style="yellow")

        # Add items to the table
        for item in sorted(items, key=lambda x: x.name.lower()):
            status = "✓" if item.purchased else " "
            table.add_row(
                item.name,
                str(item.quantity),
                status,
                item.notes or ""
            )

        console.print(table)
        console.print()  # Add spacing between categories

    # Show summary
    total_items = len(shopping_list.items)
    purchased_items = sum(1 for item in shopping_list.items if item.purchased)
    console.print(f"[bold]Summary:[/bold] {purchased_items}/{total_items} items purchased")

def list_all() -> None:
    """List all saved shopping lists."""
    lists = get_saved_lists()
    if not lists:
        console.print("[yellow]No shopping lists found[/yellow]")
        return

    table = Table(title="Saved Shopping Lists")
    table.add_column("Name", style="cyan")
    table.add_column("Items", justify="right")
    table.add_column("Last Updated", style="magenta")

    for list_name in lists:
        shopping_list = load_list_from_file(f"{list_name}.json")
        if shopping_list:
            table.add_row(
                list_name,
                str(len(shopping_list.items)),
                shopping_list.updated_at.strftime("%Y-%m-%d %H:%M")
            )

    console.print(table)

def organize_list_items() -> None:
    """Organize items in a list using GPT-4-mini."""
    list_name = Prompt.ask("Enter list name")
    shopping_list = load_list_from_file(f"{list_name}.json")
    if not shopping_list:
        console.print(f"[red]Error: List '{list_name}' not found[/red]")
        return

    console.print("[yellow]Organizing items...[/yellow]")
    try:
        organized_list = organize_list(shopping_list)
        save_list_to_file(organized_list, f"{list_name}.json")
        console.print("[green]Items organized successfully![/green]")
        show_list()  # Show the updated list
    except Exception as e:
        console.print(f"[red]Error organizing items: {str(e)}[/red]")

def export_to_markdown_file() -> None:
    """Export a shopping list to a markdown file."""
    list_name = Prompt.ask("Enter list name")
    shopping_list = load_list_from_file(f"{list_name}.json")
    if not shopping_list:
        console.print(f"[red]Error: List '{list_name}' not found[/red]")
        return

    try:
        markdown_content = export_to_markdown(shopping_list)
        filename = f"{list_name}.md"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        console.print(f"[green]List exported to {filename}[/green]")
    except Exception as e:
        console.print(f"[red]Error exporting list: {str(e)}[/red]")

def remove_items():
    """Remove items from an existing shopping list."""
    # Get list of saved lists
    saved_lists = get_saved_lists()
    
    if not saved_lists:
        console.print("[red]No saved lists found. Please create a list first.[/red]")
        return
    
    # Display available lists with numbers
    console.print("\n[cyan]Available lists:[/cyan]")
    for i, list_name in enumerate(saved_lists, 1):
        console.print(f"{i}. {list_name}")
    
    # Get user's choice
    while True:
        try:
            choice = int(Prompt.ask("\nEnter the number of the list to remove items from"))
            if 1 <= choice <= len(saved_lists):
                break
            console.print("[red]Invalid choice. Please try again.[/red]")
        except ValueError:
            console.print("[red]Please enter a valid number.[/red]")
    
    # Get the selected list name
    list_name = saved_lists[choice - 1]
    filename = f"{list_name}.json"
    
    # Load the list
    shopping_list = load_list_from_file(filename)
    if not shopping_list:
        console.print(f"[red]Error loading list: {list_name}[/red]")
        return
    
    if not shopping_list.items:
        console.print("[yellow]This list is empty. No items to remove.[/yellow]")
        return
    
    console.print("\n[bold cyan]Removing items from list. Type 'done' when finished.[/bold cyan]")
    
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
        choice = Prompt.ask("\nEnter the number of the item to remove (or 'done' to finish)")
        if choice.lower() == "done":
            break
            
        try:
            item_num = int(choice)
            if 1 <= item_num <= len(shopping_list.items):
                # Get confirmation
                item = shopping_list.items[item_num - 1]
                if Confirm.ask(f"Remove {item.quantity}x {item.name}?"):
                    shopping_list.items.pop(item_num - 1)
                    if save_list_to_file(shopping_list, filename):
                        console.print(f"[green]Removed {item.quantity}x {item.name}[/green]")
                    else:
                        console.print(f"[red]Error saving list: {list_name}[/red]")
            else:
                console.print("[red]Invalid item number. Please try again.[/red]")
        except ValueError:
            console.print("[red]Please enter a valid number or 'done'.[/red]")
    
    console.print(f"[green]Finished removing items from {list_name}[/green]")

def main() -> None:
    """Main application loop."""
    while True:
        display_menu()
        choice = Prompt.ask("Enter your choice", choices=["1", "2", "3", "4", "5", "6", "7", "8"])
        
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
            if Confirm.ask("Are you sure you want to quit?"):
                console.print("[yellow]Goodbye![/yellow]")
                break

if __name__ == "__main__":
    main()
