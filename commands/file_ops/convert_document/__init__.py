"""
Document Converter command for SimpleAgent.

This module provides the convert_document command for converting between various document formats.
"""

import os
import tempfile
import subprocess
from typing import Dict, Any, Optional
from pathlib import Path
from commands import register_command


class DocumentConverter:
    """Manages document format conversions."""
    
    def __init__(self):
        """Initialize the Document Converter."""
        self.supported_formats = {
            'input': ['txt', 'md', 'markdown', 'html', 'htm', 'pdf', 'docx', 'doc', 'rtf', 'odt'],
            'output': ['txt', 'md', 'markdown', 'html', 'htm', 'pdf', 'docx', 'doc', 'rtf', 'odt']
        }
        
        # Check if pandoc is available
        self.pandoc_available = self._check_pandoc()
    
    def _check_pandoc(self) -> bool:
        """Check if pandoc is available on the system."""
        try:
            result = subprocess.run(['pandoc', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
            return False
    
    def convert_with_pandoc(self, input_file: str, output_file: str, 
                           from_format: str, to_format: str) -> Dict[str, Any]:
        """
        Convert document using pandoc.
        
        Args:
            input_file: Path to input file
            output_file: Path to output file
            from_format: Source format
            to_format: Target format
            
        Returns:
            Dictionary containing conversion result
        """
        try:
            # Map formats to pandoc format names
            format_mapping = {
                'md': 'markdown',
                'markdown': 'markdown',
                'txt': 'plain',
                'html': 'html',
                'htm': 'html',
                'pdf': 'pdf',
                'docx': 'docx',
                'doc': 'doc',
                'rtf': 'rtf',
                'odt': 'odt'
            }
            
            pandoc_from = format_mapping.get(from_format.lower(), from_format)
            pandoc_to = format_mapping.get(to_format.lower(), to_format)
            
            # Build pandoc command
            cmd = [
                'pandoc',
                '-f', pandoc_from,
                '-t', pandoc_to,
                '-o', output_file,
                input_file
            ]
            
            # Add specific options for certain formats
            if to_format.lower() == 'pdf':
                cmd.extend(['--pdf-engine=xelatex'])
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "method": "pandoc",
                    "output_file": output_file
                }
            else:
                return {
                    "success": False,
                    "method": "pandoc",
                    "error": f"Pandoc error: {result.stderr}"
                }
                
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "method": "pandoc",
                "error": "Conversion timed out"
            }
        except Exception as e:
            return {
                "success": False,
                "method": "pandoc",
                "error": f"Pandoc conversion failed: {str(e)}"
            }
    
    def convert_text_formats(self, input_file: str, output_file: str,
                           from_format: str, to_format: str) -> Dict[str, Any]:
        """
        Convert between text-based formats using Python libraries.
        
        Args:
            input_file: Path to input file
            output_file: Path to output file
            from_format: Source format
            to_format: Target format
            
        Returns:
            Dictionary containing conversion result
        """
        try:
            # Read input content
            with open(input_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Simple conversions
            if from_format.lower() in ['txt', 'md', 'markdown'] and to_format.lower() in ['txt', 'md', 'markdown']:
                # Text to text conversions
                if to_format.lower() == 'html':
                    # Simple markdown to HTML conversion
                    content = self._markdown_to_html(content)
                elif from_format.lower() == 'html' and to_format.lower() in ['txt', 'md']:
                    # Simple HTML to text conversion
                    content = self._html_to_text(content)
                
                # Write output
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                return {
                    "success": True,
                    "method": "python",
                    "output_file": output_file
                }
            else:
                return {
                    "success": False,
                    "method": "python",
                    "error": f"Conversion from {from_format} to {to_format} not supported without pandoc"
                }
                
        except Exception as e:
            return {
                "success": False,
                "method": "python",
                "error": f"Python conversion failed: {str(e)}"
            }
    
    def _markdown_to_html(self, markdown_text: str) -> str:
        """
        Simple markdown to HTML conversion.
        
        Args:
            markdown_text: Markdown content
            
        Returns:
            HTML content
        """
        import re
        
        html = markdown_text
        
        # Headers
        html = re.sub(r'^### (.*$)', r'<h3>\1</h3>', html, flags=re.M)
        html = re.sub(r'^## (.*$)', r'<h2>\1</h2>', html, flags=re.M)
        html = re.sub(r'^# (.*$)', r'<h1>\1</h1>', html, flags=re.M)
        
        # Bold and italic
        html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
        html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html)
        
        # Links
        html = re.sub(r'\[([^\]]*)\]\(([^)]*)\)', r'<a href="\2">\1</a>', html)
        
        # Code blocks
        html = re.sub(r'```(.*?)```', r'<pre><code>\1</code></pre>', html, flags=re.DOTALL)
        html = re.sub(r'`([^`]*)`', r'<code>\1</code>', html)
        
        # Line breaks
        html = html.replace('\n\n', '</p><p>')
        html = f'<p>{html}</p>'
        html = html.replace('<p></p>', '')
        
        return f'<!DOCTYPE html><html><body>{html}</body></html>'
    
    def _html_to_text(self, html_content: str) -> str:
        """
        Simple HTML to text conversion.
        
        Args:
            html_content: HTML content
            
        Returns:
            Plain text content
        """
        import re
        
        # Remove script and style elements
        text = re.sub(r'<(script|style)[^<]*?</\1>', '', html_content, flags=re.IGNORECASE | re.DOTALL)
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Decode HTML entities
        text = text.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
        text = text.replace('&quot;', '"').replace('&#39;', "'").replace('&nbsp;', ' ')
        
        # Clean up whitespace
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = re.sub(r' +', ' ', text)
        
        return text.strip()
    
    def get_format_from_extension(self, filename: str) -> str:
        """
        Get format from file extension.
        
        Args:
            filename: File name or path
            
        Returns:
            File format
        """
        extension = Path(filename).suffix.lower().lstrip('.')
        if extension in ['md']:
            return 'markdown'
        return extension


def convert_document(
    input_file: str,
    output_file: str,
    from_format: Optional[str] = None,
    to_format: Optional[str] = None
) -> Dict[str, Any]:
    """
    Convert a document from one format to another.
    
    Args:
        input_file: Path to the input file
        output_file: Path to the output file
        from_format: Source format (auto-detected if not specified)
        to_format: Target format (auto-detected if not specified)
        
    Returns:
        Dictionary containing conversion result
    """
    try:
        converter = DocumentConverter()
        
        # Check if input file exists
        if not os.path.exists(input_file):
            return {
                "success": False,
                "error": f"Input file not found: {input_file}"
            }
        
        # Auto-detect formats if not specified
        if not from_format:
            from_format = converter.get_format_from_extension(input_file)
        
        if not to_format:
            to_format = converter.get_format_from_extension(output_file)
        
        # Validate formats
        if from_format.lower() not in converter.supported_formats['input']:
            return {
                "success": False,
                "error": f"Unsupported input format: {from_format}"
            }
        
        if to_format.lower() not in converter.supported_formats['output']:
            return {
                "success": False,
                "error": f"Unsupported output format: {to_format}"
            }
        
        # Create output directory if it doesn't exist
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Try conversion with pandoc first if available
        if converter.pandoc_available:
            result = converter.convert_with_pandoc(input_file, output_file, from_format, to_format)
            if result["success"]:
                return {
                    "success": True,
                    "input_file": input_file,
                    "output_file": output_file,
                    "from_format": from_format,
                    "to_format": to_format,
                    "method": "pandoc",
                    "file_size": os.path.getsize(output_file) if os.path.exists(output_file) else 0
                }
        
        # Fallback to Python-based conversion for simple formats
        result = converter.convert_text_formats(input_file, output_file, from_format, to_format)
        
        if result["success"]:
            return {
                "success": True,
                "input_file": input_file,
                "output_file": output_file,
                "from_format": from_format,
                "to_format": to_format,
                "method": "python",
                "file_size": os.path.getsize(output_file) if os.path.exists(output_file) else 0
            }
        else:
            return result
            
    except Exception as e:
        return {
            "success": False,
            "error": f"Conversion failed: {str(e)}"
        }


# Define the schema for the convert_document command
CONVERT_DOCUMENT_SCHEMA = {
    "type": "function",
    "function": {
        "name": "convert_document",
        "description": "Convert a document from one format to another (supports PDF, Word, Markdown, HTML, TXT, RTF, ODT)",
        "parameters": {
            "type": "object",
            "properties": {
                "input_file": {
                    "type": "string",
                    "description": "Path to the input file to convert"
                },
                "output_file": {
                    "type": "string",
                    "description": "Path where the converted file should be saved"
                },
                "from_format": {
                    "type": "string",
                    "description": "Source format (auto-detected from file extension if not specified)",
                    "enum": ["txt", "md", "markdown", "html", "htm", "pdf", "docx", "doc", "rtf", "odt"]
                },
                "to_format": {
                    "type": "string",
                    "description": "Target format (auto-detected from output file extension if not specified)",
                    "enum": ["txt", "md", "markdown", "html", "htm", "pdf", "docx", "doc", "rtf", "odt"]
                }
            },
            "required": ["input_file", "output_file"]
        }
    }
}

# Register the command
register_command("convert_document", convert_document, CONVERT_DOCUMENT_SCHEMA) 