"""
HTML generation and PDF conversion pipeline.
Handles the conversion from HTML to PDF with proper formatting.
"""

import os
import logging
from typing import Optional
from pathlib import Path
import tempfile
import webbrowser

logger = logging.getLogger(__name__)


class PDFGenerator:
    """Handles HTML to PDF conversion using multiple methods"""
    
    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def html_to_pdf(self, html_content: str, output_filename: str, 
                   margins: str = "0", method: str = "auto") -> str:
        """
        Convert HTML content to PDF
        
        Args:
            html_content: HTML content as string
            output_filename: Name of output PDF file
            margins: PDF margins (e.g., "0" for no margins)
            method: Conversion method ("auto", "weasyprint", "pdfkit", "playwright")
        
        Returns:
            Path to generated PDF file
        """
        output_path = self.output_dir / output_filename
        
        if method == "auto":
            method = self._detect_best_method()
        
        if method == "weasyprint":
            return self._convert_with_weasyprint(html_content, output_path, margins)
        elif method == "pdfkit":
            return self._convert_with_pdfkit(html_content, output_path, margins)
        elif method == "playwright":
            return self._convert_with_playwright(html_content, output_path, margins)
        else:
            raise ValueError(f"Unsupported conversion method: {method}")
    
    def _detect_best_method(self) -> str:
        """Detect the best available PDF conversion method"""
        try:
            import weasyprint
            return "weasyprint"
        except ImportError:
            pass
        
        try:
            import pdfkit
            return "pdfkit"
        except ImportError:
            pass
        
        try:
            import playwright
            return "playwright"
        except ImportError:
            pass
        
        # Fallback to weasyprint (will show installation instructions)
        return "weasyprint"
    
    def _convert_with_weasyprint(self, html_content: str, output_path: Path, margins: str) -> str:
        """Convert HTML to PDF using WeasyPrint"""
        try:
            import weasyprint
            from weasyprint import HTML, CSS
            from weasyprint.text.fonts import FontConfiguration
            
            # Create CSS for print optimization
            css_content = f"""
            @page {{
                margin: {margins};
                size: A4;
            }}
            
            body {{
                font-family: Arial, sans-serif;
                font-size: 12px;
                line-height: 1.4;
                color: #333;
            }}
            
            .container {{
                max-width: 100%;
                padding: 0;
            }}
            
            @media print {{
                body {{
                    font-size: 11px;
                }}
                
                .section {{
                    page-break-inside: avoid;
                }}
                
                .experience-item, .education-item {{
                    page-break-inside: avoid;
                }}
            }}
            """
            
            # Generate PDF
            html_doc = HTML(string=html_content)
            css_doc = CSS(string=css_content)
            
            html_doc.write_pdf(str(output_path), stylesheets=[css_doc])
            
            logger.info(f"PDF generated successfully with WeasyPrint: {output_path}")
            return str(output_path)
            
        except ImportError:
            logger.error("WeasyPrint not installed. Install with: pip install weasyprint")
            raise
        except Exception as e:
            logger.error(f"WeasyPrint conversion error: {e}")
            raise
    
    def _convert_with_pdfkit(self, html_content: str, output_path: Path, margins: str) -> str:
        """Convert HTML to PDF using pdfkit (wkhtmltopdf)"""
        try:
            import pdfkit
            
            options = {
                'page-size': 'A4',
                'margin-top': margins,
                'margin-right': margins,
                'margin-bottom': margins,
                'margin-left': margins,
                'encoding': "UTF-8",
                'no-outline': None,
                'enable-local-file-access': None,
                'print-media-type': None,
                'disable-smart-shrinking': None,
            }
            
            pdfkit.from_string(html_content, str(output_path), options=options)
            
            logger.info(f"PDF generated successfully with pdfkit: {output_path}")
            return str(output_path)
            
        except ImportError:
            logger.error("pdfkit not installed. Install with: pip install pdfkit")
            raise
        except Exception as e:
            logger.error(f"pdfkit conversion error: {e}")
            raise
    
    def _convert_with_playwright(self, html_content: str, output_path: Path, margins: str) -> str:
        """Convert HTML to PDF using Playwright"""
        try:
            from playwright.sync_api import sync_playwright
            
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page()
                
                # Set content
                page.set_content(html_content)
                
                # Generate PDF
                page.pdf(
                    path=str(output_path),
                    format='A4',
                    margin={
                        'top': margins,
                        'right': margins,
                        'bottom': margins,
                        'left': margins
                    },
                    print_background=True,
                    prefer_css_page_size=True
                )
                
                browser.close()
            
            logger.info(f"PDF generated successfully with Playwright: {output_path}")
            return str(output_path)
            
        except ImportError:
            logger.error("Playwright not installed. Install with: pip install playwright")
            raise
        except Exception as e:
            logger.error(f"Playwright conversion error: {e}")
            raise


class HTMLProcessor:
    """Processes and optimizes HTML content for PDF conversion"""
    
    def __init__(self, config):
        self.config = config
    
    def optimize_for_pdf(self, html_content: str) -> str:
        """Optimize HTML content for PDF conversion"""
        
        # Add print-specific CSS
        print_css = f"""
        <style>
            @media print {{
                * {{
                    -webkit-print-color-adjust: exact !important;
                    color-adjust: exact !important;
                }}
                
                body {{
                    font-family: {self.config.resume.font_family};
                    font-size: {self.config.resume.font_size};
                    line-height: {self.config.resume.line_height};
                }}
                
                .container {{
                    max-width: 100%;
                    padding: 0;
                }}
                
                .section {{
                    page-break-inside: avoid;
                    margin-bottom: 15px;
                }}
                
                .experience-item, .education-item, .project-item {{
                    page-break-inside: avoid;
                    margin-bottom: 12px;
                }}
                
                .header {{
                    page-break-after: avoid;
                }}
                
                .skills-grid {{
                    page-break-inside: avoid;
                }}
            }}
        </style>
        """
        
        # Insert CSS before closing head tag
        if '</head>' in html_content:
            html_content = html_content.replace('</head>', print_css + '</head>')
        else:
            html_content = print_css + html_content
        
        return html_content
    
    def validate_html(self, html_content: str) -> bool:
        """Validate HTML content"""
        try:
            # Basic HTML validation
            if not html_content.strip():
                return False
            
            if '<html' not in html_content.lower():
                return False
            
            if '<body' not in html_content.lower():
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"HTML validation error: {e}")
            return False


class FileManager:
    """Manages file operations for the pipeline"""
    
    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def save_html(self, html_content: str, filename: str) -> str:
        """Save HTML content to file"""
        html_path = self.output_dir / filename
        html_path.write_text(html_content, encoding='utf-8')
        logger.info(f"HTML saved to: {html_path}")
        return str(html_path)
    
    def cleanup_temp_files(self, *file_paths):
        """Clean up temporary files"""
        for file_path in file_paths:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.debug(f"Cleaned up temp file: {file_path}")
            except Exception as e:
                logger.warning(f"Failed to cleanup {file_path}: {e}")
    
    def get_unique_filename(self, base_name: str, extension: str) -> str:
        """Generate unique filename to avoid conflicts"""
        counter = 1
        while True:
            filename = f"{base_name}_{counter}.{extension}" if counter > 1 else f"{base_name}.{extension}"
            if not (self.output_dir / filename).exists():
                return filename
            counter += 1


def create_pdf_pipeline(config) -> tuple[PDFGenerator, HTMLProcessor, FileManager]:
    """Factory function to create PDF pipeline components"""
    pdf_generator = PDFGenerator(config.resume.output_dir)
    html_processor = HTMLProcessor(config)
    file_manager = FileManager(config.resume.output_dir)
    
    return pdf_generator, html_processor, file_manager
