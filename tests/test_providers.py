"""Tests for providers module."""

import os
from unittest.mock import Mock, patch, MagicMock

import pytest

from cybroutreach.providers import (
    OpenRouterProvider,
    OpenAIProvider,
    AnthropicProvider,
    get_provider,
    list_available_providers,
    GenerationResult,
)


class TestOpenRouterProvider:
    """Test OpenRouterProvider."""
    
    def test_init_with_api_key(self):
        """Test initialization with API key."""
        provider = OpenRouterProvider(api_key="test-key")
        assert provider.api_key == "test-key"
        assert provider.is_available() is True
    
    def test_init_without_api_key(self):
        """Test initialization without API key."""
        provider = OpenRouterProvider(api_key=None)
        assert provider.api_key is None
        assert provider.is_available() is False
    
    @patch.dict(os.environ, {"OPENROUTER_API_KEY": "env-key"})
    def test_init_from_env(self):
        """Test initialization from environment variable."""
        provider = OpenRouterProvider()
        assert provider.api_key == "env-key"
    
    def test_custom_model(self):
        """Test custom model selection."""
        provider = OpenRouterProvider(api_key="test", model="custom-model")
        assert provider.model == "custom-model"


class TestOpenAIProvider:
    """Test OpenAIProvider."""
    
    def test_init_with_api_key(self):
        """Test initialization with API key."""
        provider = OpenAIProvider(api_key="test-key")
        assert provider.api_key == "test-key"
        assert provider.is_available() is True
    
    def test_init_without_api_key(self):
        """Test initialization without API key."""
        provider = OpenAIProvider(api_key=None)
        assert provider.is_available() is False
    
    @patch.dict(os.environ, {"OPENAI_API_KEY": "env-key"})
    def test_init_from_env(self):
        """Test initialization from environment variable."""
        provider = OpenAIProvider()
        assert provider.api_key == "env-key"


class TestAnthropicProvider:
    """Test AnthropicProvider."""
    
    def test_init_with_api_key(self):
        """Test initialization with API key."""
        provider = AnthropicProvider(api_key="test-key")
        assert provider.api_key == "test-key"
        assert provider.is_available() is True
    
    def test_init_without_api_key(self):
        """Test initialization without API key."""
        provider = AnthropicProvider(api_key=None)
        assert provider.is_available() is False
    
    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": "env-key"})
    def test_init_from_env(self):
        """Test initialization from environment variable."""
        provider = AnthropicProvider()
        assert provider.api_key == "env-key"


class TestGetProvider:
    """Test get_provider function."""
    
    def test_raises_without_any_provider(self):
        """Test that error is raised when no provider is configured."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError) as exc_info:
                get_provider()
            assert "No AI provider configured" in str(exc_info.value)
    
    @patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"})
    def test_auto_selects_openrouter(self):
        """Test auto-selection of OpenRouter when configured."""
        provider = get_provider()
        assert isinstance(provider, OpenRouterProvider)
    
    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    def test_auto_selects_openai(self):
        """Test auto-selection of OpenAI when configured."""
        # Clear other providers to ensure OpenAI is selected
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": ""}):
            provider = get_provider()
            assert isinstance(provider, OpenAIProvider)
    
    @patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"})
    def test_explicit_provider(self):
        """Test explicit provider selection."""
        provider = get_provider("openrouter")
        assert isinstance(provider, OpenRouterProvider)
    
    def test_unavailable_explicit_provider(self):
        """Test error when explicit provider is unavailable."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError) as exc_info:
                get_provider("openrouter")
            assert "not available" in str(exc_info.value)


class TestListAvailableProviders:
    """Test list_available_providers function."""
    
    def test_returns_dict(self):
        """Test that function returns a dictionary."""
        providers = list_available_providers()
        assert isinstance(providers, dict)
        assert "openrouter" in providers
        assert "openai" in providers
        assert "anthropic" in providers
    
    @patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"})
    def test_shows_availability(self):
        """Test that availability status is correct."""
        providers = list_available_providers()
        assert providers["openrouter"] is True


class TestGenerationResult:
    """Test GenerationResult dataclass."""
    
    def test_creation(self):
        """Test creating a GenerationResult."""
        result = GenerationResult(
            content="Test content",
            model="test-model",
            tokens_used=100,
            cost=0.01
        )
        assert result.content == "Test content"
        assert result.model == "test-model"
        assert result.tokens_used == 100
        assert result.cost == 0.01
    
    def test_optional_fields(self):
        """Test GenerationResult with optional fields as None."""
        result = GenerationResult(
            content="Test",
            model="test-model"
        )
        assert result.tokens_used is None
        assert result.cost is None
