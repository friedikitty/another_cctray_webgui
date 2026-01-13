# -*- coding: utf-8 -*-
from flask import Flask, render_template, jsonify, request
import requests
import xml.etree.ElementTree as ET
import json
import os
import argparse
import socket
import sys
import re
from datetime import datetime
from util import sanitize_url, get_base_url

DEBUG = False

app = Flask(__name__)


# Load configuration
def load_config():
    config_path = "config.json5"
    if os.path.exists(config_path):
        import json5

        with open(config_path, "r", encoding="utf-8") as f:
            return json5.load(f)
    return {}


# Load user configuration (feeds)
def load_user_config():
    config_path = "config_user.json5"
    if os.path.exists(config_path):
        import json5

        with open(config_path, "r", encoding="utf-8") as f:
            return json5.load(f)
    return {}


# Initialize APPLICATION_ROOT from config.json
config = load_config()
APPLICATION_ROOT = config.get("application_root", "/")
if APPLICATION_ROOT != "/" and not APPLICATION_ROOT.endswith("/"):
    APPLICATION_ROOT = APPLICATION_ROOT + "/"
app.config["APPLICATION_ROOT"] = APPLICATION_ROOT


def fetch_cctray_feed(feed_url):
    """Fetch and parse CCTray XML feed"""
    try:
        response = requests.get(feed_url, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching CCTray feed: {e}")
        return None


def parse_cctray_xml(xml_content, feed_name, feed_url, main_url=""):
    """Parse CCTray XML and extract project information"""
    if not xml_content:
        return []

    try:
        root = ET.fromstring(xml_content)
        projects = []

        for project in root.findall("Project"):
            web_url = project.get("webUrl", "")
            sanitized_url = sanitize_url(web_url, feed_url, main_url) if web_url else ""

            # Debug logging
            project_name = project.get("name", "Unknown")
            if DEBUG:
                print(
                    f"Project: {project_name}, Original webUrl: {web_url}, Sanitized: {sanitized_url}"
                )

            # Use main_url for feed base URL if available, otherwise use feed_url base
            feed_base_url = (
                get_base_url(main_url) if main_url else get_base_url(feed_url)
            )

            project_data = {
                "name": project_name,
                "activity": project.get("activity", "Unknown"),
                "lastBuildStatus": project.get("lastBuildStatus", "Unknown"),
                "lastBuildLabel": project.get("lastBuildLabel", "N/A"),
                "lastBuildTime": project.get("lastBuildTime", "N/A"),
                "webUrl": sanitized_url,
                "category": project.get("category", ""),
                "feedName": feed_name,
                "feedBaseUrl": feed_base_url,
            }
            projects.append(project_data)

        return projects
    except ET.ParseError as e:
        print(f"Error parsing XML: {e}")
        return []


@app.route("/")
def index():
    """Main page displaying build status"""
    return render_template("index.html")


@app.route("/api/config")
def get_config():
    """API endpoint to get configuration"""
    config = load_config()
    colors = config.get(
        "colors",
        {
            "success": "#4CAF50",
            "failure": "#f44336",
            "exception": "#ff9800",
            "unknown": "#9e9e9e",
            "building": "#2196F3",
        },
    )

    # Create status mapping: color key -> CCTray status name
    # Map lowercase color keys to proper case status names used in CCTray XML
    # Standard CCTray statuses: Success, Failure, Exception, Unknown
    # Building is typically an activity, but we include it if present in colors
    status_mapping = {}
    color_to_status = {
        "success": "Success",
        "failure": "Failure",
        "exception": "Exception",
        "unknown": "Unknown",
        "building": "Building",  # May not be a standard status, but included if in config
    }

    for color_key in colors.keys():
        # Use predefined mapping, or capitalize if not in mapping
        status_name = color_to_status.get(color_key, color_key.capitalize())
        status_mapping[color_key] = status_name

    return jsonify(
        {
            "refresh_interval": config.get("refresh_interval", 5)
            * 1000,  # Convert to milliseconds
            "font_size": config.get("font_size", 14),
            "cards_per_row": config.get("cards_per_row", 4),
            "card_size": config.get(
                "card_size",
                {
                    "min_width": "200px",
                    "max_width": "320px",
                    "padding": "15px",
                    "gap": "15px",
                },
            ),
            "background_color": config.get("background_color", "#666666"),
            "header_background_image": config.get("header_background_image", ""),
            "header_text_color": config.get("header_text_color", "#333333"),
            "colors": colors,
            "status_mapping": status_mapping,  # Map color keys to CCTray status names
        }
    )


@app.route("/api/status")
def get_status():
    """API endpoint to get current build status from all feeds"""
    user_config = load_user_config()
    feeds = user_config.get("feeds", [])

    if not feeds:
        return (
            jsonify(
                {
                    "error": "No CCTray feeds configured",
                    "projects": [],
                    "timestamp": datetime.now().isoformat(),
                }
            ),
            400,
        )

    all_projects = []
    feed_errors = []

    for feed in feeds:
        feed_name = feed.get("name", "Unknown Feed")
        feed_url = feed.get("url", "")
        main_url = feed.get("main_url", "")

        if not feed_url:
            feed_errors.append(f"Feed '{feed_name}' has no URL configured")
            continue

        try:
            xml_content = fetch_cctray_feed(feed_url)
            if xml_content:
                projects = parse_cctray_xml(xml_content, feed_name, feed_url, main_url)

                # Apply filter_regex if specified
                filter_regex = feed.get("filter_regex", "")
                if filter_regex:
                    try:
                        pattern = re.compile(filter_regex)
                        filtered_projects = [
                            p for p in projects if not pattern.search(p.get("name", ""))
                        ]
                        projects = filtered_projects
                    except re.error as e:
                        feed_errors.append(
                            f"Invalid filter_regex for feed '{feed_name}': {str(e)}"
                        )
                        # Continue with unfiltered projects if regex is invalid

                all_projects.extend(projects)
            else:
                feed_errors.append(f"Failed to fetch feed '{feed_name}'")
        except Exception as e:
            feed_errors.append(f"Error processing feed '{feed_name}': {str(e)}")

    return jsonify(
        {
            "projects": all_projects,
            "timestamp": datetime.now().isoformat(),
            "errors": feed_errors if feed_errors else None,
        }
    )


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
    parser = argparse.ArgumentParser(description="CCTray Build Status Monitor")
    # parser.add_argument('--debug', action='store_true', help='Enable debug mode with auto-reload (default: enabled)')
    parser.add_argument(
        "--no-debug", action="store_true", help="Disable debug mode (for production)"
    )
    args = parser.parse_args()

    config = load_config()
    port = config.get("port", 5000)
    host = "0.0.0.0"

    # Check if port is available (skip check in debug mode with reloader as it will bind twice)
    if args.no_debug and not is_port_available(host, port):
        print(f"ERROR: Port {port} is already in use on {host}")
        print(
            f"Please stop the other application using this port or change the port in config.json"
        )
        sys.exit(1)

    # Enable debug mode by default unless explicitly disabled
    if args.no_debug:
        debug_mode = False
    else:
        debug_mode = True  # Default to True for easier development

    app.run(debug=debug_mode, use_reloader=debug_mode, host=host, port=port)
