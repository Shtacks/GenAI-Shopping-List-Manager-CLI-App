import os
from src.models import ShoppingList, ShoppingItem
from src.database import init_db, save_shopping_list, load_shopping_list

def main():
    # Delete existing database if it exists
    if os.path.exists("shopping_list.db"):
        try:
            os.remove("shopping_list.db")
            print("Deleted existing database")
        except Exception as e:
            print(f"Error deleting database: {e}")
            return
    
    # Initialize database
    try:
        init_db()
        print("Initialized database")
    except Exception as e:
        print(f"Error initializing database: {e}")
        return
    
    # Create test shopping list
    try:
        shopping_list = ShoppingList("Test List")
        shopping_list.add_item(ShoppingItem(
            name="Test Item",
            quantity=2.5,
            quantity_unit_of_measure="kg",
            category="Test Category"
        ))
        
        if save_shopping_list(shopping_list):
            print("Successfully created and saved shopping list")
        else:
            print("Failed to save shopping list")
            return
    except Exception as e:
        print(f"Error creating shopping list: {e}")
        return
    
    # Read back the saved list
    try:
        loaded_list = load_shopping_list("Test List")
        if loaded_list:
            print("\nLoaded shopping list:")
            print(f"Name: {loaded_list.name}")
            for item in loaded_list.items:
                print(f"\nItem: {item.name}")
                print(f"Quantity: {item.quantity} {item.quantity_unit_of_measure}")
                print(f"Category: {item.category}")
        else:
            print("Failed to load shopping list")
    except Exception as e:
        print(f"Error loading shopping list: {e}")

if __name__ == "__main__":
    main() 