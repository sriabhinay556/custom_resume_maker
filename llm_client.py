"""
LLM integration module supporting multiple providers.
Handles API calls and response processing for different LLM services.
"""

import json
import logging
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod

from config import LLMConfig, LLMProvider


logger = logging.getLogger(__name__)


class LLMClient(ABC):
    """Abstract base class for LLM clients"""
    
    @abstractmethod
    def generate_response(self, prompt: str, **kwargs) -> str:
        """Generate response from the LLM"""
        pass


class OpenAIClient(LLMClient):
    """OpenAI API client"""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        try:
            import openai
            self.client = openai.OpenAI(
                api_key=config.api_key,
                base_url=config.base_url
            )
        except ImportError:
            raise ImportError("OpenAI package not installed. Run: pip install openai")
    
    def generate_response(self, prompt: str, **kwargs) -> str:
        """Generate response using OpenAI API"""
        try:
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                **kwargs
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise


class AnthropicClient(LLMClient):
    """Anthropic Claude API client"""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=config.api_key)
        except ImportError:
            raise ImportError("Anthropic package not installed. Run: pip install anthropic")
    
    def generate_response(self, prompt: str, **kwargs) -> str:
        """Generate response using Anthropic API"""
        try:
            response = self.client.messages.create(
                model=self.config.model,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                messages=[{"role": "user", "content": prompt}],
                **kwargs
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise


class GoogleClient(LLMClient):
    """Google Gemini API client"""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        try:
            import google.generativeai as genai
            genai.configure(api_key=config.api_key)
            self.model = genai.GenerativeModel(config.model)
        except ImportError:
            raise ImportError("Google Generative AI package not installed. Run: pip install google-generativeai")
    
    def generate_response(self, prompt: str, **kwargs) -> str:
        """Generate response using Google Gemini API"""
        try:
            generation_config = {
                "temperature": self.config.temperature,
                "max_output_tokens": self.config.max_tokens,
            }
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config,
                **kwargs
            )
            return response.text
        except Exception as e:
            logger.error(f"Google API error: {e}")
            raise


class LocalClient(LLMClient):
    """Local LLM client (for Ollama, etc.)"""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self.base_url = config.base_url or "http://localhost:11434"
    
    def generate_response(self, prompt: str, **kwargs) -> str:
        """Generate response using local LLM (Ollama)"""
        try:
            import requests
            
            url = f"{self.base_url}/api/generate"
            data = {
                "model": self.config.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": self.config.temperature,
                    "num_predict": self.config.max_tokens
                }
            }
            
            response = requests.post(url, json=data)
            response.raise_for_status()
            
            result = response.json()
            return result.get("response", "")
        except Exception as e:
            logger.error(f"Local LLM error: {e}")
            raise


class LLMManager:
    """Manager class for handling different LLM providers"""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self.client = self._create_client()
    
    def _create_client(self) -> LLMClient:
        """Create appropriate client based on provider"""
        if self.config.provider == LLMProvider.OPENAI:
            return OpenAIClient(self.config)
        elif self.config.provider == LLMProvider.ANTHROPIC:
            return AnthropicClient(self.config)
        elif self.config.provider == LLMProvider.GOOGLE:
            return GoogleClient(self.config)
        elif self.config.provider == LLMProvider.LOCAL:
            return LocalClient(self.config)
        else:
            raise ValueError(f"Unsupported provider: {self.config.provider}")
    
    def tailor_resume(self, resume_text: str, job_description: str) -> str:
        """Generate tailored resume based on job description"""

        prompt = f"""
You are an expert resume writer specializing in AI/tech roles. Your task is to tailor the given resume to match the job description while maintaining the original resume's professional structure, formatting, and quality.

ORIGINAL RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

CRITICAL REQUIREMENTS:
1. PRESERVE ALL ORIGINAL CONTENT: Keep all personal information, company names, job titles, dates, locations, and achievements exactly as they appear in the original resume.

2. MAINTAIN PROFESSIONAL STRUCTURE: Keep the same sections, formatting, and layout as the original resume. Do not change the overall structure.

3. ENHANCE RELEVANCE: For each existing bullet point, enhance it by:
   - Adding relevant keywords from the job description
   - Emphasizing skills/technologies that match the JD requirements
   - Quantifying achievements where possible
   - Making descriptions more impactful for the target role

4. PRESERVE FORMATTING: Maintain the original resume's:
   - Section headers and organization
   - Bullet point structure
   - Contact information layout
   - Professional tone and style
   - All hyperlinks and certifications

5. STRATEGIC REORDERING: You may reorder bullet points within sections to highlight the most relevant experience first, but keep all original content.

6. HTML OUTPUT: Return a complete HTML document with professional CSS styling that matches the original resume's clean, ATS-friendly format.

Return ONLY the complete HTML document with embedded CSS. No explanations or markdown formatting.
"""


        try:
            response = self.client.generate_response(prompt)
            
            # Extract HTML from response if it's wrapped in markdown
            if "```html" in response:
                start = response.find("```html") + 7
                end = response.find("```", start)
                response = response[start:end].strip()
            elif "```" in response:
                start = response.find("```") + 3
                end = response.find("```", start)
                response = response[start:end].strip()
            
            return response
            
        except Exception as e:
            logger.error(f"Error tailoring resume: {e}")
            raise


def create_llm_manager(config: LLMConfig) -> LLMManager:
    """Factory function to create LLM manager"""
    return LLMManager(config)
