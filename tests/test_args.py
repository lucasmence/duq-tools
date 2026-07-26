"""
Tests for command-line argument parsing.

These tests mock sys.argv to simulate different CLI invocations.
"""

import sys
from unittest.mock import patch

import pytest
from server import parse_args


class TestParseArgsDefaults:
    """Test default values when no arguments are provided."""

    def test_default_host(self):
        """Default host should be 0.0.0.0."""

        with patch.object(sys, "argv", ["server.py"]):
            args = parse_args()
        assert args.host == "0.0.0.0"

    def test_default_port(self):
        """Default port should be 5000."""
        from server import parse_args
        with patch.object(sys, "argv", ["server.py"]):
            args = parse_args()
        assert args.port == 5000

    def test_default_debug(self):
        """Debug should default to True (from DEBUG=1 env)."""
        from server import parse_args
        with patch.object(sys, "argv", ["server.py"]):
            args = parse_args()
        assert args.debug is True

    def test_default_https_disabled(self):
        """HTTPS should be disabled by default."""
        from server import parse_args
        with patch.object(sys, "argv", ["server.py"]):
            args = parse_args()
        assert args.https is False


class TestParseArgsFlags:
    """Test that CLI flags override defaults correctly."""

    def test_https_flag(self):
        """--https should enable HTTPS."""
        from server import parse_args
        with patch.object(sys, "argv", ["server.py", "--https"]):
            args = parse_args()
        assert args.https is True

    def test_port_flag(self):
        """--port should override the default port."""
        from server import parse_args
        with patch.object(sys, "argv", ["server.py", "--port", "8080"]):
            args = parse_args()
        assert args.port == 8080

    def test_host_flag(self):
        """--host should override the default host."""
        from server import parse_args
        with patch.object(sys, "argv", ["server.py", "--host", "127.0.0.1"]):
            args = parse_args()
        assert args.host == "127.0.0.1"

    def test_no_debug_flag(self):
        """--no-debug should disable debug mode."""
        from server import parse_args
        with patch.object(sys, "argv", ["server.py", "--no-debug"]):
            args = parse_args()
        assert args.debug is False

    def test_debug_explicit(self):
        """--debug should enable debug (even if env says otherwise)."""
        from server import parse_args
        with patch.object(sys, "argv", ["server.py", "--debug"]):
            args = parse_args()
        assert args.debug is True

    def test_all_flags_together(self):
        """All flags should work together."""
        from server import parse_args
        argv = ["server.py", "--https", "--host", "127.0.0.1", "--port", "8443", "--no-debug"]
        with patch.object(sys, "argv", argv):
            args = parse_args()
        assert args.https is True
        assert args.host == "127.0.0.1"
        assert args.port == 8443
        assert args.debug is False


class TestParseArgsEnvVars:
    """Test that environment variables are respected as defaults."""

    def test_https_from_env(self, monkeypatch):
        """HTTPS=1 should enable HTTPS by default."""
        monkeypatch.setenv("HTTPS", "1")
        from server import parse_args
        with patch.object(sys, "argv", ["server.py"]):
            args = parse_args()
        assert args.https is True

    def test_port_from_env(self, monkeypatch):
        """PORT env var should set the default port."""
        monkeypatch.setenv("PORT", "3000")
        from server import parse_args
        with patch.object(sys, "argv", ["server.py"]):
            args = parse_args()
        assert args.port == 3000

    def test_host_from_env(self, monkeypatch):
        """HOST env var should set the default host."""
        monkeypatch.setenv("HOST", "127.0.0.1")
        from server import parse_args
        with patch.object(sys, "argv", ["server.py"]):
            args = parse_args()
        assert args.host == "127.0.0.1"

    def test_debug_from_env(self, monkeypatch):
        """DEBUG=0 should disable debug by default."""
        monkeypatch.setenv("DEBUG", "0")
        from server import parse_args
        with patch.object(sys, "argv", ["server.py"]):
            args = parse_args()
        assert args.debug is False

    def test_cli_flag_overrides_env(self, monkeypatch):
        """CLI flag should override environment variable."""
        monkeypatch.setenv("PORT", "3000")
        from server import parse_args
        with patch.object(sys, "argv", ["server.py", "--port", "9090"]):
            args = parse_args()
        # CLI flag takes precedence
        assert args.port == 9090


class TestParseArgsInvalid:
    """Test behavior with invalid arguments."""

    def test_non_numeric_port_fails(self):
        """Non-numeric port should cause a parse error."""
        from server import parse_args
        with patch.object(sys, "argv", ["server.py", "--port", "not-a-number"]):
            with pytest.raises(SystemExit):
                parse_args()

    def test_unknown_flag_fails(self):
        """Unknown flag should cause a parse error."""
        from server import parse_args
        with patch.object(sys, "argv", ["server.py", "--unknown-flag"]):
            with pytest.raises(SystemExit):
                parse_args()
