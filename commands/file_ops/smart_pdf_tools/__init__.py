"""
Smart PDF Tools command for SimpleAgent.

This module provides comprehensive PDF processing capabilities including text extraction, 
metadata extraction, table extraction, image extraction, and text analysis.
"""

import os
import io
import re
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
from commands import register_command


class SmartPDFProcessor:
    """Comprehensive PDF processing with multiple extraction and analysis capabilities."""
    
    def __init__(self):
        """Initialize the Smart PDF Processor."""
        self.available_libraries = self._check_available_libraries()
    
    def _check_available_libraries(self) -> Dict[str, bool]:
        """Check which PDF processing libraries are available."""
        libraries = {}
        
        # Check for PyPDF2/pypdf
        try:
            import PyPDF2
            libraries['PyPDF2'] = True
        except ImportError:
            try:
                import pypdf
                libraries['pypdf'] = True
            except ImportError:
                libraries['PyPDF2'] = False
                libraries['pypdf'] = False
        
        # Check for pdfplumber (better for tables and layout)
        try:
            import pdfplumber
            libraries['pdfplumber'] = True
        except ImportError:
            libraries['pdfplumber'] = False
        
        # Check for fitz (PyMuPDF) for images and advanced features
        try:
            import fitz
            libraries['fitz'] = True
        except ImportError:
            libraries['fitz'] = False
        
        return libraries
    
    def extract_text(self, pdf_path: str, page_range: Optional[tuple] = None) -> Dict[str, Any]:
        """
        Extract text from PDF using the best available method.
        
        Args:
            pdf_path: Path to PDF file
            page_range: Optional tuple (start_page, end_page) for page range
            
        Returns:
            Dictionary containing extracted text and metadata
        """
        try:
            if not os.path.exists(pdf_path):
                return {
                    "success": False,
                    "error": f"PDF file not found: {pdf_path}"
                }
            
            # Try pdfplumber first (best for text extraction)
            if self.available_libraries.get('pdfplumber'):
                return self._extract_text_pdfplumber(pdf_path, page_range)
            
            # Fall back to PyPDF2/pypdf
            elif self.available_libraries.get('PyPDF2') or self.available_libraries.get('pypdf'):
                return self._extract_text_pypdf(pdf_path, page_range)
            
            # Fall back to PyMuPDF
            elif self.available_libraries.get('fitz'):
                return self._extract_text_fitz(pdf_path, page_range)
            
            else:
                return {
                    "success": False,
                    "error": "No PDF processing libraries available. Install PyPDF2, pdfplumber, or PyMuPDF"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Text extraction failed: {str(e)}"
            }
    
    def _extract_text_pdfplumber(self, pdf_path: str, page_range: Optional[tuple] = None) -> Dict[str, Any]:
        """Extract text using pdfplumber."""
        import pdfplumber
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                pages_text = []
                total_pages = len(pdf.pages)
                
                # Determine page range
                if page_range:
                    start_page, end_page = page_range
                    start_page = max(0, start_page - 1)  # Convert to 0-based
                    end_page = min(total_pages, end_page)
                else:
                    start_page, end_page = 0, total_pages
                
                # Extract text from each page
                for i in range(start_page, end_page):
                    page = pdf.pages[i]
                    text = page.extract_text() or ""
                    pages_text.append({
                        'page_number': i + 1,
                        'text': text,
                        'word_count': len(text.split()) if text else 0
                    })
                
                # Combine all text
                full_text = "\n\n".join([page['text'] for page in pages_text if page['text']])
                
                return {
                    "success": True,
                    "method": "pdfplumber",
                    "full_text": full_text,
                    "pages": pages_text,
                    "total_pages": total_pages,
                    "processed_pages": len(pages_text),
                    "total_words": sum([page['word_count'] for page in pages_text]),
                    "total_characters": len(full_text)
                }
                
        except Exception as e:
            return {
                "success": False,
                "method": "pdfplumber",
                "error": f"pdfplumber extraction failed: {str(e)}"
            }
    
    def _extract_text_pypdf(self, pdf_path: str, page_range: Optional[tuple] = None) -> Dict[str, Any]:
        """Extract text using PyPDF2 or pypdf."""
        try:
            try:
                import PyPDF2 as pdf_lib
                reader_class = pdf_lib.PdfReader
            except ImportError:
                import pypdf as pdf_lib
                reader_class = pdf_lib.PdfReader
            
            with open(pdf_path, 'rb') as file:
                reader = reader_class(file)
                pages_text = []
                total_pages = len(reader.pages)
                
                # Determine page range
                if page_range:
                    start_page, end_page = page_range
                    start_page = max(0, start_page - 1)
                    end_page = min(total_pages, end_page)
                else:
                    start_page, end_page = 0, total_pages
                
                # Extract text from each page
                for i in range(start_page, end_page):
                    page = reader.pages[i]
                    text = page.extract_text()
                    pages_text.append({
                        'page_number': i + 1,
                        'text': text,
                        'word_count': len(text.split()) if text else 0
                    })
                
                # Combine all text
                full_text = "\n\n".join([page['text'] for page in pages_text if page['text']])
                
                return {
                    "success": True,
                    "method": "PyPDF2/pypdf",
                    "full_text": full_text,
                    "pages": pages_text,
                    "total_pages": total_pages,
                    "processed_pages": len(pages_text),
                    "total_words": sum([page['word_count'] for page in pages_text]),
                    "total_characters": len(full_text)
                }
                
        except Exception as e:
            return {
                "success": False,
                "method": "PyPDF2/pypdf",
                "error": f"PyPDF2/pypdf extraction failed: {str(e)}"
            }
    
    def _extract_text_fitz(self, pdf_path: str, page_range: Optional[tuple] = None) -> Dict[str, Any]:
        """Extract text using PyMuPDF (fitz)."""
        import fitz
        
        try:
            doc = fitz.open(pdf_path)
            pages_text = []
            total_pages = len(doc)
            
            # Determine page range
            if page_range:
                start_page, end_page = page_range
                start_page = max(0, start_page - 1)
                end_page = min(total_pages, end_page)
            else:
                start_page, end_page = 0, total_pages
            
            # Extract text from each page
            for i in range(start_page, end_page):
                page = doc[i]
                text = page.get_text()
                pages_text.append({
                    'page_number': i + 1,
                    'text': text,
                    'word_count': len(text.split()) if text else 0
                })
            
            doc.close()
            
            # Combine all text
            full_text = "\n\n".join([page['text'] for page in pages_text if page['text']])
            
            return {
                "success": True,
                "method": "PyMuPDF",
                "full_text": full_text,
                "pages": pages_text,
                "total_pages": total_pages,
                "processed_pages": len(pages_text),
                "total_words": sum([page['word_count'] for page in pages_text]),
                "total_characters": len(full_text)
            }
            
        except Exception as e:
            return {
                "success": False,
                "method": "PyMuPDF",
                "error": f"PyMuPDF extraction failed: {str(e)}"
            }
    
    def extract_metadata(self, pdf_path: str) -> Dict[str, Any]:
        """
        Extract metadata from PDF.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dictionary containing PDF metadata
        """
        try:
            if not os.path.exists(pdf_path):
                return {
                    "success": False,
                    "error": f"PDF file not found: {pdf_path}"
                }
            
            # Try PyPDF2/pypdf first for metadata
            if self.available_libraries.get('PyPDF2') or self.available_libraries.get('pypdf'):
                try:
                    try:
                        import PyPDF2 as pdf_lib
                        reader_class = pdf_lib.PdfReader
                    except ImportError:
                        import pypdf as pdf_lib
                        reader_class = pdf_lib.PdfReader
                    
                    with open(pdf_path, 'rb') as file:
                        reader = reader_class(file)
                        metadata = reader.metadata or {}
                        
                        return {
                            "success": True,
                            "method": "PyPDF2/pypdf",
                            "metadata": {
                                "title": metadata.get('/Title', ''),
                                "author": metadata.get('/Author', ''),
                                "subject": metadata.get('/Subject', ''),
                                "creator": metadata.get('/Creator', ''),
                                "producer": metadata.get('/Producer', ''),
                                "creation_date": str(metadata.get('/CreationDate', '')),
                                "modification_date": str(metadata.get('/ModDate', '')),
                                "total_pages": len(reader.pages)
                            },
                            "file_size": os.path.getsize(pdf_path)
                        }
                        
                except Exception as e:
                    pass
            
            # Try PyMuPDF as fallback
            if self.available_libraries.get('fitz'):
                import fitz
                
                doc = fitz.open(pdf_path)
                metadata = doc.metadata
                doc.close()
                
                return {
                    "success": True,
                    "method": "PyMuPDF",
                    "metadata": metadata,
                    "file_size": os.path.getsize(pdf_path)
                }
            
            return {
                "success": False,
                "error": "No suitable PDF library available for metadata extraction"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Metadata extraction failed: {str(e)}"
            }
    
    def extract_tables(self, pdf_path: str, page_number: Optional[int] = None) -> Dict[str, Any]:
        """
        Extract tables from PDF.
        
        Args:
            pdf_path: Path to PDF file
            page_number: Specific page number (1-based), or None for all pages
            
        Returns:
            Dictionary containing extracted tables
        """
        try:
            if not self.available_libraries.get('pdfplumber'):
                return {
                    "success": False,
                    "error": "pdfplumber library required for table extraction. Install with: pip install pdfplumber"
                }
            
            import pdfplumber
            
            with pdfplumber.open(pdf_path) as pdf:
                all_tables = []
                
                if page_number:
                    # Extract from specific page
                    if 1 <= page_number <= len(pdf.pages):
                        page = pdf.pages[page_number - 1]
                        tables = page.extract_tables()
                        if tables:
                            for i, table in enumerate(tables):
                                all_tables.append({
                                    'page': page_number,
                                    'table_index': i + 1,
                                    'rows': len(table),
                                    'columns': len(table[0]) if table else 0,
                                    'data': table
                                })
                    else:
                        return {
                            "success": False,
                            "error": f"Page {page_number} not found. PDF has {len(pdf.pages)} pages."
                        }
                else:
                    # Extract from all pages
                    for page_num, page in enumerate(pdf.pages, 1):
                        tables = page.extract_tables()
                        if tables:
                            for i, table in enumerate(tables):
                                all_tables.append({
                                    'page': page_num,
                                    'table_index': i + 1,
                                    'rows': len(table),
                                    'columns': len(table[0]) if table else 0,
                                    'data': table
                                })
                
                return {
                    "success": True,
                    "method": "pdfplumber",
                    "tables_found": len(all_tables),
                    "tables": all_tables
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Table extraction failed: {str(e)}"
            }
    
    def search_text(self, pdf_path: str, search_term: str, case_sensitive: bool = False) -> Dict[str, Any]:
        """
        Search for specific text in PDF.
        
        Args:
            pdf_path: Path to PDF file
            search_term: Text to search for
            case_sensitive: Whether search should be case sensitive
            
        Returns:
            Dictionary containing search results
        """
        try:
            # First extract all text
            text_result = self.extract_text(pdf_path)
            
            if not text_result["success"]:
                return text_result
            
            search_flags = 0 if case_sensitive else re.IGNORECASE
            matches = []
            
            # Search in each page
            for page_data in text_result["pages"]:
                page_text = page_data["text"]
                if not page_text:
                    continue
                
                # Find all matches in this page
                for match in re.finditer(re.escape(search_term), page_text, search_flags):
                    start_pos = match.start()
                    end_pos = match.end()
                    
                    # Get context around the match
                    context_start = max(0, start_pos - 100)
                    context_end = min(len(page_text), end_pos + 100)
                    context = page_text[context_start:context_end]
                    
                    matches.append({
                        'page': page_data['page_number'],
                        'position': start_pos,
                        'matched_text': match.group(),
                        'context': context.strip()
                    })
            
            return {
                "success": True,
                "search_term": search_term,
                "case_sensitive": case_sensitive,
                "total_matches": len(matches),
                "matches": matches
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Text search failed: {str(e)}"
            }
    
    def analyze_text(self, text: str) -> Dict[str, Any]:
        """
        Analyze extracted text for various metrics.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary containing text analysis
        """
        try:
            if not text:
                return {
                    "word_count": 0,
                    "character_count": 0,
                    "paragraph_count": 0,
                    "sentence_count": 0,
                    "average_words_per_sentence": 0
                }
            
            # Basic counts
            words = text.split()
            word_count = len(words)
            char_count = len(text)
            
            # Count paragraphs (double newlines)
            paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
            paragraph_count = len(paragraphs)
            
            # Count sentences (rough estimation)
            sentences = re.split(r'[.!?]+', text)
            sentences = [s.strip() for s in sentences if s.strip()]
            sentence_count = len(sentences)
            
            # Calculate averages
            avg_words_per_sentence = word_count / sentence_count if sentence_count > 0 else 0
            
            # Find most common words (simple analysis)
            word_freq = {}
            for word in words:
                word_clean = re.sub(r'[^\w]', '', word.lower())
                if len(word_clean) > 3:  # Only count words longer than 3 chars
                    word_freq[word_clean] = word_freq.get(word_clean, 0) + 1
            
            # Get top 10 most common words
            top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
            
            return {
                "word_count": word_count,
                "character_count": char_count,
                "paragraph_count": paragraph_count,
                "sentence_count": sentence_count,
                "average_words_per_sentence": round(avg_words_per_sentence, 2),
                "top_words": top_words
            }
            
        except Exception as e:
            return {
                "error": f"Text analysis failed: {str(e)}"
            }


def smart_pdf_tools(
    pdf_path: str,
    action: str = "extract_text",
    page_range: Optional[str] = None,
    page_number: Optional[int] = None,
    search_term: Optional[str] = None,
    case_sensitive: bool = False
) -> Dict[str, Any]:
    """
    Comprehensive PDF processing tool with multiple capabilities.
    
    Args:
        pdf_path: Path to the PDF file
        action: Action to perform (extract_text, extract_metadata, extract_tables, search_text, analyze)
        page_range: Page range for text extraction (e.g., "1-5" or "3-10")
        page_number: Specific page number for table extraction
        search_term: Text to search for (required for search_text action)
        case_sensitive: Whether search should be case sensitive
        
    Returns:
        Dictionary containing the results of the specified action
    """
    try:
        if not os.path.exists(pdf_path):
            return {
                "success": False,
                "error": f"PDF file not found: {pdf_path}"
            }
        
        processor = SmartPDFProcessor()
        
        # Parse page range if provided
        parsed_page_range = None
        if page_range:
            try:
                if '-' in page_range:
                    start, end = page_range.split('-')
                    parsed_page_range = (int(start), int(end))
                else:
                    page_num = int(page_range)
                    parsed_page_range = (page_num, page_num)
            except ValueError:
                return {
                    "success": False,
                    "error": f"Invalid page range format: {page_range}. Use format like '1-5' or '3'"
                }
        
        # Execute the requested action
        if action == "extract_text":
            result = processor.extract_text(pdf_path, parsed_page_range)
            if result["success"] and "full_text" in result:
                # Add text analysis
                result["text_analysis"] = processor.analyze_text(result["full_text"])
            return result
            
        elif action == "extract_metadata":
            return processor.extract_metadata(pdf_path)
            
        elif action == "extract_tables":
            return processor.extract_tables(pdf_path, page_number)
            
        elif action == "search_text":
            if not search_term:
                return {
                    "success": False,
                    "error": "search_term is required for search_text action"
                }
            return processor.search_text(pdf_path, search_term, case_sensitive)
            
        elif action == "analyze":
            # Extract text first, then analyze
            text_result = processor.extract_text(pdf_path, parsed_page_range)
            if not text_result["success"]:
                return text_result
            
            analysis = processor.analyze_text(text_result["full_text"])
            return {
                "success": True,
                "action": "analyze",
                "file_path": pdf_path,
                "text_analysis": analysis,
                "extraction_info": {
                    "total_pages": text_result.get("total_pages", 0),
                    "processed_pages": text_result.get("processed_pages", 0),
                    "method": text_result.get("method", "unknown")
                }
            }
            
        else:
            return {
                "success": False,
                "error": f"Unknown action: {action}. Use: extract_text, extract_metadata, extract_tables, search_text, or analyze"
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": f"PDF processing failed: {str(e)}"
        }


# Define the schema for the smart_pdf_tools command
SMART_PDF_TOOLS_SCHEMA = {
    "type": "function",
    "function": {
        "name": "smart_pdf_tools",
        "description": "Comprehensive PDF processing tool for extracting text, metadata, tables, searching content, and analyzing documents",
        "parameters": {
            "type": "object",
            "properties": {
                "pdf_path": {
                    "type": "string",
                    "description": "Path to the PDF file to process"
                },
                "action": {
                    "type": "string",
                    "description": "Action to perform on the PDF",
                    "enum": ["extract_text", "extract_metadata", "extract_tables", "search_text", "analyze"],
                    "default": "extract_text"
                },
                "page_range": {
                    "type": "string",
                    "description": "Page range for text extraction (e.g., '1-5', '3-10', or '7' for single page)"
                },
                "page_number": {
                    "type": "integer",
                    "description": "Specific page number for table extraction (1-based)"
                },
                "search_term": {
                    "type": "string",
                    "description": "Text to search for (required for search_text action)"
                },
                "case_sensitive": {
                    "type": "boolean",
                    "description": "Whether text search should be case sensitive",
                    "default": False
                }
            },
            "required": ["pdf_path"]
        }
    }
}

# Register the command
register_command("smart_pdf_tools", smart_pdf_tools, SMART_PDF_TOOLS_SCHEMA) 