import os
import uuid
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Union, Tuple

def generate_unique_id() -> str:
    """Generate a unique identifier using UUID4."""
    return str(uuid.uuid4())

def ensure_directory_exists(directory_path: Union[str, Path]) -> Path:
    """
    Ensure that a directory exists, creating it if necessary.
    
    Args:
        directory_path: Path to the directory to ensure exists
        
    Returns:
        Path object for the directory
    """
    path = Path(directory_path)
    path.mkdir(parents=True, exist_ok=True)
    return path

def format_file_size(size_bytes: int) -> str:
    """
    Format file size from bytes to human-readable format.
    
    Args:
        size_bytes: File size in bytes
        
    Returns:
        Human-readable file size (e.g., "2.5 MB")
    """
    # Define size units and their respective dividers
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    divider = 1024
    
    # Calculate appropriate unit
    size = size_bytes
    unit_index = 0
    
    while size >= divider and unit_index < len(units) - 1:
        size /= divider
        unit_index += 1
    
    # Format to 2 decimal places if not bytes
    if unit_index == 0:
        return f"{size} {units[unit_index]}"
    else:
        return f"{size:.2f} {units[unit_index]}"

def safe_get(data: Dict[str, Any], key: str, default: Any = None) -> Any:
    """
    Safely get a value from a dictionary, returning default if the key doesn't exist.
    
    Args:
        data: Dictionary to get value from
        key: Key to look up
        default: Default value to return if key is not found
        
    Returns:
        Value for the key, or default if not found
    """
    return data.get(key, default)

def save_json(data: Any, file_path: Union[str, Path]) -> None:
    """
    Save data as JSON to a file.
    
    Args:
        data: Data to save
        file_path: Path to save the file to
    """
    # Ensure directory exists
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    # Save the data
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_json(file_path: Union[str, Path]) -> Any:
    """
    Load data from a JSON file.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        Loaded data
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def check_file_exists(file_path: Union[str, Path]) -> bool:
    """
    Check if a file exists.
    
    Args:
        file_path: Path to the file
        
    Returns:
        True if the file exists, False otherwise
    """
    path = Path(file_path)
    return path.exists() and path.is_file()

def strip_html_tags(text: str) -> str:
    """
    Remove HTML tags from text.
    
    Args:
        text: Text containing HTML tags
        
    Returns:
        Clean text without HTML tags
    """
    import re
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename to be safe for file systems.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Replace disallowed characters with underscores
    import re
    sanitized = re.sub(r'[\\/*?:"<>|]', '_', filename)
    return sanitized
