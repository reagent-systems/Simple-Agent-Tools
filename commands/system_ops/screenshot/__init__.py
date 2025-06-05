"""
Screenshot command for SimpleAgent.

This module provides the take_screenshot command for capturing a screenshot.
"""

import os
import pyautogui
from commands import register_command

def take_screenshot(filename: str = "screenshot.png") -> str:
    """
    Take a screenshot and save it to the specified file.
    Args:
        filename: The name of the screenshot file (default: screenshot.png)
    Returns:
        The path to the saved screenshot or an error message
    """
    try:
        os.makedirs(os.path.dirname(filename), exist_ok=True)  # Ensure directory exists
        screenshot = pyautogui.screenshot()
        screenshot.save(filename)
        return f"Screenshot saved to {filename}"
    except Exception as e:
        return f"Error taking screenshot: {str(e)}"

TAKE_SCREENSHOT_SCHEMA = {
    "type": "function",
    "function": {
        "name": "take_screenshot",
        "description": "Take a screenshot and save it to the specified file.",
        "parameters": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "description": "The name of the screenshot file (default: screenshot.png)"
                }
            },
            "required": []
        }
    }
}

register_command("take_screenshot", take_screenshot, TAKE_SCREENSHOT_SCHEMA) 