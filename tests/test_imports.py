import pytest
from pathlib import Path
import sys

def test_src_importable():
    """Verify that src modules can be imported."""
    try:
        import database
        import logger_config
    except ImportError as e:
        pytest.fail(f"Failed to import src modules: {e}")

def test_scrapers_importable():
    """Verify that scraper modules can be imported."""
    try:
        from scrapers import base_scraper_v2
    except ImportError as e:
        pytest.fail(f"Failed to import scraper modules: {e}")
