#!/usr/bin/env python3
"""
Test script for the notification system.
Usage: python test_notification.py [title] [message]
"""
import sys
import os

# Set the config path
os.environ["MCP_CONFIG_PATH"] = os.path.join(os.path.dirname(__file__), "config.yaml")

# Add the project to path
sys.path.insert(0, os.path.dirname(__file__))

from src.mcp_server_openai.notifications import get_notifier


def main():
    title = sys.argv[1] if len(sys.argv) > 1 else "Test Notification"
    message = sys.argv[2] if len(sys.argv) > 2 else "Your notification system is working!"
    
    notifier = get_notifier()
    if notifier:
        notifier.notify(title, message)
        print(f"✅ Notification sent: {title}")
    else:
        print("❌ Notifications are disabled or not configured")


if __name__ == "__main__":
    main()