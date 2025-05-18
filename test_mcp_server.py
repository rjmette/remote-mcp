#!/usr/bin/env python3
"""
Test script for MCP Memory server.
This script tests the MCP Memory server by storing and retrieving messages.

Usage:
    python test_mcp_server.py <server_url>

Example:
    python test_mcp_server.py http://54.242.99.144:8000
"""

import sys
import json
import time
import requests
import uuid


def test_memory_server(base_url):
    """Test the MCP Memory server by storing and retrieving messages."""
    print(f"Testing MCP Memory Server at: {base_url}")

    # Generate unique conversation ID for this test
    conversation_id = str(uuid.uuid4())
    print(f"Using conversation ID: {conversation_id}")

    # Test message
    test_message = {
        "role": "user",
        "content": "Test message from MCP client",
        "metadata": {"timestamp": time.time()},
    }

    # Step 1: Store a message
    print("\n=== Step 1: Storing a message ===")
    store_url = f"{base_url}/memory/{conversation_id}"
    print(f"POST {store_url}")
    print(f"Data: {json.dumps(test_message, indent=2)}")

    try:
        response = requests.post(store_url, json=test_message)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")

        if response.status_code != 200:
            print("❌ Failed to store message")
            return False
        print("✅ Message stored successfully")
    except Exception as e:
        print(f"❌ Error storing message: {e}")
        return False

    # Step 2: Retrieve the message
    print("\n=== Step 2: Retrieving messages ===")
    retrieve_url = f"{base_url}/memory/{conversation_id}"
    print(f"GET {retrieve_url}")

    try:
        response = requests.get(retrieve_url)
        print(f"Status: {response.status_code}")

        if response.status_code != 200:
            print("❌ Failed to retrieve messages")
            print(f"Response: {response.text}")
            return False

        messages = response.json()
        print(f"Retrieved {len(messages)} message(s)")
        print(f"Response: {json.dumps(messages, indent=2)}")

        # Verify the message was retrieved correctly
        if not messages or len(messages) == 0:
            print("❌ No messages were retrieved")
            return False

        if messages[0].get("content") == test_message["content"]:
            print("✅ Message content verified")
        else:
            print("❌ Message content does not match")
            return False
    except Exception as e:
        print(f"❌ Error retrieving messages: {e}")
        return False

    print("\n=== Test Completed Successfully ===")
    return True


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: python {sys.argv[0]} <server_url>")
        print(f"Example: python {sys.argv[0]} http://54.242.99.144:8000")
        sys.exit(1)

    server_url = sys.argv[1]
    if server_url.endswith("/"):
        server_url = server_url[:-1]  # Remove trailing slash

    success = test_memory_server(server_url)
    sys.exit(0 if success else 1)
