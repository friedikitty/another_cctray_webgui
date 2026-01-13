# -*- coding: utf-8 -*-
"""
Utility functions for CCTray Build Status Monitor
"""
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode


def sanitize_url(url, feed_url, main_url=""):
    """
    Sanitize URL by removing credentials and replacing localhost/127.0.0.1 with feed host

    Args:
        url: The URL to sanitize (e.g., project webUrl from CCTray XML)
        feed_url: The feed URL to extract the host from for localhost replacement
        main_url: Optional main URL to use for localhost replacement (takes priority)

    Returns:
        Sanitized URL string with credentials and tokens removed

    Examples:
        >>> sanitize_url("http://user:pass@example.com/build", "http://ci.example.com")
        "http://example.com/build"

        >>> sanitize_url("http://localhost:8080/build", "http://ci.example.com:8111/feed")
        "http://ci.example.com:8111/build"

        >>> sanitize_url("http://localhost:8080/build", "http://ci.example.com:8111/feed", "http://main.example.com:9000")
        "http://main.example.com:9000/build"
    """
    if not url:
        return ""

    try:
        parsed = urlparse(url)
        # Use main_url for localhost replacement if provided, otherwise use feed_url
        replacement_url = main_url if main_url else feed_url
        feed_parsed = urlparse(replacement_url)

        # Remove username, password, and token from URL
        # Reconstruct netloc without credentials
        netloc = parsed.hostname
        if parsed.port:
            netloc = f"{netloc}:{parsed.port}"

        # Replace localhost or 127.0.0.1 with feed host
        if parsed.hostname in ["localhost", "127.0.0.1"]:
            netloc = feed_parsed.hostname
            if feed_parsed.port:
                netloc = f"{netloc}:{feed_parsed.port}"

        # Remove any tokens from query parameters
        query_params = parse_qs(parsed.query)
        # Remove common token parameter names
        token_keys = ["token", "access_token", "auth_token", "api_key", "apikey", "key"]
        for key in token_keys:
            query_params.pop(key, None)

        # Reconstruct query string
        query_string = urlencode(query_params, doseq=True)

        # Reconstruct URL
        sanitized = urlunparse(
            (
                parsed.scheme,
                netloc,
                parsed.path,
                parsed.params,
                query_string,
                parsed.fragment,
            )
        )

        return sanitized
    except Exception as e:
        # Don't print the URL as it may contain credentials
        print(f"Error sanitizing URL: {e}")
        return url


def get_base_url(url):
    """
    Extract base URL (scheme://hostname:port) from a full URL, removing credentials and path

    Args:
        url: The full URL to extract base from

    Returns:
        Base URL string (scheme://hostname:port) or empty string if invalid

    Examples:
        >>> get_base_url("http://user:pass@example.com:8111/path/to/resource")
        "http://example.com:8111"

        >>> get_base_url("https://localhost:8080")
        "https://localhost:8080"
    """
    if not url:
        return ""

    try:
        parsed = urlparse(url)

        # Remove credentials from netloc
        netloc = parsed.hostname
        if parsed.port:
            netloc = f"{netloc}:{parsed.port}"

        # Reconstruct base URL (scheme://hostname:port only)
        base_url = urlunparse(
            (
                parsed.scheme,
                netloc,
                "",  # No path
                "",  # No params
                "",  # No query
                "",  # No fragment
            )
        )

        return base_url
    except Exception as e:
        print(f"Error extracting base URL: {e}")
        return ""
