"""
Tests for SSL certificate generation and HTTPS helper functions.

These tests use monkeypatching and temporary directories to avoid
touching the real certs/ directory or calling openssl.
"""

import os
from pathlib import Path
from unittest.mock import patch

import pytest


# ── Fixtures ──────────────────────────────────────────────────────────────

@pytest.fixture
def temp_certs_dir(tmp_path, monkeypatch):
    """Replace CERT_DIR/CERT_FILE/KEY_FILE with temp paths."""
    cert_dir = tmp_path / "certs"
    cert_file = cert_dir / "cert.pem"
    key_file = cert_dir / "key.pem"

    monkeypatch.setattr("server.CERT_DIR", cert_dir)
    monkeypatch.setattr("server.CERT_FILE", cert_file)
    monkeypatch.setattr("server.KEY_FILE", key_file)

    return {"dir": cert_dir, "cert": cert_file, "key": key_file}


# ── _ensure_cert_dir ──────────────────────────────────────────────────────

class TestEnsureCertDir:
    def test_creates_directory(self, temp_certs_dir, monkeypatch):
        """_ensure_cert_dir() should create the certs directory."""
        import server
        assert not temp_certs_dir["dir"].exists()
        server._ensure_cert_dir()
        assert temp_certs_dir["dir"].exists()
        assert temp_certs_dir["dir"].is_dir()

    def test_idempotent_when_exists(self, temp_certs_dir, monkeypatch):
        """_ensure_cert_dir() should not fail if directory already exists."""
        import server
        temp_certs_dir["dir"].mkdir(parents=True)
        server._ensure_cert_dir()  # should not raise


# ── _certs_exist ──────────────────────────────────────────────────────────

class TestCertsExist:
    def test_returns_false_when_missing(self, temp_certs_dir, monkeypatch):
        """_certs_exist() should return False if no cert files."""
        import server
        temp_certs_dir["dir"].mkdir(parents=True)
        assert server._certs_exist() is False

    def test_returns_true_when_both_exist(self, temp_certs_dir, monkeypatch):
        """_certs_exist() should return True when both cert and key exist."""
        import server
        temp_certs_dir["dir"].mkdir(parents=True)
        temp_certs_dir["cert"].write_text("fake-cert")
        temp_certs_dir["key"].write_text("fake-key")
        assert server._certs_exist() is True

    def test_returns_false_if_only_cert(self, temp_certs_dir, monkeypatch):
        """_certs_exist() should return False if key is missing."""
        import server
        temp_certs_dir["dir"].mkdir(parents=True)
        temp_certs_dir["cert"].write_text("fake-cert")
        assert server._certs_exist() is False

    def test_returns_false_if_only_key(self, temp_certs_dir, monkeypatch):
        """_certs_exist() should return False if cert is missing."""
        import server
        temp_certs_dir["dir"].mkdir(parents=True)
        temp_certs_dir["key"].write_text("fake-key")
        assert server._certs_exist() is False


# ── _generate_self_signed_cert ────────────────────────────────────────────

class TestGenerateSelfSignedCert:
    def test_returns_true_when_certs_exist(self, temp_certs_dir, monkeypatch):
        """Should return True immediately if certs already exist."""
        import server
        temp_certs_dir["dir"].mkdir(parents=True)
        temp_certs_dir["cert"].write_text("fake-cert")
        temp_certs_dir["key"].write_text("fake-key")
        assert server._generate_self_signed_cert() is True

    @patch("server.subprocess.run")
    def test_returns_true_on_success(self, mock_run, temp_certs_dir, monkeypatch):
        """Should return True when openssl succeeds."""
        import server
        mock_run.return_value.returncode = 0
        result = server._generate_self_signed_cert()
        assert result is True
        mock_run.assert_called_once()

    @patch("server.subprocess.run")
    def test_calls_openssl_with_correct_args(self, mock_run, temp_certs_dir, monkeypatch):
        """Should call openssl with the expected arguments."""
        import server
        mock_run.return_value.returncode = 0
        server._generate_self_signed_cert()
        args, kwargs = mock_run.call_args
        cmd = args[0]
        assert cmd[0] == "openssl"
        assert cmd[1] == "req"
        assert cmd[2] == "-x509"
        assert cmd[3] == "-newkey"
        assert cmd[4] == "rsa:2048"
        assert "-addext" in cmd

    @patch("server.subprocess.run")
    def test_returns_false_on_subprocess_error(self, mock_run, temp_certs_dir, monkeypatch):
        """Should return False when openssl fails."""
        import server
        from subprocess import CalledProcessError
        mock_run.side_effect = CalledProcessError(1, "openssl", stderr="error")
        result = server._generate_self_signed_cert()
        assert result is False

    @patch("server.subprocess.run")
    def test_returns_false_if_openssl_not_found(self, mock_run, temp_certs_dir, monkeypatch):
        """Should return False when openssl is not installed."""
        import server
        mock_run.side_effect = FileNotFoundError()
        result = server._generate_self_signed_cert()
        assert result is False

    def test_openssl_not_called_when_certs_exist(self, temp_certs_dir, monkeypatch):
        """Should not call openssl if certs already exist."""
        import server
        temp_certs_dir["dir"].mkdir(parents=True)
        temp_certs_dir["cert"].write_text("fake-cert")
        temp_certs_dir["key"].write_text("fake-key")

        with patch("server.subprocess.run") as mock_run:
            server._generate_self_signed_cert()
            mock_run.assert_not_called()


# ── _get_ssl_context ──────────────────────────────────────────────────────

class TestGetSSLContext:
    def test_returns_none_if_no_certs(self, temp_certs_dir, monkeypatch):
        """Should return None if certificate generation fails."""
        import server
        with patch("server._generate_self_signed_cert", return_value=False):
            ctx = server._get_ssl_context()
            assert ctx is None

    def test_returns_tuple_when_certs_exist(self, temp_certs_dir, monkeypatch):
        """Should return (cert_path, key_path) tuple when certs exist."""
        import server
        temp_certs_dir["dir"].mkdir(parents=True)
        temp_certs_dir["cert"].write_text("cert")
        temp_certs_dir["key"].write_text("key")

        ctx = server._get_ssl_context()
        assert ctx is not None
        assert isinstance(ctx, tuple)
        assert len(ctx) == 2
        assert str(temp_certs_dir["cert"]) in str(ctx[0])
        assert str(temp_certs_dir["key"]) in str(ctx[1])

    def test_returns_tuple_after_successful_gen(self, temp_certs_dir, monkeypatch):
        """Should return a tuple after successfully generating certs."""
        import server
        temp_certs_dir["dir"].mkdir(parents=True)
        temp_certs_dir["cert"].write_text("cert")
        temp_certs_dir["key"].write_text("key")

        with patch("server._generate_self_signed_cert", return_value=True) as mock_gen:
            ctx = server._get_ssl_context()
            assert ctx is not None
            assert isinstance(ctx, tuple)
            assert len(ctx) == 2
