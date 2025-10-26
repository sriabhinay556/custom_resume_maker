#!/usr/bin/env python3
"""
Setup script for the Resume Automation Pipeline.
Helps with installation and configuration.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path


def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True


def install_package(package):
    """Install a package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError:
        return False


def install_dependencies():
    """Install required dependencies"""
    print("\n📦 Installing dependencies...")
    
    # Core dependencies
    core_packages = [
        "requests>=2.31.0",
    ]
    
    # LLM providers (user can choose)
    llm_packages = {
        "openai": "openai>=1.0.0",
        "anthropic": "anthropic>=0.7.0", 
        "google": "google-generativeai>=0.3.0",
    }
    
    # PDF generation packages
    pdf_packages = {
        "weasyprint": "weasyprint>=60.0",
        "pdfkit": "pdfkit>=1.0.0",
        "playwright": "playwright>=1.40.0",
    }
    
    # Install core packages
    for package in core_packages:
        print(f"Installing {package}...")
        if not install_package(package):
            print(f"❌ Failed to install {package}")
            return False
    
    # Ask user for LLM provider
    print("\n🤖 Choose your LLM provider:")
    print("1. OpenAI (GPT models)")
    print("2. Anthropic (Claude models)")
    print("3. Google (Gemini models)")
    print("4. Skip LLM installation")
    
    choice = input("Enter choice (1-4): ").strip()
    
    if choice == "1":
        install_package(llm_packages["openai"])
    elif choice == "2":
        install_package(llm_packages["anthropic"])
    elif choice == "3":
        install_package(llm_packages["google"])
    
    # Ask user for PDF generation method
    print("\n📄 Choose PDF generation method:")
    print("1. WeasyPrint (recommended)")
    print("2. pdfkit (requires wkhtmltopdf)")
    print("3. Playwright (browser-based)")
    print("4. Skip PDF installation")
    
    choice = input("Enter choice (1-4): ").strip()
    
    if choice == "1":
        install_package(pdf_packages["weasyprint"])
    elif choice == "2":
        install_package(pdf_packages["pdfkit"])
        print("⚠️  Note: You'll need to install wkhtmltopdf separately")
    elif choice == "3":
        install_package(pdf_packages["playwright"])
        print("Installing Playwright browsers...")
        subprocess.run([sys.executable, "-m", "playwright", "install"])
    
    return True


def setup_environment():
    """Set up environment variables"""
    print("\n🔧 Setting up environment...")
    
    # Create .env file template
    env_content = """# Resume Automation Pipeline Configuration
# Add your actual API keys here

# LLM Provider (openai, anthropic, google, local)
LLM_PROVIDER=openai

# Your OpenAI API Key (get it from https://platform.openai.com/api-keys)
LLM_API_KEY=sk-your-openai-api-key-here

# Model name (optional, uses provider default)
# LLM_MODEL=gpt-4o-mini

# Temperature (0.0-1.0, default: 0.7)
# LLM_TEMPERATURE=0.7

# Max tokens (default: 4000)
# LLM_MAX_TOKENS=4000

# Output directory (default: output)
# OUTPUT_DIR=output

# Debug mode (true/false, default: false)
# DEBUG=false

# PDF margins (default: 0 for no margins)
# PDF_MARGINS=0

# Font settings
# FONT_FAMILY=Arial, sans-serif
# FONT_SIZE=12px
# LINE_HEIGHT=1.4
"""
    
    env_file = Path(".env")
    if not env_file.exists():
        env_file.write_text(env_content)
        print("✅ Created .env file template")
        print("   📝 Please edit .env and add your OpenAI API key")
        print("   🔑 Get your API key from: https://platform.openai.com/api-keys")
    else:
        print("✅ .env file already exists")
    
    # Create output directory
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    print("✅ Created output directory")


def test_installation():
    """Test the installation"""
    print("\n🧪 Testing installation...")
    
    try:
        # Test imports
        import config
        import llm_client
        import resume_parser
        import pdf_generator
        print("✅ All modules imported successfully")
        
        # Test configuration loading
        config_obj = config.load_config()
        print("✅ Configuration loaded successfully")
        
        print("🎉 Installation test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Installation test failed: {e}")
        return False


def main():
    """Main setup function"""
    print("🚀 Resume Automation Pipeline Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Dependency installation failed")
        sys.exit(1)
    
    # Setup environment
    setup_environment()
    
    # Test installation
    if not test_installation():
        print("❌ Installation test failed")
        sys.exit(1)
    
    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Edit .env file and add your API key")
    print("2. Run: python example.py")
    print("3. Or run: python main.py --help")
    print("\nFor more information, see README.md")


if __name__ == "__main__":
    main()
