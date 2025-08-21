from __future__ import annotations

import platform
import subprocess
from typing import Protocol

from .config import get_notification_config


class Notifier(Protocol):
    """Protocol for a notification provider."""

    def notify(self, title: str, message: str) -> None:
        """Send a notification."""
        ...


class CommandNotifier:
    """Sends notifications by running a shell command."""

    def __init__(self, command_template: str):
        if not command_template:
            raise ValueError("Command template cannot be empty.")
        self.command_template = command_template

    def notify(self, title: str, message: str) -> None:
        """Send a notification using the configured command."""
        command = self.command_template.format(title=title, message=message)
        try:
            subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"Error sending notification: {e}")


def get_notifier() -> Notifier | None:
    """
    Get the configured notifier based on the platform.
    """
    config = get_notification_config()
    if not config or not config.get("enabled"):
        return None

    system = platform.system()
    command = config.get(f"command_{system.lower()}")

    if command:
        return CommandNotifier(command)

    return None
