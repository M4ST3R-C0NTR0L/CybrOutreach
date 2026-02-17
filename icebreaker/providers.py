"""
AI provider integrations for IceBreaker.

Supports multiple AI providers through OpenRouter and direct integrations.
"""

import os
import time
from typing import Optional, Dict, Any, Iterator
from dataclasses import dataclass
from abc import ABC, abstractmethod

import requests
from tenacity import retry, stop_after_attempt, wait_exponential


@dataclass
class GenerationResult:
    """Result from AI generation."""
    content: str
    model: str
    tokens_used: Optional[int] = None
    cost: Optional[float] = None


class AIProvider(ABC):
    """Abstract base class for AI providers."""
    
    @abstractmethod
    def generate(
        self, 
        prompt: str, 
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> GenerationResult:
        """Generate content from a prompt."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is properly configured."""
        pass


class OpenRouterProvider(AIProvider):
    """OpenRouter provider - supports multiple models."""
    
    API_URL = "https://openrouter.ai/api/v1/chat/completions"
    DEFAULT_MODEL = "anthropic/claude-3.5-sonnet"
    
    # Cost-effective fallback models
    FALLBACK_MODELS = [
        "anthropic/claude-3.5-sonnet",
        "meta-llama/llama-3.1-70b-instruct",
        "google/gemini-pro-1.5",
        "mistralai/mistral-large",
    ]
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.model = model or os.getenv("OPENROUTER_MODEL", self.DEFAULT_MODEL)
        self.site_url = os.getenv("OPENROUTER_SITE_URL", "https://icebreaker.dev")
        self.site_name = os.getenv("OPENROUTER_SITE_NAME", "IceBreaker")
    
    def is_available(self) -> bool:
        """Check if OpenRouter API key is configured."""
        return bool(self.api_key)
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    def generate(
        self, 
        prompt: str, 
        temperature: float = 0.7,
        max_tokens: int = 1000,
        model: Optional[str] = None
    ) -> GenerationResult:
        """Generate content using OpenRouter."""
        if not self.api_key:
            raise ValueError(
                "OpenRouter API key not found. Set OPENROUTER_API_KEY environment variable."
            )
        
        use_model = model or self.model
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": self.site_url,
            "X-Title": self.site_name,
        }
        
        payload = {
            "model": use_model,
            "messages": [
                {"role": "system", "content": "You are an expert cold email copywriter."},
                {"role": "user", "content": prompt}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        
        response = requests.post(
            self.API_URL,
            headers=headers,
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        
        data = response.json()
        
        if "error" in data:
            raise ValueError(f"OpenRouter API error: {data['error']}")
        
        content = data["choices"][0]["message"]["content"]
        usage = data.get("usage", {})
        
        return GenerationResult(
            content=content.strip(),
            model=use_model,
            tokens_used=usage.get("total_tokens"),
        )
    
    def generate_with_fallback(
        self, 
        prompt: str, 
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> GenerationResult:
        """Generate with automatic fallback models."""
        models_to_try = [self.model] + [
            m for m in self.FALLBACK_MODELS if m != self.model
        ]
        
        last_error = None
        for model in models_to_try:
            try:
                return self.generate(prompt, temperature, max_tokens, model=model)
            except Exception as e:
                last_error = e
                time.sleep(1)
                continue
        
        raise ValueError(f"All models failed. Last error: {last_error}")


class OpenAIProvider(AIProvider):
    """Direct OpenAI integration."""
    
    API_URL = "https://api.openai.com/v1/chat/completions"
    DEFAULT_MODEL = "gpt-4o-mini"
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model or os.getenv("OPENAI_MODEL", self.DEFAULT_MODEL)
    
    def is_available(self) -> bool:
        """Check if OpenAI API key is configured."""
        return bool(self.api_key)
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    def generate(
        self, 
        prompt: str, 
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> GenerationResult:
        """Generate content using OpenAI."""
        if not self.api_key:
            raise ValueError(
                "OpenAI API key not found. Set OPENAI_API_KEY environment variable."
            )
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are an expert cold email copywriter."},
                {"role": "user", "content": prompt}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        
        response = requests.post(
            self.API_URL,
            headers=headers,
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        
        data = response.json()
        content = data["choices"][0]["message"]["content"]
        usage = data.get("usage", {})
        
        return GenerationResult(
            content=content.strip(),
            model=self.model,
            tokens_used=usage.get("total_tokens"),
        )


class AnthropicProvider(AIProvider):
    """Direct Anthropic/Claude integration."""
    
    API_URL = "https://api.anthropic.com/v1/messages"
    DEFAULT_MODEL = "claude-3-5-sonnet-20241022"
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.model = model or os.getenv("ANTHROPIC_MODEL", self.DEFAULT_MODEL)
    
    def is_available(self) -> bool:
        """Check if Anthropic API key is configured."""
        return bool(self.api_key)
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    def generate(
        self, 
        prompt: str, 
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> GenerationResult:
        """Generate content using Anthropic."""
        if not self.api_key:
            raise ValueError(
                "Anthropic API key not found. Set ANTHROPIC_API_KEY environment variable."
            )
        
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01",
        }
        
        payload = {
            "model": self.model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "system": "You are an expert cold email copywriter.",
            "messages": [
                {"role": "user", "content": prompt}
            ],
        }
        
        response = requests.post(
            self.API_URL,
            headers=headers,
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        
        data = response.json()
        content = data["content"][0]["text"]
        usage = data.get("usage", {})
        
        return GenerationResult(
            content=content.strip(),
            model=self.model,
            tokens_used=usage.get("input_tokens", 0) + usage.get("output_tokens", 0),
        )


def get_provider(provider_name: Optional[str] = None) -> AIProvider:
    """
    Get an AI provider instance.
    
    Priority:
    1. Explicit provider_name parameter
    2. ICEBREAKER_PROVIDER env var
    3. First available provider (OpenRouter > OpenAI > Anthropic)
    
    Args:
        provider_name: Name of provider to use ('openrouter', 'openai', 'anthropic')
        
    Returns:
        Configured AI provider instance
        
    Raises:
        ValueError: If no provider is available
    """
    provider_name = provider_name or os.getenv("ICEBREAKER_PROVIDER", "auto")
    
    providers: Dict[str, AIProvider] = {
        "openrouter": OpenRouterProvider(),
        "openai": OpenAIProvider(),
        "anthropic": AnthropicProvider(),
    }
    
    if provider_name != "auto" and provider_name in providers:
        provider = providers[provider_name]
        if provider.is_available():
            return provider
        raise ValueError(
            f"Provider '{provider_name}' is not available. "
            f"Please check your API key configuration."
        )
    
    # Auto-detect available provider
    for name, provider in providers.items():
        if provider.is_available():
            return provider
    
    raise ValueError(
        "No AI provider configured. Please set one of these environment variables:\n"
        "  - OPENROUTER_API_KEY (recommended - supports multiple models)\n"
        "  - OPENAI_API_KEY\n"
        "  - ANTHROPIC_API_KEY"
    )


def list_available_providers() -> Dict[str, bool]:
    """List all providers and their availability status."""
    return {
        "openrouter": OpenRouterProvider().is_available(),
        "openai": OpenAIProvider().is_available(),
        "anthropic": AnthropicProvider().is_available(),
    }
