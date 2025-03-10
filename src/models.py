from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime

@dataclass
class ShoppingItem:
    """Represents a single item in a shopping list.
    
    Attributes:
        name: The name of the item
        quantity: The quantity to purchase (default: 1.0)
        quantity_unit_of_measure: The unit of measure for the quantity (default: "pieces")
        category: The category of the item (default: "Uncategorized")
        purchased: Whether the item has been purchased (default: False)
        notes: Optional notes about the item
        created_at: When the item was created
        updated_at: When the item was last updated
    """
    name: str
    quantity: float = 1.0
    quantity_unit_of_measure: str = "pieces"
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

@dataclass
class RecipeIngredient:
    """Represents an ingredient in a recipe with its quantity and preparation notes.
    
    Attributes:
        name: The name of the ingredient
        quantity: The amount needed (e.g., "2 tablespoons", "1 cup")
        category: The category of the ingredient (e.g., "Produce", "Dairy")
        notes: Optional preparation notes (e.g., "finely diced", "room temperature")
    """
    name: str
    quantity: str
    category: str = "Other"
    notes: Optional[str] = None

@dataclass
class Recipe:
    """Represents a cooking recipe with ingredients and instructions.
    
    Attributes:
        name: The name of the recipe
        ingredients: List of ingredients needed
        instructions: List of step-by-step cooking instructions
        prep_time: Preparation time in minutes
        cook_time: Cooking time in minutes
        servings: Number of servings the recipe makes
        description: Brief description of the recipe
        notes: Additional notes or tips
        created_at: When the recipe was created
        updated_at: When the recipe was last updated
    """
    name: str
    ingredients: List[RecipeIngredient] = field(default_factory=list)
    instructions: List[str] = field(default_factory=list)
    prep_time: Optional[int] = None
    cook_time: Optional[int] = None
    servings: int = 4
    description: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def add_ingredient(self, ingredient: RecipeIngredient) -> None:
        """Add an ingredient to the recipe.
        
        Args:
            ingredient: The ingredient to add
        """
        self.ingredients.append(ingredient)
        self.updated_at = datetime.now()

    def add_instruction(self, instruction: str) -> None:
        """Add a cooking instruction step.
        
        Args:
            instruction: The instruction step to add
        """
        self.instructions.append(instruction)
        self.updated_at = datetime.now()

    def get_ingredients_by_category(self) -> Dict[str, List[RecipeIngredient]]:
        """Group ingredients by their category.
        
        Returns:
            Dict[str, List[RecipeIngredient]]: A dictionary mapping categories to lists of ingredients
        """
        categories: Dict[str, List[RecipeIngredient]] = {}
        for ingredient in self.ingredients:
            if ingredient.category not in categories:
                categories[ingredient.category] = []
            categories[ingredient.category].append(ingredient)
        return categories

    def to_shopping_list(self) -> ShoppingList:
        """Convert the recipe's ingredients into a shopping list.
        
        Returns:
            ShoppingList: A new shopping list containing all ingredients
        """
        shopping_list = ShoppingList(name=f"{self.name} ingredients")
        
        for ingredient in self.ingredients:
            # Try to extract numeric quantity if possible
            try:
                quantity_parts = ingredient.quantity.split()
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
                notes=f"{ingredient.quantity}" + (f" - {ingredient.notes}" if ingredient.notes else "")
            )
            shopping_list.add_item(item)
        
        return shopping_list

    def get_total_time(self) -> Optional[int]:
        """Get the total time needed for the recipe in minutes.
        
        Returns:
            Optional[int]: Total time in minutes, or None if times aren't specified
        """
        if self.prep_time is None or self.cook_time is None:
            return None
        return self.prep_time + self.cook_time 