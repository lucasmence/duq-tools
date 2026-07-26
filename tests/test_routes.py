"""
Tests for all HTTP routes in the duq-tools Flask server.
"""

import pytest


class TestHomepage:
    def test_homepage_returns_200(self, client):
        """GET / should return 200."""
        resp = client.get("/")
        assert resp.status_code == 200

    def test_homepage_is_html(self, client):
        """GET / should have HTML content type."""
        resp = client.get("/")
        assert resp.content_type.startswith("text/html")

    def test_homepage_contains_tool_names(self, client):
        """GET / should contain all three tool names."""
        resp = client.get("/")
        html = resp.data.decode("utf-8")
        assert "Sprite Editor" in html
        assert "Sprite Fusion" in html
        assert "Trigger Editor" in html

    def test_homepage_contains_duq_title(self, client):
        """GET / should contain the page title."""
        resp = client.get("/")
        html = resp.data.decode("utf-8")
        assert "duq-tools" in html
        assert "Game Dev Toolkit" in html

    def test_homepage_contains_links_to_tools(self, client):
        """GET / should contain links to each tool."""
        resp = client.get("/")
        html = resp.data.decode("utf-8")
        assert "/sprite-editor" in html
        assert "/sprite-fusion" in html
        assert "/trigger-editor" in html


class TestToolRoutes:
    @pytest.mark.parametrize("path", [
        "/sprite-editor/",
        "/sprite-fusion/",
        "/trigger-editor/",
    ])
    def test_tool_homepages_return_200(self, client, path):
        """GET each tool's root should return 200."""
        resp = client.get(path)
        assert resp.status_code == 200, f"{path} returned {resp.status_code}"

    @pytest.mark.parametrize("path", [
        "/sprite-editor/",
        "/sprite-fusion/",
        "/trigger-editor/",
    ])
    def test_tool_homepages_are_html(self, client, path):
        """GET each tool's root should serve HTML."""
        resp = client.get(path)
        assert resp.content_type.startswith("text/html"), f"{path} is {resp.content_type}"

    @pytest.mark.parametrize("path,expected_bytes", [
        ("/sprite-editor/", b"Duq Sprite Editor"),
        ("/sprite-fusion/", b"Duq Sprite Fusion"),
        ("/trigger-editor/", b"Duq Trigger Editor"),
    ])
    def test_tool_homepage_identifies_itself(self, client, path, expected_bytes):
        """Each tool's homepage should contain its name."""
        resp = client.get(path)
        assert expected_bytes in resp.data, f"{path} missing {expected_bytes}"


class TestStaticFiles:
    @pytest.mark.parametrize("path,content_type", [
        ("/static/persist.js", "text/javascript"),
    ])
    def test_static_files_return_200(self, client, path, content_type):
        """Shared static files should be served correctly."""
        resp = client.get(path)
        assert resp.status_code == 200, f"{path} returned {resp.status_code}"
        assert resp.content_type.startswith(content_type), \
            f"{path} is {resp.content_type}, expected {content_type}"

    def test_persist_js_contains_duq_persist(self, client):
        """persist.js should expose window.duqPersist."""
        resp = client.get("/static/persist.js")
        assert b"duqPersist" in resp.data

    def test_persist_js_contains_helpers(self, client):
        """persist.js should have save/load/remove/debounce functions."""
        resp = client.get("/static/persist.js")
        data = resp.data.decode("utf-8")
        assert "function save" in data or "save:" in data
        assert "function load" in data or "load:" in data
        assert "function debounce" in data or "debounce:" in data


class TestToolStaticAssets:
    """Tests for static assets served from each tool's directory."""

    @pytest.mark.parametrize("path", [
        "/sprite-editor/js/app.js",
        "/sprite-editor/css/styles.css",
        "/sprite-editor/icon.png",
        "/sprite-fusion/script.js",
        "/sprite-fusion/styles.css",
        "/sprite-fusion/icon.png",
        "/trigger-editor/icon.png",
    ])
    def test_tool_assets_return_200(self, client, path):
        """Each tool's static assets should be served."""
        resp = client.get(path)
        assert resp.status_code == 200, f"{path} returned {resp.status_code}"

    @pytest.mark.parametrize("path,expected", [
        ("/sprite-editor/js/app.js", b"Duq Sprite Manager"),
        ("/sprite-editor/css/styles.css", b"--bg-primary"),
        ("/sprite-fusion/script.js", b"formatFileSize"),
        ("/sprite-fusion/styles.css", b"--bg-primary"),
    ])
    def test_tool_assets_contain_expected_content(self, client, path, expected):
        """Each tool's static assets should contain expected identifiers."""
        resp = client.get(path)
        assert expected in resp.data, f"{path} missing expected content"


class TestFavicon:
    def test_favicon_returns_200(self, client):
        """GET /favicon.ico should return 200."""
        resp = client.get("/favicon.ico")
        assert resp.status_code == 200

    def test_favicon_is_png(self, client):
        """Favicon should be a PNG image."""
        resp = client.get("/favicon.ico")
        # PNG magic bytes
        assert resp.data[:4] == b'\x89PNG', "Not a PNG file"


class Test404:
    @pytest.mark.parametrize("path", [
        "/nonexistent",
        "/nonexistent/",
        "/sprite-editor/nonexistent.js",
        "/sprite-fusion/missing.css",
        "/trigger-editor/missing.js",
    ])
    def test_nonexistent_returns_404(self, client, path):
        """Requests to non-existent paths should return 404."""
        resp = client.get(path)
        assert resp.status_code == 404, f"{path} returned {resp.status_code}"


class TestHeaders:
    def test_response_has_content_type(self, client):
        """Response should have correct content-type header."""
        resp = client.get("/")
        assert resp.headers.get("Content-Type") == "text/html; charset=utf-8"

    def test_content_type_html(self, client):
        """Homepage should be served as HTML."""
        resp = client.get("/")
        assert resp.content_type == "text/html; charset=utf-8"
