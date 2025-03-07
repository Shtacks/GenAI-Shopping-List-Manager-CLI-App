import pytest
from src.models import ShoppingList, ShoppingItem
from src.utils import save_list_to_file, load_list_from_file

def test_create_shopping_list():
    """Test creating a new shopping list."""
    list_name = "Test List"
    shopping_list = ShoppingList(name=list_name)
    assert shopping_list.name == list_name
    assert len(shopping_list.items) == 0

def test_add_item():
    """Test adding an item to a shopping list."""
    shopping_list = ShoppingList(name="Test List")
    item = ShoppingItem(name="Test Item", quantity=2, category="Test Category")
    shopping_list.add_item(item)
    assert len(shopping_list.items) == 1
    assert shopping_list.items[0].name == "Test Item"

def test_remove_item():
    """Test removing an item from a shopping list."""
    shopping_list = ShoppingList(name="Test List")
    item = ShoppingItem(name="Test Item")
    shopping_list.add_item(item)
    assert shopping_list.remove_item("Test Item")
    assert len(shopping_list.items) == 0

def test_save_and_load_list(tmp_path):
    """Test saving and loading a shopping list."""
    shopping_list = ShoppingList(name="Test List")
    item = ShoppingItem(name="Test Item")
    shopping_list.add_item(item)
    
    filename = tmp_path / "test_list.json"
    assert save_list_to_file(shopping_list, str(filename))
    
    loaded_list = load_list_from_file(str(filename))
    assert loaded_list is not None
    assert loaded_list.name == shopping_list.name
    assert len(loaded_list.items) == 1
    assert loaded_list.items[0].name == "Test Item" 