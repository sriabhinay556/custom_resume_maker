#!/usr/bin/env python3
"""
Resume Automation Pipeline with Flask Web Interface.
Takes HTML resume file and job description, outputs tailored PDF resume.
Can be used via command line or web interface.
"""

import os
import sys
import logging
import argparse
from pathlib import Path
from typing import Optional
from datetime import datetime
import tempfile
import json

# Import our modules
from config import load_config, validate_config, PipelineConfig
from llm_client import create_llm_manager
from pdf_generator import PDFGenerator

# Flask imports
try:
    from flask import Flask, request, jsonify, send_file, render_template_string
    from werkzeug.utils import secure_filename
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    print("Flask not installed. Install with: pip install flask")


# Set up logging
def setup_logging(debug: bool = False):
    """Set up logging configuration"""
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('resume_pipeline.log')
        ]
    )


class ResumePipeline:
    """Simplified resume tailoring pipeline"""
    
    def __init__(self, config: PipelineConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.llm_manager = create_llm_manager(config.llm)
        self.pdf_generator = PDFGenerator(config.resume.output_dir)
        
        self.logger.info(f"Pipeline initialized with {config.llm.provider.value} provider")
    
    def process_resume(self, resume_file_path: str, job_description: str, 
                     output_filename: Optional[str] = None,
                     pdf_method: str = 'auto') -> str:
        """
        Main processing function
        
        Args:
            resume_file_path: Path to HTML resume file
            job_description: Plain text job description
            output_filename: Optional custom output filename
            pdf_method: PDF generation method (auto, weasyprint, pdfkit, playwright)
        
        Returns:
            Path to generated PDF file
        """
        try:
            self.logger.info("Starting resume tailoring pipeline")
            
            # Step 1: Load resume HTML file
            resume_path = Path(resume_file_path)
            if not resume_path.exists():
                raise FileNotFoundError(f"Resume file not found: {resume_path}")
            
            with open(resume_path, 'r', encoding='utf-8') as f:
                resume_html_content = f.read()
            
            # Step 2: Tailor resume with LLM
            self.logger.info("Tailoring resume with LLM...")
            tailored_html = self.llm_manager.tailor_resume(resume_html_content, job_description)
            
            # Step 3: Generate output filename
            if not output_filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_filename = f"tailored_resume_{timestamp}.pdf"
            else:
                # Ensure PDF extension
                if not output_filename.endswith('.pdf'):
                    output_filename = output_filename.replace('.html', '.pdf')
            
            # Step 4: Convert HTML to PDF
            self.logger.info(f"Converting HTML to PDF using {pdf_method} method...")
            pdf_path = self.pdf_generator.html_to_pdf(
                tailored_html,
                output_filename,
                margins=self.config.resume.pdf_margins,
                method=pdf_method
            )
            
            # Step 5: Save HTML file for reference (optional)
            if self.config.debug:
                html_filename = output_filename.replace('.pdf', '.html')
                html_path = Path(self.config.resume.output_dir) / html_filename
                with open(html_path, 'w', encoding='utf-8') as f:
                    f.write(tailored_html)
                self.logger.info(f"Debug: HTML saved as {html_path}")
            
            self.logger.info(f"Pipeline completed successfully. PDF saved to: {pdf_path}")
            return str(pdf_path)
            
        except Exception as e:
            self.logger.error(f"Pipeline failed: {e}")
            raise


def start_web_server(pipeline: ResumePipeline, host: str, port: int, debug: bool):
    """Start Flask web server"""
    app = Flask(__name__)
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    
    # HTML template for the web interface
    HTML_TEMPLATE = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Resume Automation Pipeline</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            .form-group { margin-bottom: 20px; }
            label { display: block; margin-bottom: 5px; font-weight: bold; }
            input[type="file"], textarea, input[type="text"] { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; }
            textarea { height: 200px; resize: vertical; }
            button { background: #007bff; color: white; padding: 12px 24px; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; }
            button:hover { background: #0056b3; }
            button:disabled { background: #ccc; cursor: not-allowed; }
            .status { margin-top: 20px; padding: 10px; border-radius: 4px; }
            .success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
            .error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
            .loading { background: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; }
        </style>
    </head>
    <body>
        <h1>🤖 Resume Automation Pipeline</h1>
        <p>Upload your HTML resume and paste a job description to get a tailored PDF resume.</p>
        
        <form id="resumeForm" enctype="multipart/form-data">
            <div class="form-group">
                <label for="resume_file">HTML Resume File:</label>
                <input type="file" id="resume_file" name="resume_file" accept=".html,.htm" required>
                <small>Upload your HTML resume file</small>
            </div>
            
            <div class="form-group">
                <label for="job_description">Job Description:</label>
                <textarea id="job_description" name="job_description" placeholder="Paste the job description here..." required></textarea>
            </div>
            
            <div class="form-group">
                <label for="output_filename">Output Filename (optional):</label>
                <input type="text" id="output_filename" name="output_filename" placeholder="my_tailored_resume.pdf">
                <small>Leave empty for auto-generated filename</small>
            </div>
            
            <div class="form-group">
                <label for="pdf_method">PDF Method:</label>
                <select id="pdf_method" name="pdf_method">
                    <option value="auto">Auto (Recommended)</option>
                    <option value="weasyprint">WeasyPrint</option>
                    <option value="pdfkit">PDFKit</option>
                    <option value="playwright">Playwright</option>
                </select>
            </div>
            
            <button type="submit" id="submitBtn">🚀 Generate Tailored Resume</button>
        </form>
        
        <div id="status"></div>
        
        <script>
            document.getElementById('resumeForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const submitBtn = document.getElementById('submitBtn');
                const statusDiv = document.getElementById('status');
                
                submitBtn.disabled = true;
                submitBtn.textContent = '⏳ Processing...';
                statusDiv.innerHTML = '<div class="status loading">Processing your resume... This may take a few moments.</div>';
                
                const formData = new FormData();
                formData.append('resume_file', document.getElementById('resume_file').files[0]);
                formData.append('job_description', document.getElementById('job_description').value);
                formData.append('output_filename', document.getElementById('output_filename').value);
                formData.append('pdf_method', document.getElementById('pdf_method').value);
                
                try {
                    const response = await fetch('/process', {
                        method: 'POST',
                        body: formData
                    });
                    
                    if (response.ok) {
                        const blob = await response.blob();
                        const url = window.URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = url;
                        a.download = 'tailored_resume.pdf';
                        document.body.appendChild(a);
                        a.click();
                        window.URL.revokeObjectURL(url);
                        document.body.removeChild(a);
                        
                        statusDiv.innerHTML = '<div class="status success">✅ Resume tailored successfully! PDF downloaded.</div>';
                    } else {
                        const error = await response.text();
                        statusDiv.innerHTML = `<div class="status error">❌ Error: ${error}</div>`;
                    }
                } catch (error) {
                    statusDiv.innerHTML = `<div class="status error">❌ Error: ${error.message}</div>`;
                } finally {
                    submitBtn.disabled = false;
                    submitBtn.textContent = '🚀 Generate Tailored Resume';
                }
            });
        </script>
    </body>
    </html>
    """
    
    @app.route('/')
    def index():
        return render_template_string(HTML_TEMPLATE)
    
    @app.route('/process', methods=['POST'])
    def process_resume():
        try:
            # Check if resume file is uploaded
            if 'resume_file' not in request.files:
                return "No resume file uploaded", 400
            
            resume_file = request.files['resume_file']
            if resume_file.filename == '':
                return "No resume file selected", 400
            
            # Get job description
            job_description = request.form.get('job_description', '').strip()
            if not job_description:
                return "Job description is required", 400
            
            # Get optional parameters
            output_filename = request.form.get('output_filename', '').strip()
            pdf_method = request.form.get('pdf_method', 'auto')
            
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as temp_file:
                resume_content = resume_file.read().decode('utf-8')
                temp_file.write(resume_content)
                temp_file_path = temp_file.name
            
            try:
                # Process resume
                pdf_path = pipeline.process_resume(
                    resume_file_path=temp_file_path,
                    job_description=job_description,
                    output_filename=output_filename or None,
                    pdf_method=pdf_method
                )
                
                # Return PDF file
                return send_file(pdf_path, as_attachment=True, download_name=Path(pdf_path).name)
                
            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_file_path)
                except:
                    pass
                    
        except Exception as e:
            return f"Error processing resume: {str(e)}", 500
    
    @app.route('/health')
    def health():
        return jsonify({"status": "healthy", "service": "resume-automation-pipeline"})
    
    print(f"\n🌐 Starting Resume Automation Web Server...")
    print(f"📍 Server running at: http://localhost:{port}")
    print(f"🔗 Open in browser: http://localhost:{port}")
    print(f"📊 Health check: http://localhost:{port}/health")
    print(f"⏹️  Press Ctrl+C to stop the server")
    print(f"🔒 Server is running on localhost only (not accessible from other devices)")
    
    app.run(host=host, port=port, debug=debug, threaded=True)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Resume Automation Pipeline with Web Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Command line usage with HTML resume file
  python main_simple.py --resume-file "templates/resume.html" --job-description "Job description here..."

  # Custom output filename
  python main_simple.py --resume-file "templates/resume.html" --job-description "Job description..." --output "my_resume.pdf"

  # Using different PDF method
  python main_simple.py --resume-file "templates/resume.html" --job-description "Job description..." --pdf-method playwright

  # Start web server (localhost only)
  python main_simple.py --web --port 5000

Environment Variables:
  LLM_PROVIDER: openai, anthropic, google, local (default: openai)
  LLM_API_KEY: Your API key
  LLM_MODEL: Model name (default: provider-specific)
  LLM_TEMPERATURE: 0.0-1.0 (default: 0.7)
  LLM_MAX_TOKENS: Max tokens (default: 4000)
  OUTPUT_DIR: Output directory (default: output)
  DEBUG: true/false (default: false)
        """
    )
    
    parser.add_argument(
        '--resume-file', '-r',
        help='HTML resume file path'
    )
    
    parser.add_argument(
        '--job-description', '-j',
        help='Plain text job description'
    )
    
    parser.add_argument(
        '--output', '-o',
        help='Output PDF filename'
    )
    
    parser.add_argument(
        '--pdf-method',
        choices=['auto', 'weasyprint', 'pdfkit', 'playwright'],
        default='auto',
        help='PDF generation method (default: auto)'
    )
    
    parser.add_argument(
        '--web',
        action='store_true',
        help='Start web server instead of command line processing'
    )
    
    parser.add_argument(
        '--host',
        default='127.0.0.1',
        help='Host for web server (default: 127.0.0.1, localhost only)'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=5000,
        help='Port for web server (default: 5000)'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )
    
    args = parser.parse_args()
    
    # Set up logging
    setup_logging(args.debug)
    logger = logging.getLogger(__name__)
    
    try:
        # Load configuration
        config = load_config()
        validate_config(config)
        
        if args.debug:
            logger.info(f"Configuration loaded: {config}")
        
        # Create pipeline
        pipeline = ResumePipeline(config)
        
        # Check if web mode is requested
        if args.web:
            if not FLASK_AVAILABLE:
                print("❌ Flask is required for web mode. Install with: pip install flask")
                sys.exit(1)
            
            start_web_server(pipeline, args.host, args.port, args.debug)
            return
        
        # Command line mode - validate required arguments
        if not args.resume_file or not args.job_description:
            print("❌ Both --resume-file and --job-description are required for command line mode")
            print("   Use --web to start the web server instead")
            sys.exit(1)
        
        # Process resume
        pdf_path = pipeline.process_resume(
            resume_file_path=args.resume_file,
            job_description=args.job_description,
            output_filename=args.output,
            pdf_method=args.pdf_method
        )
        
        print(f"\n✅ Resume tailored successfully!")
        print(f"📄 PDF saved to: {pdf_path}")
        
        # Open PDF if on macOS
        if sys.platform == "darwin":
            try:
                os.system(f"open '{pdf_path}'")
                print("📖 PDF opened in default viewer")
            except:
                pass
        
    except KeyboardInterrupt:
        logger.info("Pipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
