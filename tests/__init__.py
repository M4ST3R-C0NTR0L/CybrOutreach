"""Test suite for IceBreaker."""

import pytest


def test_import():
    """Test that the package can be imported."""
    import icebreaker
    assert icebreaker.__version__ == "1.0.0"
