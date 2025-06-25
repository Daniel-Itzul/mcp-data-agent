
import json

def get_catalog_data(catalog_path) -> str | None:
    """Get the database catalog."""
    with open(catalog_path, 'r') as file:
        data = json.load(file)
    return data