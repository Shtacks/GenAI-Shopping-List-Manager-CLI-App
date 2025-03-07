from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime

@dataclass
class ShoppingItem:
    """Represents a single item in a shopping list.
    
    Attributes:
        name: The name of the item
        quantity: The quantity to purchase (default: 1)
        category: The category of the item (default: "Uncategorized")
        purchased: Whether the item has been purchased (default: False)
        notes: Optional notes about the item
        created_at: When the item was created
        updated_at: When the item was last updated
    """
    name: str
    quantity: int = 1
    category: str = "Uncategorized"
    purchased: bool = False
    notes: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

@dataclass
class ShoppingList:
    """Represents a collection of shopping items.
    
    Attributes:
        name: The name of the shopping list
        items: List of shopping items
        created_at: When the list was created
        updated_at: When the list was last updated
    """
    name: str
    items: List[ShoppingItem] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def add_item(self, item: ShoppingItem) -> None:
        """Add an item to the shopping list.
        
        Args:
            item: The shopping item to add
        """
        self.items.append(item)
        self.updated_at = datetime.now()

    def remove_item(self, item_name: str) -> bool:
        """Remove an item from the shopping list by name.
        
        Args:
            item_name: The name of the item to remove
            
        Returns:
            bool: True if the item was found and removed, False otherwise
        """
        for item in self.items:
            if item.name.lower() == item_name.lower():
                self.items.remove(item)
                self.updated_at = datetime.now()
                return True
        return False

    def get_items_by_category(self) -> Dict[str, List[ShoppingItem]]:
        """Group items by their category.
        
        Returns:
            Dict[str, List[ShoppingItem]]: A dictionary mapping categories to lists of items
        """
        categories: Dict[str, List[ShoppingItem]] = {}
        for item in self.items:
            if item.category not in categories:
                categories[item.category] = []
            categories[item.category].append(item)
        return categories 