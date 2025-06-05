"""
Write file command for SimpleAgent.

This module provides the write_file command for writing content to a file.
"""

import os
from commands import register_command


def write_file(file_path: str, content: str) -> str:
    """
    Write content to a file (overwrites existing content).
    
    Args:
        file_path: Path to the file to write to
        content: Content to write to the file
        
    Returns:
        Success or error message
    """
    try:        
        # Create directory if it doesn't exist
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
            
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
        return f"Successfully wrote to {os.path.basename(file_path)}"
    except Exception as e:
        return f"Error writing to file: {str(e)}"


# Define the schema for the write_file command
WRITE_FILE_SCHEMA = {
    "type": "function",
    "function": {
        "name": "write_file",
        "description": "Write content to a file (overwrites existing content)",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the file to write to"
                },
                "content": {
                    "type": "string",
                    "description": "Content to write to the file"
                }
            },
            "required": ["file_path", "content"]
        }
    }
}

# Register the command
register_command("write_file", write_file, WRITE_FILE_SCHEMA) 