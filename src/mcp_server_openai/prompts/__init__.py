"""
Prompts package.

Exports:
- summarize (module)
- register_summarize (callable) for server bootstrap
"""

from . import summarize as summarize  # re-export the module for tests
from .summarize import register_summarize  # legacy hook expected by server

__all__ = ["summarize", "register_summarize"]
