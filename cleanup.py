import json
from datetime import datetime
from typing import List, Dict, Any

def clean_shopping_list(filename: str) -> None:
    """Clean up a shopping list JSON file by removing items with blank names."""
    try:
        # Read the file
        with open(filename, 'r') as f:
            data = json.load(f)
        
        # Filter out items with blank names
        data['items'] = [item for item in data['items'] if item['name'].strip()]
        
        # Update the updated_at timestamp
        data['updated_at'] = datetime.now().isoformat()
        
        # Write back to file
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
            
        print(f"Successfully cleaned up {filename}")
        print(f"Removed {len(data['items'])} items with blank names")
        
    except Exception as e:
        print(f"Error cleaning up file: {e}")

if __name__ == "__main__":
    clean_shopping_list("Test 1.json") 