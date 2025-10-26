# How to Set Up Your .env File

## Quick Setup Instructions

1. **Create a .env file** in the project directory:
   ```bash
   touch .env
   ```

2. **Add your OpenAI API key** to the .env file:
   ```
   # Resume Automation Pipeline Configuration
   LLM_PROVIDER=openai
   LLM_API_KEY=sk-your-actual-openai-api-key-here
   LLM_MODEL=gpt-4o-mini
   LLM_TEMPERATURE=0.7
   LLM_MAX_TOKENS=4000
   OUTPUT_DIR=output
   DEBUG=false
   PDF_MARGINS=0
   ```

3. **Get your OpenAI API key** from: https://platform.openai.com/api-keys

4. **Replace** `sk-your-actual-openai-api-key-here` with your real API key

## Alternative: Use the setup script

```bash
python3 setup_openai.py
```

This will prompt you for your API key and create the .env file automatically.

## Test your setup

```bash
python3 -c "from config import load_config; config = load_config(); print(f'Provider: {config.llm.provider.value}')"
```

## Example .env file content

```
LLM_PROVIDER=openai
LLM_API_KEY=sk-proj-abc123def456ghi789jkl012mno345pqr678stu901vwx234yz
LLM_MODEL=gpt-4o-mini
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=4000
OUTPUT_DIR=output
DEBUG=false
PDF_MARGINS=0
```

## Security Note

- Never commit your .env file to version control
- Keep your API keys secure
- The .env file is already in .gitignore
