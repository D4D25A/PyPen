# PyPen MCP Agent Skill

## Purpose

PyPen MCP enables LLM agents to perform browser-based security testing and automation tasks. This skill provides guidance on effective usage patterns.

## Capabilities

### What PyPen CAN Do
- Control a Chromium browser instance (launch, navigate, interact)
- Monitor and intercept network traffic
- Execute JavaScript in browser context
- Extract and manipulate DOM elements
- Manage cookies and sessions
- Handle Cloudflare Turnstile automatically
- Request human intervention for unsolvable captchas
- Take screenshots for documentation

### What PyPen CANNOT Do
- Solve ReCAPTCHA v2 image challenges automatically
- Bypass IP-based blocks (use residential proxies)
- Circumvent sophisticated anti-bot systems without good fingerprint
- Access pages that require authentication without valid credentials

## Workflow Patterns

### Pattern 1: Reconnaissance

```
1. browser_launch(headless=True)
2. browser_navigate(url="https://target.com")
3. dom_get_source() → Analyze page structure
4. js_get_forms() → Identify forms
5. js_get_links() → Find all links
6. network_enable_monitoring()
7. Interact with page elements
8. network_get_logs() → Capture API calls
9. browser_close()
```

### Pattern 2: Authenticated Testing

```
1. browser_launch()
2. browser_navigate(url="https://app.com/login")
3. dom_type(selector="#username", text="user")
4. dom_type(selector="#password", text="pass")
5. dom_click(selector="button[type=submit]")
6. dom_wait_for(selector=".dashboard", timeout=10)
7. session_get_cookies() → Capture session cookies
8. session_export_cookies(format="json") → Save for later
9. Continue testing...
```

### Pattern 3: API Reverse Engineering

```
1. browser_launch()
2. network_enable_monitoring()
3. browser_navigate(url="https://app.com")
4. Perform actions that trigger API calls
5. network_get_logs(filter_url="/api/")
6. network_get_response_body(request_id) → Get response data
7. Identify API endpoints and parameters
8. session_make_request() → Test API directly with session
```

### Pattern 4: Captcha Handling

```
1. browser_launch()
2. captcha_enable_turnstile_bypass()
3. browser_navigate(url="https://protected-site.com")
4. await 5 seconds for captcha processing
5. captcha_detect_type() → Check if still blocked
6. If captcha remains:
   a. captcha_request_human_intervention(captcha_type="recaptcha_v2", message="...")
   b. captcha_wait_for_resolution(request_id, timeout=300)
7. Continue with page interaction
```

### Pattern 5: Form Testing

```
1. browser_launch()
2. browser_navigate(url="https://target.com/form")
3. js_get_forms() → Identify all forms and inputs
4. For each input:
   - Test with valid values
   - Test with invalid values
   - Test with XSS payloads
   - Test with SQL injection payloads
5. network_get_logs() → Capture submissions
6. Analyze responses for vulnerabilities
```

## Best Practices

### Browser Management
- Always close the browser when done: `browser_close()`
- Use headless mode for automated testing: `browser_launch(headless=True)`
- Use visible browser for debugging: `browser_launch(headless=False)`
- Configure proxy for anonymity: `browser_launch(proxy="socks5://127.0.0.1:9050")`

### Network Operations
- Enable monitoring BEFORE navigating
- Disable monitoring when not needed to save resources
- Use filters to reduce log noise: `network_get_logs(filter_url="/api/")`

### Element Interaction
- Use specific selectors to avoid ambiguity
- Wait for dynamic content: `dom_wait_for(selector, timeout=30)`
- Take screenshots before/after critical actions

### Captcha Handling
- Enable Turnstile bypass BEFORE navigating to protected pages
- Check captcha type after navigation to verify success
- Request human intervention early if auto-handling fails
- Always wait for resolution before continuing

### Session Management
- Export cookies after authentication for reuse
- Import cookies to restore sessions
- Use `session_make_request` for API testing with browser session

## Error Handling

### Common Errors and Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| "No browser tab available" | Browser not launched | Run `browser_launch` first |
| "Element not found" | Selector incorrect or element not loaded | Check selector, increase timeout |
| "Request timeout" | Page slow to load | Increase timeout values |
| "Captcha not solved" | IP/fingerprint flagged | Use residential proxy, improve fingerprint |

### Graceful Degradation

```
# Always check for errors
result = dom_find_element(selector="#dynamic-content")
if result["status"] == "error":
    # Handle missing element
    dom_wait_for(selector="#dynamic-content", timeout=30)
    result = dom_find_element(selector="#dynamic-content")
```

## Security Considerations

### Ethical Usage
- Only test systems you have permission to test
- Respect rate limits and robots.txt
- Do not use for unauthorized access or data theft
- Follow responsible disclosure for vulnerabilities found

### Operational Security
- Use proxies to protect your IP
- Rotate user agents
- Clear cookies between sessions
- Close browser instances when done

## Tool Selection Guide

### I need to...
- **Navigate to a URL** → `browser_navigate`
- **Click something** → `dom_click`
- **Type into an input** → `dom_type`
- **Read page content** → `dom_get_source` or `dom_get_text`
- **Find specific elements** → `dom_find_element` or `dom_find_elements`
- **See network traffic** → `network_enable_monitoring` → `network_get_logs`
- **Block ads/trackers** → `network_setup_handler(block_patterns=[...])`
- **Run JavaScript** → `js_execute`
- **Get/set cookies** → `session_get_cookies` / `session_set_cookie`
- **Make authenticated API calls** → `session_make_request`
- **Take a screenshot** → `debug_screenshot`
- **Handle Cloudflare** → `captcha_enable_turnstile_bypass`
- **Get human help** → `captcha_request_human_intervention`

## Session State Management

The browser session is maintained as a singleton:
- Launch once, use for multiple operations
- Session persists until `browser_close` is called
- All tools operate on the same browser instance
- Cookies and state are preserved across navigations

## Integration Notes

### With Other MCPs
- Use with code execution MCPs for advanced analysis
- Use with database MCPs for storing captured data
- Use with notification MCPs for alerting on findings

### Automation Tips
- Chain operations logically: navigate → wait → interact → capture
- Use screenshots to document findings
- Export cookies and logs for analysis
- Request human intervention when stuck on captchas
