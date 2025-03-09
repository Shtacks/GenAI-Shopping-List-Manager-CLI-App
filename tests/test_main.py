import os
import pytest
from datetime import datetime
from unittest.mock import Mock, patch
from src.models import ShoppingList, ShoppingItem, Recipe, RecipeIngredient
from src.database import (
    init_db, save_shopping_list, load_shopping_list, get_shopping_list_names,
    save_recipe, load_recipe, get_recipe_names, delete_shopping_list, delete_recipe
)
from src.utils import (
    ensure_directories_exist, get_markdown_path, get_api_key, get_client,
    generate_ingredient_list, generate_recipe, organize_list,
    export_to_markdown, export_recipe_to_markdown
)

# Test data
TEST_SHOPPING_LIST = ShoppingList(
    name="Test List",
    created_at=datetime.now(),
    updated_at=datetime.now()
)
TEST_SHOPPING_ITEM = ShoppingItem(
    name="Test Item",
    quantity=2,
    category="Test Category",
    notes="Test Notes"
)
TEST_RECIPE = Recipe(
    name="Test Recipe",
    description="Test Description",
    prep_time=30,
    cook_time=45,
    servings=4,
    notes="Test Notes"
)
TEST_RECIPE_INGREDIENT = RecipeIngredient(
    name="Test Ingredient",
    quantity="2 cups",
    category="Test Category",
    notes="Test Notes"
)

@pytest.fixture
def setup_database():
    """Setup a test database and clean it up after tests."""
    # Use an in-memory database for testing
    import src.database
    src.database.DATABASE_FILE = ":memory:"
    init_db()
    yield
    # Database is automatically cleaned up when connection is closed

@pytest.fixture
def setup_directories(tmp_path):
    """Setup test directories and clean them up after tests."""
    import src.utils
    src.utils.LIST_DIR = str(tmp_path / "lists")
    src.utils.SHOPPING_DIR = str(tmp_path / "lists/shopping")
    src.utils.RECIPES_DIR = str(tmp_path / "lists/recipes")
    src.utils.SHOPPING_MD_DIR = str(tmp_path / "lists/shopping/MD")
    src.utils.RECIPES_MD_DIR = str(tmp_path / "lists/recipes/MD")
    ensure_directories_exist()
    yield
    # Directories are automatically cleaned up by pytest

# Database Tests
def test_init_db(setup_database):
    """Test database initialization."""
    # Database is initialized in setup_database fixture
    assert True  # If we got here, initialization succeeded

def test_save_load_shopping_list(setup_database):
    """Test saving and loading shopping lists."""
    # Create and save a test shopping list
    test_list = TEST_SHOPPING_LIST
    test_list.add_item(TEST_SHOPPING_ITEM)
    assert save_shopping_list(test_list)
    
    # Load and verify the list
    loaded_list = load_shopping_list(test_list.name)
    assert loaded_list is not None
    assert loaded_list.name == test_list.name
    assert len(loaded_list.items) == 1
    assert loaded_list.items[0].name == TEST_SHOPPING_ITEM.name
    assert loaded_list.items[0].quantity == TEST_SHOPPING_ITEM.quantity

def test_save_load_recipe(setup_database):
    """Test saving and loading recipes."""
    # Create and save a test recipe
    test_recipe = TEST_RECIPE
    test_recipe.add_ingredient(TEST_RECIPE_INGREDIENT)
    test_recipe.add_instruction("Test Step 1")
    assert save_recipe(test_recipe)
    
    # Load and verify the recipe
    loaded_recipe = load_recipe(test_recipe.name)
    assert loaded_recipe is not None
    assert loaded_recipe.name == test_recipe.name
    assert len(loaded_recipe.ingredients) == 1
    assert loaded_recipe.ingredients[0].name == TEST_RECIPE_INGREDIENT.name
    assert len(loaded_recipe.instructions) == 1

def test_get_list_names(setup_database):
    """Test retrieving shopping list names."""
    # Save multiple lists
    list_names = ["List1", "List2", "List3"]
    for name in list_names:
        save_shopping_list(ShoppingList(name=name))
    
    # Get and verify names
    saved_names = get_shopping_list_names()
    assert len(saved_names) == len(list_names)
    assert all(name in saved_names for name in list_names)

def test_get_recipe_names(setup_database):
    """Test retrieving recipe names."""
    # Save multiple recipes
    recipe_names = ["Recipe1", "Recipe2", "Recipe3"]
    for name in recipe_names:
        save_recipe(Recipe(name=name))
    
    # Get and verify names
    saved_names = get_recipe_names()
    assert len(saved_names) == len(recipe_names)
    assert all(name in saved_names for name in recipe_names)

def test_delete_shopping_list(setup_database):
    """Test deleting shopping lists."""
    # Create and save a list
    save_shopping_list(TEST_SHOPPING_LIST)
    assert TEST_SHOPPING_LIST.name in get_shopping_list_names()
    
    # Delete and verify
    assert delete_shopping_list(TEST_SHOPPING_LIST.name)
    assert TEST_SHOPPING_LIST.name not in get_shopping_list_names()

def test_delete_recipe(setup_database):
    """Test deleting recipes."""
    # Create and save a recipe
    save_recipe(TEST_RECIPE)
    assert TEST_RECIPE.name in get_recipe_names()
    
    # Delete and verify
    assert delete_recipe(TEST_RECIPE.name)
    assert TEST_RECIPE.name not in get_recipe_names()

# Utility Tests
def test_ensure_directories_exist(setup_directories, tmp_path):
    """Test directory creation."""
    # Directories are created in setup_directories fixture
    assert os.path.exists(str(tmp_path / "lists/shopping/MD"))
    assert os.path.exists(str(tmp_path / "lists/recipes/MD"))

def test_get_markdown_path(setup_directories):
    """Test markdown path generation."""
    # Test shopping list path
    shopping_path = get_markdown_path("test_list.md", is_recipe=False)
    assert shopping_path.endswith("shopping/MD/test_list.md")
    
    # Test recipe path
    recipe_path = get_markdown_path("test_recipe.md", is_recipe=True)
    assert recipe_path.endswith("recipes/MD/test_recipe.md")

@patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'})
def test_get_api_key():
    """Test API key retrieval."""
    assert get_api_key() == 'test_key'

@patch('openai.OpenAI')
def test_get_client(mock_openai):
    """Test OpenAI client creation."""
    client = get_client()
    assert client is not None

# OpenAI Integration Tests
@patch('src.utils.get_client')
def test_generate_ingredient_list(mock_get_client):
    """Test ingredient list generation."""
    # Mock OpenAI response
    mock_client = Mock()
    mock_response = Mock()
    mock_response.choices = [Mock(message=Mock(content='''
        {"name": "chicken", "quantity": "2 pounds", "category": "Meat", "notes": "boneless"}
        {"name": "salt", "quantity": "1 tsp", "category": "Spices", "notes": ""}
    '''))]
    mock_client.chat.completions.create.return_value = mock_response
    mock_get_client.return_value = mock_client
    
    # Test generation
    ingredients = generate_ingredient_list("Test Meal")
    assert ingredients is not None
    assert len(ingredients) == 2
    assert ingredients[0]["name"] == "chicken"
    assert ingredients[1]["category"] == "Spices"

@patch('src.utils.get_client')
def test_generate_recipe(mock_get_client):
    """Test recipe generation."""
    # Mock OpenAI response
    mock_client = Mock()
    mock_response = Mock()
    mock_response.choices = [Mock(message=Mock(content='''
        Description:
        Test recipe description
        
        Prep Time:
        30 minutes
        
        Cook Time:
        45 minutes
        
        Servings:
        4
        
        Ingredients:
        {"name": "ingredient1", "quantity": "1 cup", "category": "Pantry", "notes": ""}
        
        Instructions:
        1. Test step one
        2. Test step two
        
        Notes:
        Test notes
    '''))]
    mock_client.chat.completions.create.return_value = mock_response
    mock_get_client.return_value = mock_client
    
    # Test generation
    recipe = generate_recipe("Test Recipe")
    assert recipe is not None
    assert recipe.name == "Test Recipe"
    assert recipe.prep_time == 30
    assert recipe.cook_time == 45
    assert len(recipe.ingredients) == 1
    assert len(recipe.instructions) == 2

@patch('src.utils.get_client')
def test_organize_list(mock_get_client):
    """Test shopping list organization."""
    # Create test list
    test_list = ShoppingList("Test List")
    test_list.add_item(ShoppingItem(name="apple", category="Uncategorized"))
    test_list.add_item(ShoppingItem(name="banana", category="Uncategorized"))
    
    # Mock OpenAI response
    mock_client = Mock()
    mock_response = Mock()
    mock_response.choices = [Mock(message=Mock(content='''
        Produce:
        - apple
        - banana
    '''))]
    mock_client.chat.completions.create.return_value = mock_response
    mock_get_client.return_value = mock_client
    
    # Test organization
    organized_list = organize_list(test_list)
    assert organized_list is not None
    assert all(item.category == "Produce" for item in organized_list.items)

# Export Tests
def test_export_to_markdown():
    """Test shopping list markdown export."""
    # Create test list
    test_list = TEST_SHOPPING_LIST
    test_list.add_item(TEST_SHOPPING_ITEM)
    
    # Generate and verify markdown
    markdown = export_to_markdown(test_list)
    assert markdown is not None
    assert test_list.name in markdown
    assert TEST_SHOPPING_ITEM.name in markdown
    assert TEST_SHOPPING_ITEM.category in markdown

def test_export_recipe_to_markdown():
    """Test recipe markdown export."""
    # Create test recipe
    test_recipe = TEST_RECIPE
    test_recipe.add_ingredient(TEST_RECIPE_INGREDIENT)
    test_recipe.add_instruction("Test Step 1")
    
    # Generate and verify markdown
    markdown = export_recipe_to_markdown(test_recipe)
    assert markdown is not None
    assert test_recipe.name in markdown
    assert test_recipe.description in markdown
    assert TEST_RECIPE_INGREDIENT.name in markdown
    assert "Test Step 1" in markdown

# Error Handling Tests
def test_invalid_shopping_list_load(setup_database):
    """Test loading non-existent shopping list."""
    assert load_shopping_list("NonExistentList") is None

def test_invalid_recipe_load(setup_database):
    """Test loading non-existent recipe."""
    assert load_recipe("NonExistentRecipe") is None

@patch('src.utils.get_client')
def test_ingredient_generation_error(mock_get_client):
    """Test handling of ingredient generation errors."""
    mock_client = Mock()
    mock_client.chat.completions.create.side_effect = Exception("API Error")
    mock_get_client.return_value = mock_client
    
    assert generate_ingredient_list("Test Meal") is None

@patch('src.utils.get_client')
def test_recipe_generation_error(mock_get_client):
    """Test handling of recipe generation errors."""
    mock_client = Mock()
    mock_client.chat.completions.create.side_effect = Exception("API Error")
    mock_get_client.return_value = mock_client
    
    assert generate_recipe("Test Recipe") is None 