"""
Analyze Image with GPT-4 Vision command for SimpleAgent.

This module provides the analyze_image_with_gpt4 command for sending an image to GPT-4 Vision and returning the reply.
"""

import os
from commands import register_command
from core.config import create_client, API_PROVIDER
import base64

# Use the vision-capable model (gpt-4o or gpt-4-vision-preview)
VISION_MODEL = "gpt-4o"

def analyze_image_with_gpt4(image_path: str, prompt: str) -> str:
    """
    Send an image to GPT-4 Vision with a prompt and return the reply.
    Args:
        image_path: Path to the image file
        prompt: The prompt/question for GPT-4 Vision
    Returns:
        The model's reply or an error message
    """
    try:
        # Check if we're using LM-Studio - vision capabilities may not be available
        if API_PROVIDER == "lmstudio":
            return "Image analysis is not supported with LM-Studio provider. This feature requires OpenAI's vision-capable models."
        
        if not os.path.exists(image_path):
            return f"Image file not found: {image_path}"
        with open(image_path, "rb") as img_file:
            img_bytes = img_file.read()
            img_b64 = base64.b64encode(img_bytes).decode("utf-8")
            client = create_client()
            response = client.chat.completions.create(
                model=VISION_MODEL,
                messages=[
                    {"role": "user", "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_b64}"}}
                    ]}
                ]
            )
            if response.choices and response.choices[0].message and response.choices[0].message.content:
                return response.choices[0].message.content
            return "No reply from GPT-4 Vision."
    except Exception as e:
        return f"Error analyzing image: {str(e)}"

ANALYZE_IMAGE_WITH_GPT4_SCHEMA = {
    "type": "function",
    "function": {
        "name": "analyze_image_with_gpt4",
        "description": "Send an image to GPT-4 Vision with a prompt and return the reply.",
        "parameters": {
            "type": "object",
            "properties": {
                "image_path": {
                    "type": "string",
                    "description": "Path to the image file"
                },
                "prompt": {
                    "type": "string",
                    "description": "The prompt/question for GPT-4 Vision"
                }
            },
            "required": ["image_path", "prompt"]
        }
    }
}

register_command("analyze_image_with_gpt4", analyze_image_with_gpt4, ANALYZE_IMAGE_WITH_GPT4_SCHEMA) 