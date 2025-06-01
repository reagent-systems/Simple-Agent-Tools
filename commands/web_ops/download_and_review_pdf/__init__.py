"""
Download and Review PDF command for SimpleAgent.

This module provides the download_and_review_pdf command for downloading PDFs from URLs 
and automatically analyzing them with comprehensive review capabilities.
"""

import os
import tempfile
import requests
from typing import Dict, Any, Optional
from urllib.parse import urlparse, unquote
from pathlib import Path
from commands import register_command


class PDFDownloadReviewer:
    """Manages downloading and reviewing PDFs from URLs."""
    
    def __init__(self):
        """Initialize the PDF Download Reviewer."""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        # Import smart_pdf_tools functionality
        try:
            from commands.file_ops.smart_pdf_tools import smart_pdf_tools
            self.smart_pdf_tools = smart_pdf_tools
            self.pdf_tools_available = True
        except ImportError:
            self.pdf_tools_available = False
    
    def download_pdf(self, url: str, save_path: Optional[str] = None, timeout: int = 60) -> Dict[str, Any]:
        """
        Download PDF from URL.
        
        Args:
            url: URL to download PDF from
            save_path: Optional path to save the PDF (if None, saves to temp file)
            timeout: Request timeout in seconds
            
        Returns:
            Dictionary containing download result and file path
        """
        try:
            # Validate URL
            parsed_url = urlparse(url)
            if not parsed_url.scheme or not parsed_url.netloc:
                return {
                    "success": False,
                    "error": "Invalid URL format"
                }
            
            # Make request with streaming to handle large files
            response = self.session.get(url, stream=True, timeout=timeout)
            response.raise_for_status()
            
            # Check if response is actually a PDF
            content_type = response.headers.get('content-type', '').lower()
            if 'application/pdf' not in content_type and not url.lower().endswith('.pdf'):
                # Try to detect PDF by reading first few bytes
                first_chunk = next(response.iter_content(chunk_size=8192), b'')
                if not first_chunk.startswith(b'%PDF'):
                    return {
                        "success": False,
                        "error": f"URL does not appear to contain a PDF file. Content-Type: {content_type}"
                    }
                # Reset response by making a new request
                response = self.session.get(url, stream=True, timeout=timeout)
                response.raise_for_status()
            
            # Determine save path
            if not save_path:
                # Create temporary file
                temp_dir = tempfile.gettempdir()
                filename = self._extract_filename_from_url(url)
                save_path = os.path.join(temp_dir, filename)
            else:
                # Ensure directory exists
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            # Download the file
            file_size = 0
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        file_size += len(chunk)
            
            return {
                "success": True,
                "file_path": save_path,
                "file_size": file_size,
                "url": url,
                "content_type": content_type
            }
            
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "error": f"Download timed out after {timeout} seconds"
            }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"Download failed: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error during download: {str(e)}"
            }
    
    def _extract_filename_from_url(self, url: str) -> str:
        """
        Extract filename from URL or generate one.
        
        Args:
            url: URL to extract filename from
            
        Returns:
            Filename for the PDF
        """
        try:
            # Try to get filename from URL path
            parsed_url = urlparse(url)
            path = unquote(parsed_url.path)
            filename = os.path.basename(path)
            
            # If no filename or no .pdf extension, generate one
            if not filename or not filename.lower().endswith('.pdf'):
                # Use domain and generate a name
                domain = parsed_url.netloc.replace('www.', '')
                filename = f"downloaded_pdf_{domain}.pdf"
                # Clean up filename
                filename = "".join(c for c in filename if c.isalnum() or c in ('_', '-', '.')).strip()
            
            return filename
            
        except Exception:
            return "downloaded_pdf.pdf"
    
    def review_pdf(self, pdf_path: str, review_type: str = "comprehensive") -> Dict[str, Any]:
        """
        Review PDF using smart_pdf_tools.
        
        Args:
            pdf_path: Path to PDF file
            review_type: Type of review (quick, comprehensive, metadata_only, tables_only)
            
        Returns:
            Dictionary containing review results
        """
        if not self.pdf_tools_available:
            return {
                "success": False,
                "error": "smart_pdf_tools not available for PDF review"
            }
        
        try:
            review_results = {}
            
            if review_type == "metadata_only":
                # Only extract metadata
                review_results["metadata"] = self.smart_pdf_tools(pdf_path, action="extract_metadata")
                
            elif review_type == "tables_only":
                # Only extract tables
                review_results["tables"] = self.smart_pdf_tools(pdf_path, action="extract_tables")
                
            elif review_type == "quick":
                # Quick review: metadata + first 3 pages text + analysis
                review_results["metadata"] = self.smart_pdf_tools(pdf_path, action="extract_metadata")
                review_results["text_preview"] = self.smart_pdf_tools(pdf_path, action="extract_text", page_range="1-3")
                
            else:  # comprehensive
                # Full review: everything
                review_results["metadata"] = self.smart_pdf_tools(pdf_path, action="extract_metadata")
                review_results["full_text"] = self.smart_pdf_tools(pdf_path, action="extract_text")
                review_results["tables"] = self.smart_pdf_tools(pdf_path, action="extract_tables")
                review_results["analysis"] = self.smart_pdf_tools(pdf_path, action="analyze")
            
            return {
                "success": True,
                "review_type": review_type,
                "review_results": review_results
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"PDF review failed: {str(e)}"
            }
    
    def generate_summary(self, review_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a summary from review results.
        
        Args:
            review_results: Results from PDF review
            
        Returns:
            Dictionary containing summary information
        """
        try:
            summary = {
                "document_info": {},
                "content_summary": {},
                "key_findings": []
            }
            
            # Extract document info from metadata
            if "metadata" in review_results and review_results["metadata"].get("success"):
                metadata = review_results["metadata"].get("metadata", {})
                summary["document_info"] = {
                    "title": metadata.get("title", "Unknown"),
                    "author": metadata.get("author", "Unknown"),
                    "total_pages": metadata.get("total_pages", 0),
                    "file_size": review_results["metadata"].get("file_size", 0),
                    "creation_date": metadata.get("creation_date", "Unknown")
                }
            
            # Extract content summary from text analysis
            if "analysis" in review_results and review_results["analysis"].get("success"):
                text_analysis = review_results["analysis"].get("text_analysis", {})
                summary["content_summary"] = {
                    "word_count": text_analysis.get("word_count", 0),
                    "paragraph_count": text_analysis.get("paragraph_count", 0),
                    "sentence_count": text_analysis.get("sentence_count", 0),
                    "top_words": text_analysis.get("top_words", [])[:5]  # Top 5 words
                }
            elif "text_preview" in review_results and review_results["text_preview"].get("success"):
                text_analysis = review_results["text_preview"].get("text_analysis", {})
                summary["content_summary"] = {
                    "word_count_preview": text_analysis.get("word_count", 0),
                    "note": "Based on first 3 pages only"
                }
            
            # Extract table information
            if "tables" in review_results and review_results["tables"].get("success"):
                tables_count = review_results["tables"].get("tables_found", 0)
                if tables_count > 0:
                    summary["key_findings"].append(f"Contains {tables_count} table(s)")
            
            # Extract text preview for key findings
            if "full_text" in review_results and review_results["full_text"].get("success"):
                full_text = review_results["full_text"].get("full_text", "")
                if full_text:
                    # Get first 500 characters as preview
                    preview = full_text[:500].strip()
                    if len(full_text) > 500:
                        preview += "..."
                    summary["text_preview"] = preview
            elif "text_preview" in review_results and review_results["text_preview"].get("success"):
                preview_text = review_results["text_preview"].get("full_text", "")
                if preview_text:
                    preview = preview_text[:500].strip()
                    if len(preview_text) > 500:
                        preview += "..."
                    summary["text_preview"] = preview
            
            return {
                "success": True,
                "summary": summary
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Summary generation failed: {str(e)}"
            }


def download_and_review_pdf(
    url: str,
    save_path: Optional[str] = None,
    review_type: str = "comprehensive",
    include_summary: bool = True,
    timeout: int = 60,
    cleanup_temp: bool = True
) -> Dict[str, Any]:
    """
    Download a PDF from URL and automatically review/analyze it.
    
    Args:
        url: URL to download PDF from
        save_path: Optional path to save the PDF (if None, uses temporary file)
        review_type: Type of review (quick, comprehensive, metadata_only, tables_only)
        include_summary: Whether to generate a summary of the PDF
        timeout: Download timeout in seconds
        cleanup_temp: Whether to cleanup temporary files (only if save_path is None)
        
    Returns:
        Dictionary containing download results, review results, and optional summary
    """
    try:
        reviewer = PDFDownloadReviewer()
        
        # Download the PDF
        download_result = reviewer.download_pdf(url, save_path, timeout)
        
        if not download_result["success"]:
            return download_result
        
        pdf_path = download_result["file_path"]
        is_temp_file = save_path is None
        
        try:
            # Review the PDF
            review_result = reviewer.review_pdf(pdf_path, review_type)
            
            # Generate summary if requested
            summary_result = {}
            if include_summary and review_result.get("success"):
                summary_result = reviewer.generate_summary(review_result.get("review_results", {}))
            
            # Prepare final result
            result = {
                "success": True,
                "url": url,
                "download_info": {
                    "file_path": pdf_path,
                    "file_size": download_result["file_size"],
                    "content_type": download_result["content_type"],
                    "is_temporary": is_temp_file
                },
                "review_type": review_type,
                "review_results": review_result,
            }
            
            if include_summary and summary_result.get("success"):
                result["summary"] = summary_result["summary"]
            
            return result
            
        finally:
            # Cleanup temporary file if requested
            if is_temp_file and cleanup_temp and os.path.exists(pdf_path):
                try:
                    os.remove(pdf_path)
                    if "download_info" in locals():
                        result["download_info"]["cleaned_up"] = True
                except Exception:
                    pass
            
    except Exception as e:
        return {
            "success": False,
            "error": f"Download and review failed: {str(e)}"
        }


# Define the schema for the download_and_review_pdf command
DOWNLOAD_AND_REVIEW_PDF_SCHEMA = {
    "type": "function",
    "function": {
        "name": "download_and_review_pdf",
        "description": "Download a PDF from a URL and automatically analyze it with comprehensive review capabilities",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "URL to download the PDF from"
                },
                "save_path": {
                    "type": "string",
                    "description": "Optional path to save the PDF file (uses temporary file if not specified)"
                },
                "review_type": {
                    "type": "string",
                    "description": "Type of review to perform on the PDF",
                    "enum": ["quick", "comprehensive", "metadata_only", "tables_only"],
                    "default": "comprehensive"
                },
                "include_summary": {
                    "type": "boolean",
                    "description": "Whether to generate a summary of the PDF content",
                    "default": True
                },
                "timeout": {
                    "type": "integer",
                    "description": "Download timeout in seconds",
                    "default": 60,
                    "minimum": 10,
                    "maximum": 300
                },
                "cleanup_temp": {
                    "type": "boolean",
                    "description": "Whether to cleanup temporary files after processing",
                    "default": True
                }
            },
            "required": ["url"]
        }
    }
}

# Register the command
register_command("download_and_review_pdf", download_and_review_pdf, DOWNLOAD_AND_REVIEW_PDF_SCHEMA) 