# PyPen MCP

Model Context Protocol server for browser-based penetration testing using PyDoll.

## Overview

PyPen MCP provides a comprehensive set of tools for LLM-powered browser automation and security testing. It leverages PyDoll's Chrome DevTools Protocol integration for reliable, webdriver-free browser control.

## Features

### Browser Management
- Launch/close browser instances with configurable options
- Navigation control (navigate, back, forward, refresh)
- Headless mode, proxy support, custom user agents
- Incognito mode and resource blocking

### Network Operations
- **Monitoring**: Capture all HTTP traffic, analyze requests/responses
- **Interception**: Block, modify, or mock requests in real-time
- **Authenticated Requests**: Make API calls that inherit browser session/cookies

### DOM Manipulation
- Find elements by CSS selector, XPath, or attributes
- Click, type, scroll, and interact with elements
- Extract page source, element text, and HTML
- Human-like scrolling with physics simulation

### JavaScript Execution
- Execute arbitrary JavaScript in browser context
- Access localStorage and sessionStorage
- Extract global variables, forms, and links

### Session Management
- Cookie manipulation (get, set, delete, clear)
- Import/export cookies in multiple formats
- Session-aware HTTP requests

### Captcha Handling
- **Turnstile Bypass**: Automatic Cloudflare Turnstile interaction
- **Human Intervention**: Request human help for unsolvable captchas (ReCAPTCHA v2, hCaptcha)
- **Detection**: Identify captcha types on the page

### Debugging
- Screenshots (full page or elements)
- Viewport control
- Performance metrics
- Element highlighting

## Installation

```bash
pip install pypen-mcp
```

Or install from source:

```bash
git clone https://github.com/your-repo/pypen-mcp
cd pypen-mcp
pip install -e .
```

## Configuration

Add to your MCP client configuration:

```json
{
  "mcpServers": {
    "pypen": {
      "command": "pypen-mcp"
    }
  }
}
```

For development:

```json
{
  "mcpServers": {
    "pypen": {
      "command": "/path/to/pypen-mcp/.venv/bin/pypen-mcp"
    }
  }
}
```

## Usage Examples

### Basic Browser Automation

```python
# Launch browser
browser_launch(headless=True)

# Navigate to target
browser_navigate(url="https://example.com")

# Extract page content
dom_get_source()

# Find and interact with elements
dom_find_element(css_selector="#username")
dom_type(selector="#username", text="admin")
dom_click(selector="button[type=submit]")

# Take screenshot for documentation
debug_screenshot(path="/tmp/screenshot.png")

# Close when done
browser_close()
```

### Network Monitoring

```python
# Enable traffic capture
network_enable_monitoring()

# Navigate and capture
browser_navigate(url="https://api.example.com")

# Get captured requests
network_get_logs(filter_url="/api/")

# Get response body for specific request
network_get_response_body(request_id="abc123")

# Disable when done
network_disable_monitoring()
```

### Request Interception

```python
# Set up interception rules
network_setup_handler(
    block_patterns=["analytics", "tracking", "ads"],
    modify_headers={"Authorization": "Bearer token123"},
    mock_responses={"/api/config": {"status": 200, "body": {"debug": true}}}
)

# Navigate with interception active
browser_navigate(url="https://example.com")
```

### Session-Based Requests

```python
# Login via UI (handles complex auth)
browser_navigate(url="https://app.com/login")
dom_type(selector="#email", text="user@example.com")
dom_type(selector="#password", text="password123")
dom_click(selector="button[type=submit]")

# Make authenticated API calls
session_make_request(
    url="https://app.com/api/user/profile",
    method="GET"
)
```

### Captcha Handling

```python
# Enable automatic Turnstile bypass
captcha_enable_turnstile_bypass(time_to_wait_captcha=10.0)

# Navigate to protected site
browser_navigate(url="https://protected-site.com")

# Wait for captcha processing
# ... automation continues ...

# For unsolvable captchas, request human help
captcha_detect_type()  # Check what's on page
captcha_request_human_intervention(
    captcha_type="recaptcha_v2",
    message="Please solve the ReCAPTCHA to continue"
)

# Wait for human to solve
captcha_wait_for_resolution(request_id="abc123", timeout=300)
```

## Tool Reference

### Browser Tools
| Tool | Description |
|------|-------------|
| `browser_launch` | Launch browser with options (headless, proxy, etc.) |
| `browser_close` | Close the browser instance |
| `browser_navigate` | Navigate to a URL |
| `browser_go_back` | Navigate back in history |
| `browser_go_forward` | Navigate forward in history |
| `browser_refresh` | Refresh current page |
| `browser_get_info` | Get current URL and title |

### Network Tools
| Tool | Description |
|------|-------------|
| `network_enable_monitoring` | Start capturing HTTP traffic |
| `network_disable_monitoring` | Stop traffic capture |
| `network_get_logs` | Get captured requests (with optional filter) |
| `network_get_response_body` | Get response body for a request |
| `network_enable_interception` | Enable request interception |
| `network_disable_interception` | Disable interception |
| `network_setup_handler` | Configure auto interception rules |

### DOM Tools
| Tool | Description |
|------|-------------|
| `dom_find_element` | Find element by selector |
| `dom_find_elements` | Find multiple elements |
| `dom_get_text` | Get element text content |
| `dom_get_html` | Get element HTML |
| `dom_click` | Click an element |
| `dom_type` | Type text into input |
| `dom_scroll` | Scroll the page |
| `dom_get_source` | Get full page HTML |
| `dom_wait_for` | Wait for element to appear |

### JavaScript Tools
| Tool | Description |
|------|-------------|
| `js_execute` | Execute JavaScript code |
| `js_get_console_logs` | Get console logs |
| `js_get_global_vars` | Extract global variables |
| `js_get_local_storage` | Get localStorage data |
| `js_get_session_storage` | Get sessionStorage data |
| `js_set_local_storage` | Set localStorage value |
| `js_get_forms` | Get all forms with inputs |
| `js_get_links` | Get all links on page |

### Session Tools
| Tool | Description |
|------|-------------|
| `session_get_cookies` | Get all cookies |
| `session_get_cookie` | Get specific cookie |
| `session_set_cookie` | Set a cookie |
| `session_delete_cookie` | Delete a cookie |
| `session_clear_cookies` | Clear all cookies |
| `session_export_cookies` | Export cookies (json/netscape/header) |
| `session_import_cookies` | Import cookies from JSON |
| `session_make_request` | Make session-authenticated HTTP request |

### Captcha Tools
| Tool | Description |
|------|-------------|
| `captcha_enable_turnstile_bypass` | Enable auto Turnstile handling |
| `captcha_disable_turnstile_bypass` | Disable Turnstile handling |
| `captcha_detect_type` | Detect captcha type on page |
| `captcha_handle_auto` | Auto-handle detected captcha |
| `captcha_request_human_intervention` | Request human help |
| `captcha_get_pending_interventions` | Get unresolved requests |
| `captcha_resolve_intervention` | Mark intervention as resolved |
| `captcha_wait_for_resolution` | Wait for human to solve |

### Debug Tools
| Tool | Description |
|------|-------------|
| `debug_screenshot` | Take page screenshot |
| `debug_get_viewport` | Get viewport size |
| `debug_set_viewport` | Set viewport size |
| `debug_get_performance` | Get performance metrics |
| `debug_highlight` | Highlight matching elements |

## Important Notes

### Browser Session Persistence
- The browser session persists until explicitly closed with `browser_close`
- All operations (DOM, JS, network) use the same active session
- Cookies and session state are maintained across navigations

### Captcha Success Factors
Turnstile bypass success depends on:
1. **IP Reputation**: Use residential proxies with good reputation
2. **Browser Fingerprint**: Configure realistic browser options
3. **Behavioral Patterns**: Add realistic delays and interactions

### Human Intervention Workflow
1. Detect captcha: `captcha_detect_type()`
2. Try auto-handling: `captcha_handle_auto()`
3. If fails, request help: `captcha_request_human_intervention()`
4. Wait for resolution: `captcha_wait_for_resolution()`
5. Continue automation

## License

MIT
