"""
PyPen MCP - Model Context Protocol server for browser-based pentesting.

This module provides MCP tools for LLM harnesses to interact with browsers
using PyDoll and Chrome DevTools Protocol (CDP) for security testing.

Features:
- Browser navigation and control
- Network monitoring and interception
- DOM extraction and manipulation
- JavaScript execution
- Cookie and session management
- Screenshots and debugging
- Captcha handling (Turnstile bypass + human intervention)
"""

__version__ = "0.1.0"

from .browser import browser_manager, BrowserManager
from .network import network_manager, NetworkManager
from .dom import dom_manager, DOMManager
from .javascript import js_manager, JSManager
from .session import session_manager, SessionManager
from .debug import debug_manager, DebugManager
from .captcha import captcha_manager, CaptchaManager, CaptchaType, HumanInterventionRequest

__all__ = [
    "browser_manager",
    "BrowserManager",
    "network_manager",
    "NetworkManager",
    "dom_manager",
    "DOMManager",
    "js_manager",
    "JSManager",
    "session_manager",
    "SessionManager",
    "debug_manager",
    "DebugManager",
    "captcha_manager",
    "CaptchaManager",
    "CaptchaType",
    "HumanInterventionRequest",
]
