#!/usr/bin/env python3
"""
Quick setup script to create .env file with OpenAI API key.
"""

import os
from pathlib import Path


def create_env_file():
    """Create .env file with OpenAI configuration"""
    
    print("🔧 Setting up .env file for OpenAI")
    print("=" * 40)
    
    # Get API key from user
    print("Please enter your OpenAI API key:")
    print("(Get it from: https://platform.openai.com/api-keys)")
    api_key = input("API Key: ").strip()
    
    if not api_key:
        print("❌ No API key provided. Exiting.")
        return False
    
    if not api_key.startswith('sk-'):
        print("⚠️  Warning: OpenAI API keys usually start with 'sk-'")
        confirm = input("Continue anyway? (y/n): ").strip().lower()
        if confirm != 'y':
            return False
    
    # Create .env content
    env_content = f"""# Resume Automation Pipeline Configuration
# Generated automatically

# LLM Provider
LLM_PROVIDER=openai

# Your OpenAI API Key
LLM_API_KEY={api_key}

# Model name (optional)
LLM_MODEL=gpt-4o-mini

# Temperature (0.0-1.0)
LLM_TEMPERATURE=0.7

# Max tokens
LLM_MAX_TOKENS=4000

# Output directory
OUTPUT_DIR=output

# Debug mode
DEBUG=false

# PDF margins (0 for no margins)
PDF_MARGINS=0
"""
    
    # Write .env file
    env_file = Path(".env")
    env_file.write_text(env_content)
    
    print(f"✅ Created .env file with your OpenAI API key")
    print(f"📁 Location: {env_file.absolute()}")
    
    # Test the configuration
    print("\n🧪 Testing configuration...")
    try:
        from config import load_config, validate_config
        config = load_config()
        validate_config(config)
        print("✅ Configuration is valid!")
        print(f"   Provider: {config.llm.provider.value}")
        print(f"   Model: {config.llm.model}")
        return True
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False


def main():
    """Main function"""
    print("🚀 Resume Pipeline - OpenAI Setup")
    print("=" * 40)
    
    # Check if .env already exists
    env_file = Path(".env")
    if env_file.exists():
        print("⚠️  .env file already exists!")
        overwrite = input("Overwrite it? (y/n): ").strip().lower()
        if overwrite != 'y':
            print("Setup cancelled.")
            return
    
    # Create .env file
    if create_env_file():
        print("\n🎉 Setup completed successfully!")
        print("\nNext steps:")
        print("1. Run: python example.py")
        print("2. Or run: python main.py --help")
        print("3. Try: python main.py --resume-file sample_resume.json 'Job description here...'")
    else:
        print("\n❌ Setup failed. Please check your API key and try again.")


if __name__ == "__main__":
    main()
