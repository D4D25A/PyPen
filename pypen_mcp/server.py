"""
PyPen MCP Server - Model Context Protocol server for browser-based pentesting.

This module provides MCP tools for LLM harnesses to interact with browsers
using PyDoll and Chrome DevTools Protocol (CDP) for security testing.
"""

import asyncio
import json
from typing import Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .browser import browser_manager
from .network import network_manager
from .dom import dom_manager
from .javascript import js_manager
from .session import session_manager
from .debug import debug_manager
from .captcha import captcha_manager

# Create MCP server instance
app = Server("pypen-mcp")


# ============================================================================
# BROWSER MANAGEMENT TOOLS
# ============================================================================

@app.list_tools()
async def list_tools():
    """List all available MCP tools."""
    return [
        # Browser Management
        Tool(
            name="browser_launch",
            description="Launch a new browser instance with optional configuration (headless, proxy, user agent, etc.)",
            inputSchema={
                "type": "object",
                "properties": {
                    "headless": {"type": "boolean", "description": "Run in headless mode", "default": False},
                    "proxy": {"type": "string", "description": "Proxy server URL (e.g., socks5://127.0.0.1:9050)"},
                    "user_agent": {"type": "string", "description": "Custom user agent string"},
                    "binary_location": {"type": "string", "description": "Path to Chrome binary"},
                    "window_size": {"type": "array", "items": {"type": "integer"}, "description": "Window size [width, height]"},
                    "incognito": {"type": "boolean", "description": "Run in incognito mode", "default": False},
                    "disable_images": {"type": "boolean", "description": "Disable image loading", "default": False},
                    "arguments": {"type": "array", "items": {"type": "string"}, "description": "Additional browser arguments"},
                },
            },
        ),
        Tool(
            name="browser_close",
            description="Close the browser instance",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="browser_navigate",
            description="Navigate to a URL",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "URL to navigate to"},
                },
                "required": ["url"],
            },
        ),
        Tool(
            name="browser_go_back",
            description="Navigate back in browser history",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="browser_go_forward",
            description="Navigate forward in browser history",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="browser_refresh",
            description="Refresh the current page",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="browser_get_info",
            description="Get information about the current page (URL, title)",
            inputSchema={"type": "object", "properties": {}},
        ),
        
        # Network Monitoring
        Tool(
            name="network_enable_monitoring",
            description="Enable network event monitoring to capture all HTTP traffic",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="network_disable_monitoring",
            description="Disable network event monitoring",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="network_get_logs",
            description="Get captured network logs, optionally filtered by URL pattern",
            inputSchema={
                "type": "object",
                "properties": {
                    "filter_url": {"type": "string", "description": "URL pattern to filter logs"},
                },
            },
        ),
        Tool(
            name="network_get_response_body",
            description="Get the response body for a specific request ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "request_id": {"type": "string", "description": "Request ID from network logs"},
                },
                "required": ["request_id"],
            },
        ),
        
        # Network Interception
        Tool(
            name="network_enable_interception",
            description="Enable request/response interception",
            inputSchema={
                "type": "object",
                "properties": {
                    "resource_type": {"type": "string", "description": "Resource type to intercept (Image, Script, XHR, etc.)"},
                    "request_stage": {"type": "string", "description": "Stage to intercept at (Request or Response)", "default": "Request"},
                },
            },
        ),
        Tool(
            name="network_disable_interception",
            description="Disable request interception",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="network_setup_handler",
            description="Set up automatic interception handler with blocking, modification, and mocking rules",
            inputSchema={
                "type": "object",
                "properties": {
                    "block_patterns": {"type": "array", "items": {"type": "string"}, "description": "URL patterns to block"},
                    "modify_headers": {"type": "object", "description": "Headers to add/modify for all requests"},
                    "mock_responses": {"type": "object", "description": "URL patterns and mock response data"},
                },
            },
        ),
        
        # DOM Operations
        Tool(
            name="dom_find_element",
            description="Find an element on the page using various selectors",
            inputSchema={
                "type": "object",
                "properties": {
                    "tag_name": {"type": "string", "description": "HTML tag name"},
                    "id": {"type": "string", "description": "Element ID"},
                    "class_name": {"type": "string", "description": "CSS class name"},
                    "name": {"type": "string", "description": "Name attribute"},
                    "text": {"type": "string", "description": "Text content to match"},
                    "css_selector": {"type": "string", "description": "CSS selector"},
                    "xpath": {"type": "string", "description": "XPath expression"},
                    "timeout": {"type": "integer", "description": "Timeout in seconds", "default": 10},
                },
            },
        ),
        Tool(
            name="dom_find_elements",
            description="Find multiple elements on the page",
            inputSchema={
                "type": "object",
                "properties": {
                    "tag_name": {"type": "string", "description": "HTML tag name"},
                    "class_name": {"type": "string", "description": "CSS class name"},
                    "css_selector": {"type": "string", "description": "CSS selector"},
                    "xpath": {"type": "string", "description": "XPath expression"},
                    "timeout": {"type": "integer", "description": "Timeout in seconds", "default": 10},
                },
            },
        ),
        Tool(
            name="dom_get_text",
            description="Get the text content of an element",
            inputSchema={
                "type": "object",
                "properties": {
                    "selector": {"type": "string", "description": "CSS selector or XPath"},
                    "timeout": {"type": "integer", "description": "Timeout in seconds", "default": 10},
                },
                "required": ["selector"],
            },
        ),
        Tool(
            name="dom_get_html",
            description="Get the outer HTML of an element",
            inputSchema={
                "type": "object",
                "properties": {
                    "selector": {"type": "string", "description": "CSS selector or XPath"},
                    "timeout": {"type": "integer", "description": "Timeout in seconds", "default": 10},
                },
                "required": ["selector"],
            },
        ),
        Tool(
            name="dom_click",
            description="Click on an element",
            inputSchema={
                "type": "object",
                "properties": {
                    "selector": {"type": "string", "description": "CSS selector or XPath"},
                    "timeout": {"type": "integer", "description": "Timeout in seconds", "default": 10},
                },
                "required": ["selector"],
            },
        ),
        Tool(
            name="dom_type",
            description="Type text into an input element",
            inputSchema={
                "type": "object",
                "properties": {
                    "selector": {"type": "string", "description": "CSS selector or XPath"},
                    "text": {"type": "string", "description": "Text to type"},
                    "clear_first": {"type": "boolean", "description": "Clear input before typing", "default": False},
                    "timeout": {"type": "integer", "description": "Timeout in seconds", "default": 10},
                },
                "required": ["selector", "text"],
            },
        ),
        Tool(
            name="dom_scroll",
            description="Scroll the page",
            inputSchema={
                "type": "object",
                "properties": {
                    "direction": {"type": "string", "description": "Scroll direction (down, up, bottom, top)", "default": "down"},
                    "amount": {"type": "integer", "description": "Pixels to scroll", "default": 500},
                },
            },
        ),
        Tool(
            name="dom_get_source",
            description="Get the full page HTML source",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="dom_wait_for",
            description="Wait for an element to appear on the page",
            inputSchema={
                "type": "object",
                "properties": {
                    "selector": {"type": "string", "description": "CSS selector or XPath"},
                    "timeout": {"type": "integer", "description": "Timeout in seconds", "default": 30},
                },
                "required": ["selector"],
            },
        ),
        
        # JavaScript Execution
        Tool(
            name="js_execute",
            description="Execute JavaScript in the browser context",
            inputSchema={
                "type": "object",
                "properties": {
                    "script": {"type": "string", "description": "JavaScript code to execute"},
                },
                "required": ["script"],
            },
        ),
        Tool(
            name="js_get_console_logs",
            description="Get console logs from the browser",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="js_get_global_vars",
            description="Extract global JavaScript variables",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="js_get_local_storage",
            description="Get all localStorage data",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="js_get_session_storage",
            description="Get all sessionStorage data",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="js_set_local_storage",
            description="Set a localStorage value",
            inputSchema={
                "type": "object",
                "properties": {
                    "key": {"type": "string", "description": "Storage key"},
                    "value": {"type": "string", "description": "Storage value"},
                },
                "required": ["key", "value"],
            },
        ),
        Tool(
            name="js_get_forms",
            description="Get all forms on the page with their inputs",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="js_get_links",
            description="Get all links on the page",
            inputSchema={"type": "object", "properties": {}},
        ),
        
        # Cookie & Session Management
        Tool(
            name="session_get_cookies",
            description="Get all cookies from the browser",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="session_get_cookie",
            description="Get a specific cookie by name",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Cookie name"},
                },
                "required": ["name"],
            },
        ),
        Tool(
            name="session_set_cookie",
            description="Set a cookie in the browser",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Cookie name"},
                    "value": {"type": "string", "description": "Cookie value"},
                    "domain": {"type": "string", "description": "Cookie domain"},
                    "path": {"type": "string", "description": "Cookie path", "default": "/"},
                    "secure": {"type": "boolean", "description": "Secure flag", "default": False},
                    "http_only": {"type": "boolean", "description": "HttpOnly flag", "default": False},
                },
                "required": ["name", "value"],
            },
        ),
        Tool(
            name="session_delete_cookie",
            description="Delete a cookie by name",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Cookie name"},
                    "domain": {"type": "string", "description": "Cookie domain"},
                },
                "required": ["name"],
            },
        ),
        Tool(
            name="session_clear_cookies",
            description="Clear all cookies",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="session_export_cookies",
            description="Export cookies in various formats (json, netscape, header)",
            inputSchema={
                "type": "object",
                "properties": {
                    "format": {"type": "string", "description": "Export format (json, netscape, header)", "default": "json"},
                },
            },
        ),
        Tool(
            name="session_import_cookies",
            description="Import cookies from JSON string",
            inputSchema={
                "type": "object",
                "properties": {
                    "cookies_json": {"type": "string", "description": "JSON array of cookies"},
                },
                "required": ["cookies_json"],
            },
        ),
        Tool(
            name="session_make_request",
            description="Make an HTTP request using the browser's session (inherits cookies/auth)",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "Request URL"},
                    "method": {"type": "string", "description": "HTTP method", "default": "GET"},
                    "headers": {"type": "object", "description": "Request headers"},
                    "body": {"type": "string", "description": "Request body"},
                    "params": {"type": "object", "description": "Query parameters"},
                },
                "required": ["url"],
            },
        ),
        
        # Screenshot & Debugging
        Tool(
            name="debug_screenshot",
            description="Take a screenshot of the current page",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File path to save screenshot"},
                    "full_page": {"type": "boolean", "description": "Capture full page", "default": False},
                    "as_base64": {"type": "boolean", "description": "Return as base64 string", "default": False},
                },
            },
        ),
        Tool(
            name="debug_get_viewport",
            description="Get the current viewport size",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="debug_set_viewport",
            description="Set the viewport size",
            inputSchema={
                "type": "object",
                "properties": {
                    "width": {"type": "integer", "description": "Viewport width"},
                    "height": {"type": "integer", "description": "Viewport height"},
                },
                "required": ["width", "height"],
            },
        ),
        Tool(
            name="debug_get_performance",
            description="Get performance metrics from the page",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="debug_highlight",
            description="Highlight all elements matching a selector",
            inputSchema={
                "type": "object",
                "properties": {
                    "selector": {"type": "string", "description": "CSS selector"},
                    "color": {"type": "string", "description": "Highlight color", "default": "red"},
                },
                "required": ["selector"],
            },
        ),
        
        # Captcha Handling
        Tool(
            name="captcha_enable_turnstile_bypass",
            description="Enable automatic Cloudflare Turnstile bypass. Uses PyDoll's built-in mechanism to detect and click the Turnstile checkbox. Success depends on IP reputation and browser fingerprint - this is NOT a magic bypass. Use residential proxies for best results.",
            inputSchema={
                "type": "object",
                "properties": {
                    "time_to_wait_captcha": {"type": "number", "description": "Seconds to wait for captcha to appear (default: 5.0)", "default": 5.0},
                },
            },
        ),
        Tool(
            name="captcha_disable_turnstile_bypass",
            description="Disable automatic Turnstile bypass",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="captcha_detect_type",
            description="Detect what type of captcha is present on the current page. Scans for Cloudflare Turnstile, reCAPTCHA, hCaptcha, and image challenge indicators.",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="captcha_handle_auto",
            description="Attempt to automatically handle any detected captcha. For Turnstile: uses built-in bypass. For others (ReCAPTCHA v2, hCaptcha, image challenges): returns need for human intervention.",
            inputSchema={
                "type": "object",
                "properties": {
                    "timeout": {"type": "number", "description": "Timeout in seconds for automatic handling (default: 30.0)", "default": 30.0},
                },
            },
        ),
        Tool(
            name="captcha_request_human_intervention",
            description="Request human intervention for an unsolvable captcha (e.g., ReCAPTCHA v2 image challenges, hCaptcha puzzles). Creates an intervention request with screenshot. The automation should wait for human to solve.",
            inputSchema={
                "type": "object",
                "properties": {
                    "captcha_type": {"type": "string", "description": "Type of captcha: turnstile, recaptcha_v2, recaptcha_v3, hcaptcha, image_challenge, puzzle, or unknown"},
                    "message": {"type": "string", "description": "Message explaining what the human needs to do"},
                    "take_screenshot": {"type": "boolean", "description": "Take a screenshot for reference (default: true)", "default": True},
                },
                "required": ["captcha_type", "message"],
            },
        ),
        Tool(
            name="captcha_get_pending_interventions",
            description="Get all pending human intervention requests that have not been resolved",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="captcha_resolve_intervention",
            description="Mark an intervention request as resolved after human has solved the captcha. This allows the automation to continue.",
            inputSchema={
                "type": "object",
                "properties": {
                    "request_id": {"type": "string", "description": "The intervention request ID to resolve"},
                    "resolution": {"type": "string", "description": "Resolution status (default: 'solved')", "default": "solved"},
                },
                "required": ["request_id"],
            },
        ),
        Tool(
            name="captcha_wait_for_resolution",
            description="Block until a human intervention is resolved or timeout expires. Use this to pause automation while waiting for human to solve captcha.",
            inputSchema={
                "type": "object",
                "properties": {
                    "request_id": {"type": "string", "description": "The intervention request ID to wait for"},
                    "timeout": {"type": "number", "description": "Maximum seconds to wait (default: 300)", "default": 300.0},
                    "poll_interval": {"type": "number", "description": "Seconds between checks (default: 2)", "default": 2.0},
                },
                "required": ["request_id"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict):
    """Execute a tool call."""
    
    # Browser Management
    if name == "browser_launch":
        result = await browser_manager.launch(
            headless=arguments.get("headless", False),
            proxy=arguments.get("proxy"),
            user_agent=arguments.get("user_agent"),
            binary_location=arguments.get("binary_location"),
            window_size=tuple(arguments["window_size"]) if arguments.get("window_size") else None,
            incognito=arguments.get("incognito", False),
            disable_images=arguments.get("disable_images", False),
            arguments=arguments.get("arguments"),
        )
    
    elif name == "browser_close":
        result = await browser_manager.close()
    
    elif name == "browser_navigate":
        result = await browser_manager.navigate(arguments["url"])
    
    elif name == "browser_go_back":
        result = await browser_manager.go_back()
    
    elif name == "browser_go_forward":
        result = await browser_manager.go_forward()
    
    elif name == "browser_refresh":
        result = await browser_manager.refresh()
    
    elif name == "browser_get_info":
        result = await browser_manager.get_page_info()
    
    # Network Monitoring
    elif name == "network_enable_monitoring":
        result = await network_manager.enable_monitoring()
    
    elif name == "network_disable_monitoring":
        result = await network_manager.disable_monitoring()
    
    elif name == "network_get_logs":
        result = await network_manager.get_network_logs(arguments.get("filter_url"))
    
    elif name == "network_get_response_body":
        result = await network_manager.get_response_body(arguments["request_id"])
    
    # Network Interception
    elif name == "network_enable_interception":
        result = await network_manager.enable_interception(
            resource_type=arguments.get("resource_type"),
            request_stage=arguments.get("request_stage", "Request"),
        )
    
    elif name == "network_disable_interception":
        result = await network_manager.disable_interception()
    
    elif name == "network_setup_handler":
        result = await network_manager.setup_interception_handler(
            block_patterns=arguments.get("block_patterns"),
            modify_headers=arguments.get("modify_headers"),
            mock_responses=arguments.get("mock_responses"),
        )
    
    # DOM Operations
    elif name == "dom_find_element":
        result = await dom_manager.find_element(
            tag_name=arguments.get("tag_name"),
            id=arguments.get("id"),
            class_name=arguments.get("class_name"),
            name=arguments.get("name"),
            text=arguments.get("text"),
            css_selector=arguments.get("css_selector"),
            xpath=arguments.get("xpath"),
            timeout=arguments.get("timeout", 10),
        )
    
    elif name == "dom_find_elements":
        result = await dom_manager.find_elements(
            tag_name=arguments.get("tag_name"),
            class_name=arguments.get("class_name"),
            css_selector=arguments.get("css_selector"),
            xpath=arguments.get("xpath"),
            timeout=arguments.get("timeout", 10),
        )
    
    elif name == "dom_get_text":
        result = await dom_manager.get_element_text(
            selector=arguments["selector"],
            timeout=arguments.get("timeout", 10),
        )
    
    elif name == "dom_get_html":
        result = await dom_manager.get_element_html(
            selector=arguments["selector"],
            timeout=arguments.get("timeout", 10),
        )
    
    elif name == "dom_click":
        result = await dom_manager.click_element(
            selector=arguments["selector"],
            timeout=arguments.get("timeout", 10),
        )
    
    elif name == "dom_type":
        result = await dom_manager.type_text(
            selector=arguments["selector"],
            text=arguments["text"],
            clear_first=arguments.get("clear_first", False),
            timeout=arguments.get("timeout", 10),
        )
    
    elif name == "dom_scroll":
        result = await dom_manager.scroll_page(
            direction=arguments.get("direction", "down"),
            amount=arguments.get("amount", 500),
        )
    
    elif name == "dom_get_source":
        result = await dom_manager.get_page_source()
    
    elif name == "dom_wait_for":
        result = await dom_manager.wait_for_element(
            selector=arguments["selector"],
            timeout=arguments.get("timeout", 30),
        )
    
    # JavaScript Execution
    elif name == "js_execute":
        result = await js_manager.execute_script(arguments["script"])
    
    elif name == "js_get_console_logs":
        result = await js_manager.get_console_logs()
    
    elif name == "js_get_global_vars":
        result = await js_manager.get_global_variables()
    
    elif name == "js_get_local_storage":
        result = await js_manager.get_local_storage()
    
    elif name == "js_get_session_storage":
        result = await js_manager.get_session_storage()
    
    elif name == "js_set_local_storage":
        result = await js_manager.set_local_storage(
            key=arguments["key"],
            value=arguments["value"],
        )
    
    elif name == "js_get_forms":
        result = await js_manager.get_forms()
    
    elif name == "js_get_links":
        result = await js_manager.get_links()
    
    # Cookie & Session Management
    elif name == "session_get_cookies":
        result = await session_manager.get_cookies()
    
    elif name == "session_get_cookie":
        result = await session_manager.get_cookie(arguments["name"])
    
    elif name == "session_set_cookie":
        result = await session_manager.set_cookie(
            name=arguments["name"],
            value=arguments["value"],
            domain=arguments.get("domain"),
            path=arguments.get("path", "/"),
            secure=arguments.get("secure", False),
            http_only=arguments.get("http_only", False),
        )
    
    elif name == "session_delete_cookie":
        result = await session_manager.delete_cookie(
            name=arguments["name"],
            domain=arguments.get("domain"),
        )
    
    elif name == "session_clear_cookies":
        result = await session_manager.clear_cookies()
    
    elif name == "session_export_cookies":
        result = await session_manager.export_cookies(arguments.get("format", "json"))
    
    elif name == "session_import_cookies":
        result = await session_manager.import_cookies(arguments["cookies_json"])
    
    elif name == "session_make_request":
        result = await session_manager.make_request(
            url=arguments["url"],
            method=arguments.get("method", "GET"),
            headers=arguments.get("headers"),
            body=arguments.get("body"),
            params=arguments.get("params"),
        )
    
    # Screenshot & Debugging
    elif name == "debug_screenshot":
        result = await debug_manager.take_screenshot(
            path=arguments.get("path"),
            full_page=arguments.get("full_page", False),
            as_base64=arguments.get("as_base64", False),
        )
    
    elif name == "debug_get_viewport":
        result = await debug_manager.get_viewport_size()
    
    elif name == "debug_set_viewport":
        result = await debug_manager.set_viewport_size(
            width=arguments["width"],
            height=arguments["height"],
        )
    
    elif name == "debug_get_performance":
        result = await debug_manager.get_performance_metrics()
    
    elif name == "debug_highlight":
        result = await debug_manager.highlight_elements(
            selector=arguments["selector"],
            color=arguments.get("color", "red"),
        )
    
    # Captcha Handling
    elif name == "captcha_enable_turnstile_bypass":
        result = await captcha_manager.enable_turnstile_bypass(
            time_to_wait_captcha=arguments.get("time_to_wait_captcha", 5.0),
        )
    
    elif name == "captcha_disable_turnstile_bypass":
        result = await captcha_manager.disable_turnstile_bypass()
    
    elif name == "captcha_detect_type":
        result = await captcha_manager.detect_captcha_type()
    
    elif name == "captcha_handle_auto":
        result = await captcha_manager.handle_captcha_automatically(
            timeout=arguments.get("timeout", 30.0),
        )
    
    elif name == "captcha_request_human_intervention":
        result = await captcha_manager.request_human_intervention(
            captcha_type=arguments["captcha_type"],
            message=arguments["message"],
            take_screenshot=arguments.get("take_screenshot", True),
        )
    
    elif name == "captcha_get_pending_interventions":
        result = await captcha_manager.get_pending_interventions()
    
    elif name == "captcha_resolve_intervention":
        result = await captcha_manager.resolve_intervention(
            request_id=arguments["request_id"],
            resolution=arguments.get("resolution", "solved"),
        )
    
    elif name == "captcha_wait_for_resolution":
        result = await captcha_manager.wait_for_intervention_resolution(
            request_id=arguments["request_id"],
            timeout=arguments.get("timeout", 300.0),
            poll_interval=arguments.get("poll_interval", 2.0),
        )
    
    else:
        result = {"status": "error", "message": f"Unknown tool: {name}"}
    
    return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]


def main():
    """Main entry point for the MCP server."""
    asyncio.run(stdio_server(app))


if __name__ == "__main__":
    main()
