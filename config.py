"""
Configuration module for the resume automation pipeline.
Allows easy switching between LLM providers and customization of settings.
"""

import os
from dataclasses import dataclass
from typing import Dict, Any, Optional
from enum import Enum
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    # Load .env file if it exists
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
    else:
        # Try to load from current directory
        load_dotenv()
except ImportError:
    # dotenv not installed, continue without it
    pass


class LLMProvider(Enum):
    """Supported LLM providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    LOCAL = "local"


@dataclass
class LLMConfig:
    """Configuration for LLM providers"""
    provider: LLMProvider
    api_key: Optional[str] = None
    model: str = ""
    temperature: float = 0.7
    max_tokens: int = 4000
    base_url: Optional[str] = None  # For local or custom endpoints


@dataclass
class ResumeConfig:
    """Configuration for resume processing"""
    template_path: str = "templates/resume_template.html"
    output_dir: str = "output"
    pdf_margins: str = "0"  # No margins for clean PDF
    font_family: str = "Arial, sans-serif"
    font_size: str = "12px"
    line_height: str = "1.4"


@dataclass
class PipelineConfig:
    """Main configuration for the entire pipeline"""
    llm: LLMConfig
    resume: ResumeConfig
    debug: bool = False


def load_config() -> PipelineConfig:
    """Load configuration from environment variables and defaults"""
    
    # LLM Configuration
    provider_name = os.getenv("LLM_PROVIDER", "openai").lower()
    try:
        provider = LLMProvider(provider_name)
    except ValueError:
        provider = LLMProvider.OPENAI
    
    llm_config = LLMConfig(
        provider=provider,
        api_key=os.getenv("LLM_API_KEY"),
        model=os.getenv("LLM_MODEL", get_default_model(provider)),
        temperature=float(os.getenv("LLM_TEMPERATURE", "0.7")),
        max_tokens=int(os.getenv("LLM_MAX_TOKENS", "4000")),
        base_url=os.getenv("LLM_BASE_URL")
    )
    
    # Resume Configuration
    resume_config = ResumeConfig(
        template_path=os.getenv("RESUME_TEMPLATE_PATH", "templates/resume_template.html"),
        output_dir=os.getenv("OUTPUT_DIR", "output"),
        pdf_margins=os.getenv("PDF_MARGINS", "0"),
        font_family=os.getenv("FONT_FAMILY", "Arial, sans-serif"),
        font_size=os.getenv("FONT_SIZE", "12px"),
        line_height=os.getenv("LINE_HEIGHT", "1.4")
    )
    
    return PipelineConfig(
        llm=llm_config,
        resume=resume_config,
        debug=os.getenv("DEBUG", "false").lower() == "true"
    )


def get_default_model(provider: LLMProvider) -> str:
    """Get default model for each provider"""
    defaults = {
        LLMProvider.OPENAI: "gpt-4o-mini",
        LLMProvider.ANTHROPIC: "claude-3-5-sonnet-20241022",
        LLMProvider.GOOGLE: "gemini-1.5-flash",
        LLMProvider.LOCAL: "llama-3.1-8b"
    }
    return defaults.get(provider, "gpt-4o-mini")


def validate_config(config: PipelineConfig) -> None:
    """Validate configuration and raise errors if invalid"""
    if not config.llm.api_key and config.llm.provider != LLMProvider.LOCAL:
        raise ValueError(f"API key required for {config.llm.provider.value} provider")
    
    if not config.llm.model:
        raise ValueError("LLM model must be specified")
    
    # Create output directory if it doesn't exist
    os.makedirs(config.resume.output_dir, exist_ok=True)
