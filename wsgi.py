# -*- coding: utf-8 -*-
"""
WSGI server entry point for production deployment.
Uses Waitress, a production WSGI server that works on Windows.
"""
from waitress import serve
from app import app
import os
import json
import socket
import sys


def load_config():
    """Load configuration from config.json5"""
    config_path = "config.json5"
    if os.path.exists(config_path):
        import json5

        with open(config_path, "r", encoding="utf-8") as f:
            return json5.load(f)
    return {}


def is_port_available(host, port):
    """Check if a port is available"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            s.bind((host, port))
            return True
    except OSError:
        return False


if __name__ == "__main__":
    config = load_config()
    port = config.get("port", 5000)
    host = config.get("host", "127.0.0.1")
    threads = config.get("threads", 4)

    # Check if port is available
    if not is_port_available(host, port):
        print(f"ERROR: Port {port} is already in use on {host}")
        print(
            f"Please stop the other application using this port or change the port in config.json5"
        )
        sys.exit(1)

    print(f"Starting Waitress WSGI server on {host}:{port}")
    print(f"Threads: {threads}")
    print("Press Ctrl+C to stop the server")

    serve(
        app,
        host=host,
        port=port,
        threads=threads,
        channel_timeout=120,
        cleanup_interval=30,
        asyncore_use_poll=True,
    )
