#!/usr/bin/env python3
"""
Initialization script to create credentials.json and cookies.txt from environment variables.
This script should be run before starting the main application.
"""

import os
import json
import base64
import sys
from pathlib import Path


def create_credentials_file():
    """Create credentials.json from CREDENTIALS environment variable."""
    credentials_env = os.getenv("CREDENTIALS")

    if not credentials_env:
        print(
            "Warning: CREDENTIALS environment variable not set. Skipping credentials.json creation."
        )
        return False

    try:
        # Try to decode if it's base64 encoded
        try:
            credentials_json = base64.b64decode(credentials_env).decode("utf-8")
        except (ValueError, UnicodeDecodeError):
            # If base64 decode fails, assume it's already a JSON string
            credentials_json = credentials_env

        # Validate JSON format
        credentials_data = json.loads(credentials_json)

        # Write to credentials.json
        credentials_path = Path("/app/credentials.json")
        with open(credentials_path, "w", encoding="utf-8") as f:
            json.dump(credentials_data, f, indent=2)

        print(f"✓ Successfully created {credentials_path}")
        return True

    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in CREDENTIALS environment variable: {e}")
        return False
    except (IOError, OSError) as e:
        print(f"Error creating credentials.json: {e}")
        return False


def create_cookies_file():
    """Create cookies.txt from COOKIES environment variable."""
    cookies_env = os.getenv("COOKIES")

    if not cookies_env:
        print(
            "Warning: COOKIES environment variable not set. Skipping cookies.txt creation."
        )
        return False

    try:
        # Try to decode if it's base64 encoded
        try:
            cookies_content = base64.b64decode(cookies_env).decode("utf-8")
        except (ValueError, UnicodeDecodeError):
            # If base64 decode fails, assume it's already plain text
            cookies_content = cookies_env

        # Write to cookies.txt
        cookies_path = Path("/app/cookies.txt")
        with open(cookies_path, "w", encoding="utf-8") as f:
            f.write(cookies_content)

        print(f"✓ Successfully created {cookies_path}")
        return True

    except (IOError, OSError) as e:
        print(f"Error creating cookies.txt: {e}")
        return False


def main():
    """Main function to create both files."""
    print("🚀 Initializing environment files...")

    success_count = 0
    total_files = 2

    if create_credentials_file():
        success_count += 1

    if create_cookies_file():
        success_count += 1

    if success_count == 0:
        print("❌ No files were created. Please check your environment variables.")
        sys.exit(1)
    elif success_count < total_files:
        print(f"⚠️  Only {success_count}/{total_files} files were created successfully.")
        print("Some environment variables may be missing.")
    else:
        print(f"✅ All {success_count} files created successfully!")

    print("🎉 Environment initialization complete!")


if __name__ == "__main__":
    main()
