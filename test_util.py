# -*- coding: utf-8 -*-
"""
Unit tests for utility functions
"""
import unittest
from util import sanitize_url, get_base_url


class TestSanitizeUrl(unittest.TestCase):
    """Test cases for sanitize_url function"""

    def test_empty_url(self):
        """Test with empty URL"""
        result = sanitize_url("", "http://ci.example.com")
        self.assertEqual(result, "")

    def test_remove_username_password(self):
        """Test removal of username and password from URL"""
        result = sanitize_url(
            "http://user:password@ci.example.com:8111/build/123",
            "http://ci.example.com:8111/feed",
        )
        self.assertEqual(result, "http://ci.example.com:8111/build/123")

    def test_replace_localhost_with_feed_host(self):
        """Test replacing localhost with feed host"""
        result = sanitize_url(
            "http://localhost:8080/build/123", "http://ci.example.com:8111/feed"
        )
        self.assertEqual(result, "http://ci.example.com:8111/build/123")

    def test_replace_127_0_0_1_with_feed_host(self):
        """Test replacing 127.0.0.1 with feed host"""
        result = sanitize_url(
            "http://127.0.0.1:8080/build/123", "http://ci.example.com:8111/feed"
        )
        self.assertEqual(result, "http://ci.example.com:8111/build/123")

    def test_remove_token_from_query_params(self):
        """Test removal of token from query parameters"""
        result = sanitize_url(
            "http://ci.example.com/build?token=secret123&buildId=456",
            "http://ci.example.com/feed",
        )
        self.assertEqual(result, "http://ci.example.com/build?buildId=456")

    def test_remove_access_token_from_query_params(self):
        """Test removal of access_token from query parameters"""
        result = sanitize_url(
            "http://ci.example.com/build?access_token=secret&id=1",
            "http://ci.example.com/feed",
        )
        self.assertEqual(result, "http://ci.example.com/build?id=1")

    def test_remove_api_key_from_query_params(self):
        """Test removal of api_key from query parameters"""
        result = sanitize_url(
            "http://ci.example.com/build?api_key=secret&project=test",
            "http://ci.example.com/feed",
        )
        self.assertEqual(result, "http://ci.example.com/build?project=test")

    def test_complex_url_sanitization(self):
        """Test complex URL with credentials, localhost, and token"""
        result = sanitize_url(
            "http://user:pass@localhost:8080/build/123?token=abc&project=test",
            "http://ci.example.com:8111/feed",
        )
        self.assertEqual(result, "http://ci.example.com:8111/build/123?project=test")

    def test_url_without_port(self):
        """Test URL without port number"""
        result = sanitize_url(
            "http://user:pass@ci.example.com/build/123", "http://ci.example.com/feed"
        )
        self.assertEqual(result, "http://ci.example.com/build/123")

    def test_https_url(self):
        """Test HTTPS URL"""
        result = sanitize_url(
            "https://user:pass@ci.example.com/build", "https://ci.example.com/feed"
        )
        self.assertEqual(result, "https://ci.example.com/build")

    def test_url_with_fragment(self):
        """Test URL with fragment"""
        result = sanitize_url(
            "http://ci.example.com/build#section", "http://ci.example.com/feed"
        )
        self.assertEqual(result, "http://ci.example.com/build#section")

    def test_normal_url_unchanged(self):
        """Test that normal URL without credentials/tokens remains unchanged"""
        result = sanitize_url(
            "http://ci.example.com:8111/build/123?project=test",
            "http://ci.example.com:8111/feed",
        )
        self.assertEqual(result, "http://ci.example.com:8111/build/123?project=test")

    def test_localhost_without_port(self):
        """Test localhost replacement when feed has no port"""
        result = sanitize_url("http://localhost/build", "http://ci.example.com/feed")
        self.assertEqual(result, "http://ci.example.com/build")

    def test_feed_url_without_port_localhost_with_port(self):
        """Test localhost with port when feed has no port"""
        result = sanitize_url(
            "http://localhost:8080/build", "http://ci.example.com/feed"
        )
        self.assertEqual(result, "http://ci.example.com/build")

    def test_localhost_with_main_url(self):
        """Test localhost replacement using main_url (priority over feed_url)"""
        result = sanitize_url(
            "http://localhost:8080/build/123",
            "http://feed.example.com:8111/feed",
            "http://main.example.com:9000",
        )
        self.assertEqual(result, "http://main.example.com:9000/build/123")

    def test_127_0_0_1_with_main_url(self):
        """Test 127.0.0.1 replacement using main_url (priority over feed_url)"""
        result = sanitize_url(
            "http://127.0.0.1:8080/build/123",
            "http://feed.example.com:8111/feed",
            "http://main.example.com:9000",
        )
        self.assertEqual(result, "http://main.example.com:9000/build/123")

    def test_localhost_with_empty_main_url(self):
        """Test localhost replacement falls back to feed_url when main_url is empty"""
        result = sanitize_url(
            "http://localhost:8080/build/123",
            "http://feed.example.com:8111/feed",
            "",
        )
        self.assertEqual(result, "http://feed.example.com:8111/build/123")


class TestGetBaseUrl(unittest.TestCase):
    """Test cases for get_base_url function"""

    def test_empty_url(self):
        """Test with empty URL"""
        result = get_base_url("")
        self.assertEqual(result, "")

    def test_simple_url(self):
        """Test simple URL without credentials"""
        result = get_base_url("http://example.com:8111/path/to/resource")
        self.assertEqual(result, "http://example.com:8111")

    def test_url_with_credentials(self):
        """Test URL with username and password"""
        result = get_base_url("http://user:password@example.com:8111/path")
        self.assertEqual(result, "http://example.com:8111")

    def test_url_without_port(self):
        """Test URL without port number"""
        result = get_base_url("http://example.com/path/to/resource")
        self.assertEqual(result, "http://example.com")

    def test_https_url(self):
        """Test HTTPS URL"""
        result = get_base_url("https://user:pass@ci.example.com:443/path")
        self.assertEqual(result, "https://ci.example.com:443")

    def test_url_with_query_params(self):
        """Test URL with query parameters"""
        result = get_base_url("http://example.com:8111/path?param=value&other=test")
        self.assertEqual(result, "http://example.com:8111")

    def test_url_with_fragment(self):
        """Test URL with fragment"""
        result = get_base_url("http://example.com:8111/path#section")
        self.assertEqual(result, "http://example.com:8111")

    def test_url_with_path_only(self):
        """Test URL with just path"""
        result = get_base_url(
            "http://example.com:8111/httpAuth/app/rest/cctray/projects.xml"
        )
        self.assertEqual(result, "http://example.com:8111")

    def test_complex_url(self):
        """Test complex URL with credentials, path, query, and fragment"""
        result = get_base_url(
            "http://user:pass@example.com:8111/path/to/resource?token=abc&id=123#section"
        )
        self.assertEqual(result, "http://example.com:8111")

    def test_localhost_url(self):
        """Test localhost URL"""
        result = get_base_url("http://localhost:8080/path")
        self.assertEqual(result, "http://localhost:8080")

    def test_ip_address_url(self):
        """Test URL with IP address"""
        result = get_base_url(
            "http://10.226.181.2:8111/httpAuth/app/rest/cctray/projects.xml"
        )
        self.assertEqual(result, "http://10.226.181.2:8111")

    def test_url_with_credentials_and_ip(self):
        """Test URL with credentials and IP address"""
        result = get_base_url(
            "http://simple_viewer:simple_viewer@10.226.181.2:8111/httpAuth/app/rest/cctray/projects.xml"
        )
        self.assertEqual(result, "http://10.226.181.2:8111")

    def test_url_without_scheme(self):
        """Test URL without scheme (should handle gracefully)"""
        # urlparse treats // as a network location, returns it as-is
        result = get_base_url("//example.com:8111/path")
        self.assertEqual(result, "//example.com:8111")

    def test_invalid_url(self):
        """Test invalid URL format"""
        # Invalid URLs should return empty string or handle gracefully
        result = get_base_url("not-a-valid-url")
        # urlparse will still parse it but scheme will be empty
        self.assertIsInstance(result, str)


if __name__ == "__main__":
    unittest.main()
