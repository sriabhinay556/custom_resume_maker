# Resume Automation Pipeline

A simple, powerful tool that automatically tailors your resume to match any job description using AI. Takes an HTML resume template and job description, then generates a professionally tailored PDF resume.

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- OpenAI API key (or other LLM provider)

### 1. Clone/Download the Project
```bash
git clone <repository-url>
cd resume_builder
```

### 2. Set Up Virtual Environment (Recommended)
```bash
# Create virtual environment
python3 -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate
```

### 3. Install Dependencies
```bash
# Install core dependencies
pip install python-dotenv openai weasyprint flask

# Or install all dependencies
pip install -r requirements.txt
```

### 4. Set Up API Key
Create a `.env` file in the project directory:
```bash
# Create .env file
echo "LLM_PROVIDER=openai" > .env
echo "LLM_API_KEY=your-openai-api-key-here" >> .env
```

**Get your OpenAI API key from:** https://platform.openai.com/api-keys

### 5. Prepare Your Resume
Place your HTML resume file in the `templates/` folder. You can use the existing templates as examples:
- `templates/1-base_resume_format.html`
- `templates/2_base_resume_format.html`

### 6. Run the Pipeline

**Option A: Command Line Interface**
```bash
# Basic usage
python3 main_simple.py --resume-file "templates/your_resume.html" --job-description "Job description here..."

# With custom output filename
python3 main_simple.py --resume-file "templates/your_resume.html" --job-description "Job description..." --output "my_tailored_resume.pdf"

# Using different PDF method (if WeasyPrint fails)
python3 main_simple.py --resume-file "templates/your_resume.html" --job-description "Job description..." --pdf-method playwright
```

**Option B: Web Interface (Recommended)**
```bash
# Start web server
python3 main_simple.py --web

# Start web server accessible from other computers
python3 main_simple.py --web --host 0.0.0.0 --port 5000
```

Then open your browser to `http://localhost:5000` and use the web interface!

## 📁 Project Structure

```
resume_builder/
├── main_simple.py          # Main pipeline script
├── config.py              # Configuration management
├── llm_client.py          # LLM provider integration
├── pdf_generator.py       # PDF generation
├── requirements.txt       # Python dependencies
├── .env                   # Your API keys (create this)
├── templates/             # HTML resume templates
│   ├── 1-base_resume_format.html
│   └── 2_base_resume_format.html
├── output/                # Generated PDFs
└── README.md             # This file
```

## 🔧 Configuration

### Environment Variables (.env file)
```bash
# LLM Provider (openai, anthropic, google, local)
LLM_PROVIDER=openai

# Your API Key
LLM_API_KEY=sk-your-openai-api-key-here

# Optional settings
LLM_MODEL=gpt-4o-mini
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=4000
OUTPUT_DIR=output
DEBUG=false
PDF_MARGINS=0
```

### Supported LLM Providers
- **OpenAI** (recommended): GPT-4, GPT-3.5-turbo
- **Anthropic**: Claude-3.5-Sonnet, Claude-3-Haiku
- **Google**: Gemini-1.5-Flash, Gemini-1.5-Pro
- **Local**: Ollama, other local LLM servers

## 📝 Usage Examples

### Example 1: Command Line Usage
```bash
python3 main_simple.py --resume-file "templates/1-base_resume_format.html" --job-description "We are looking for a Senior AI Engineer with experience in machine learning, Python, and cloud technologies..."
```

### Example 2: Custom Output
```bash
python3 main_simple.py --resume-file "templates/1-base_resume_format.html" --job-description "Job description..." --output "ai_engineer_resume.pdf"
```

### Example 3: Web Interface
```bash
# Start web server
python3 main_simple.py --web

# Access from browser: http://localhost:5000
# Upload HTML resume file and paste job description
# Download tailored PDF automatically
```

### Example 4: Remote Access
```bash
# Start server accessible from other computers
python3 main_simple.py --web --host 0.0.0.0 --port 5000

# Access from other computers: http://YOUR_IP:5000
```

## 🛠️ Troubleshooting

### PDF Generation Issues on macOS
If you get WeasyPrint errors, try these solutions:

**Option 1: Install Playwright (Recommended)**
```bash
pip install playwright
playwright install
python3 main_simple.py --pdf-method playwright "resume.html" "Job description..."
```

**Option 2: Fix WeasyPrint Dependencies**
```bash
brew install pango gdk-pixbuf libffi
```

**Option 3: Use pdfkit**
```bash
pip install pdfkit
brew install wkhtmltopdf
python3 main_simple.py --pdf-method pdfkit "resume.html" "Job description..."
```

### Common Issues

1. **API Key Not Set**
   - Make sure your `.env` file exists and contains `LLM_API_KEY=your-key-here`
   - Verify the API key is valid and has credits

2. **Resume File Not Found**
   - Ensure your HTML resume file is in the `templates/` folder
   - Check the filename is correct (case-sensitive)

3. **Import Errors**
   - Make sure you're in the virtual environment: `source venv/bin/activate`
   - Install missing packages: `pip install -r requirements.txt`

4. **Permission Errors**
   - Ensure the `output/` directory is writable
   - Check file permissions

## 🎯 How It Works

1. **Input**: HTML resume template + Job description text
2. **Processing**: AI analyzes the job requirements and tailors your resume
3. **Output**: Professional PDF resume optimized for the specific role

The AI:
- Preserves all your original information and achievements
- Enhances bullet points with relevant keywords from the job description
- Reorders content to highlight most relevant experience first
- Maintains professional formatting and structure

## 📋 Command Line Options

```bash
python3 main_simple.py [OPTIONS]

Options:
  --resume-file, -r     HTML resume file path
  --job-description, -j Plain text job description
  --output, -o          Output PDF filename
  --pdf-method          PDF generation method (auto, weasyprint, pdfkit, playwright)
  --web                 Start web server instead of command line processing
  --host                Host for web server (default: 127.0.0.1)
  --port                Port for web server (default: 5000)
  --debug               Enable debug logging
  --help                Show help message
```

## 🌐 Web Interface Features

- **File Upload**: Upload HTML resume files directly
- **Real-time Processing**: See processing status in real-time
- **Automatic Download**: PDF downloads automatically when ready
- **Remote Access**: Access from any computer on the network
- **Health Check**: Built-in health monitoring endpoint
- **Error Handling**: Clear error messages and troubleshooting

## 🔒 Security Notes

- Never commit your `.env` file to version control
- Keep your API keys secure and private
- The `.env` file is already in `.gitignore`

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Enable debug mode: `python3 main_simple.py --debug ...`
3. Check the log file: `resume_pipeline.log`
4. Verify your API key and dependencies

## 🎉 Success!

Once set up, you can tailor your resume to any job description in seconds:

**Command Line:**
```bash
python3 main_simple.py --resume-file "templates/your_resume.html" --job-description "Job description here..."
```

**Web Interface:**
```bash
python3 main_simple.py --web
# Then visit http://localhost:5000
```

The system will generate a professionally tailored PDF resume in the `output/` folder, ready for your job application!

## 🚀 Quick Start Summary

1. **Install**: `pip install python-dotenv openai weasyprint flask`
2. **Configure**: Add your OpenAI API key to `.env` file
3. **Run**: `python3 main_simple.py --web`
4. **Access**: Open `http://localhost:5000` in your browser
5. **Upload**: Your HTML resume and paste job description
6. **Download**: Get your tailored PDF resume instantly!
