"""Pytest configuration for CybrOutreach."""

import os
import pytest
from unittest.mock import Mock


@pytest.fixture
def mock_provider():
    """Create a mock AI provider for testing."""
    provider = Mock()
    provider.generate.return_value = Mock(
        content="Subject: Test Subject\n\nTest email body content.",
        model="test-model",
        tokens_used=100
    )
    provider.is_available.return_value = True
    return provider


@pytest.fixture
def sample_leads():
    """Sample leads data for testing."""
    return [
        {"name": "John Doe", "company": "Acme Corp", "context": "AI startup"},
        {"name": "Jane Smith", "company": "Tech Inc", "context": "SaaS company"},
    ]


@pytest.fixture(autouse=True)
def clean_env():
    """Clean environment variables before each test."""
    # Store original values
    env_vars = [
        "OPENROUTER_API_KEY",
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "ICEBREAKER_PROVIDER",
    ]
    original = {var: os.environ.get(var) for var in env_vars}
    
    # Clear for test
    for var in env_vars:
        if var in os.environ:
            del os.environ[var]
    
    yield
    
    # Restore original values
    for var, value in original.items():
        if value is not None:
            os.environ[var] = value
        elif var in os.environ:
            del os.environ[var]
