"""Test suite for CybrOutreach."""

import pytest


def test_import():
    """Test that the package can be imported."""
    import cybroutreach
    assert cybroutreach.__version__ == "1.0.0"
