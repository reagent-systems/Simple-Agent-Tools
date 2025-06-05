"""
Read file command for SimpleAgent.

This module provides the read_file command for reading the contents of a file.
"""

import os
from commands import register_command


def read_file(file_path: str) -> str:
    """
    Read the contents of a file.
    
    Args:
        file_path: Path to the file to read
        
    Returns:
        The contents of the file as a string
    """
    try:
        if not os.path.exists(file_path):
            return f"Error: File not found: {os.path.basename(file_path)}"
            
        # Read the file
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"


# Define the schema for the read_file command
READ_FILE_SCHEMA = {
    "type": "function",
    "function": {
        "name": "read_file",
        "description": "Read the contents of a file",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the file to read"
                }
            },
            "required": ["file_path"]
        }
    }
}

# Register the command
register_command("read_file", read_file, READ_FILE_SCHEMA) 