"""
Pytest fixtures for duq-tools server tests.
"""

import pytest
from server import app


@pytest.fixture
def client():
    """Flask test client for HTTP requests."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def runner():
    """Click CLI test runner (if we add Click commands later)."""
    return app.test_cli_runner()
