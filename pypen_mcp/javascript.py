"""
JavaScript execution module for PyPen MCP.

Provides tools for executing JavaScript in the browser context.
"""

from typing import Optional, Any

from .browser import browser_manager


class JSManager:
    """Manages JavaScript execution for pentesting."""
    
    async def execute_script(
        self,
        script: str,
        return_by_value: bool = True,
    ) -> dict:
        """Execute JavaScript in the browser context."""
        tab = browser_manager.get_tab()
        if tab is None:
            return {"status": "error", "message": "No browser tab available"}
        
        try:
            result = await tab.execute_script(script, return_by_value=return_by_value)
            return {
                "status": "success",
                "result": result,
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def execute_async_script(
        self,
        script: str,
        timeout: int = 30,
    ) -> dict:
        """Execute asynchronous JavaScript."""
        tab = browser_manager.get_tab()
        if tab is None:
            return {"status": "error", "message": "No browser tab available"}
        
        try:
            result = await tab.execute_async_script(script, timeout=timeout)
            return {
                "status": "success",
                "result": result,
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def get_console_logs(self) -> dict:
        """Get console logs from the browser (captured via JavaScript)."""
        tab = browser_manager.get_tab()
        if tab is None:
            return {"status": "error", "message": "No browser tab available"}
        
        try:
            # PyDoll doesn't have a built-in get_console_logs method
            # Return a message explaining how to capture console logs
            return {
                "status": "success",
                "message": "Console logs not directly available via CDP. Use network logs or JavaScript interception.",
                "logs": [],
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def inject_jquery(self) -> dict:
        """Inject jQuery into the page."""
        tab = browser_manager.get_tab()
        if tab is None:
            return {"status": "error", "message": "No browser tab available"}
        
        jquery_cdn = """
        var script = document.createElement('script');
        script.src = 'https://code.jquery.com/jquery-3.6.0.min.js';
        script.onload = function() { window.jQueryInjected = true; };
        document.head.appendChild(script);
        """
        
        try:
            await tab.execute_script(jquery_cdn)
            import asyncio
            await asyncio.sleep(1)
            
            is_loaded = await tab.execute_script("return typeof jQuery !== 'undefined'")
            if is_loaded:
                return {"status": "success", "message": "jQuery injected successfully"}
            else:
                return {"status": "error", "message": "Failed to inject jQuery"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def get_global_variables(self) -> dict:
        """Extract global JavaScript variables."""
        tab = browser_manager.get_tab()
        if tab is None:
            return {"status": "error", "message": "No browser tab available"}
        
        script = """
        (function() {
            var globals = {};
            for (var key in window) {
                try {
                    if (window.hasOwnProperty(key) && typeof window[key] !== 'function') {
                        var value = window[key];
                        if (typeof value === 'object' || typeof value === 'string' || 
                            typeof value === 'number' || typeof value === 'boolean') {
                            try {
                                JSON.stringify(value);
                                globals[key] = value;
                            } catch(e) {}
                        }
                    }
                } catch(e) {}
            }
            return globals;
        })();
        """
        
        try:
            result = await tab.execute_script(script)
            
            if isinstance(result, dict):
                filtered = {k: v for k, v in result.items() if not k.startswith('webkit') and not k.startswith('on')}
                return {
                    "status": "success",
                    "variables": dict(list(filtered.items())[:50]),
                    "count": len(filtered),
                }
            
            return {"status": "success", "variables": result}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def get_local_storage(self) -> dict:
        """Get all localStorage data."""
        tab = browser_manager.get_tab()
        if tab is None:
            return {"status": "error", "message": "No browser tab available"}
        
        script = """
        (function() {
            var data = {};
            for (var i = 0; i < localStorage.length; i++) {
                var key = localStorage.key(i);
                data[key] = localStorage.getItem(key);
            }
            return data;
        })();
        """
        
        try:
            result = await tab.execute_script(script)
            return {
                "status": "success",
                "storage": result,
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def get_session_storage(self) -> dict:
        """Get all sessionStorage data."""
        tab = browser_manager.get_tab()
        if tab is None:
            return {"status": "error", "message": "No browser tab available"}
        
        script = """
        (function() {
            var data = {};
            for (var i = 0; i < sessionStorage.length; i++) {
                var key = sessionStorage.key(i);
                data[key] = sessionStorage.getItem(key);
            }
            return data;
        })();
        """
        
        try:
            result = await tab.execute_script(script)
            return {
                "status": "success",
                "storage": result,
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def set_local_storage(self, key: str, value: str) -> dict:
        """Set a localStorage value."""
        tab = browser_manager.get_tab()
        if tab is None:
            return {"status": "error", "message": "No browser tab available"}
        
        script = f"localStorage.setItem('{key}', '{value}');"
        
        try:
            await tab.execute_script(script)
            return {"status": "success", "message": f"Set localStorage['{key}']"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def set_session_storage(self, key: str, value: str) -> dict:
        """Set a sessionStorage value."""
        tab = browser_manager.get_tab()
        if tab is None:
            return {"status": "error", "message": "No browser tab available"}
        
        script = f"sessionStorage.setItem('{key}', '{value}');"
        
        try:
            await tab.execute_script(script)
            return {"status": "success", "message": f"Set sessionStorage['{key}']"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def clear_local_storage(self) -> dict:
        """Clear all localStorage."""
        tab = browser_manager.get_tab()
        if tab is None:
            return {"status": "error", "message": "No browser tab available"}
        
        try:
            await tab.execute_script("localStorage.clear();")
            return {"status": "success", "message": "localStorage cleared"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def clear_session_storage(self) -> dict:
        """Clear all sessionStorage."""
        tab = browser_manager.get_tab()
        if tab is None:
            return {"status": "error", "message": "No browser tab available"}
        
        try:
            await tab.execute_script("sessionStorage.clear();")
            return {"status": "success", "message": "sessionStorage cleared"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def trigger_event(
        self,
        selector: str,
        event_type: str,
        bubbles: bool = True,
    ) -> dict:
        """Trigger a DOM event on an element."""
        tab = browser_manager.get_tab()
        if tab is None:
            return {"status": "error", "message": "No browser tab available"}
        
        script = f"""
        (function() {{
            var element = document.querySelector('{selector}');
            if (element) {{
                var event = new Event('{event_type}', {{ bubbles: {str(bubbles).lower()} }});
                element.dispatchEvent(event);
                return true;
            }}
            return false;
        }})();
        """
        
        try:
            result = await tab.execute_script(script)
            if result:
                return {"status": "success", "message": f"Triggered {event_type} on {selector}"}
            else:
                return {"status": "error", "message": "Element not found"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def eval_function(
        self,
        function_code: str,
        *args,
    ) -> dict:
        """Evaluate a JavaScript function with arguments."""
        tab = browser_manager.get_tab()
        if tab is None:
            return {"status": "error", "message": "No browser tab available"}
        
        script = f"({function_code})({', '.join(repr(arg) for arg in args)})"
        
        try:
            result = await tab.execute_script(script)
            return {
                "status": "success",
                "result": result,
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def get_forms(self) -> dict:
        """Get all forms on the page with their inputs."""
        tab = browser_manager.get_tab()
        if tab is None:
            return {"status": "error", "message": "No browser tab available"}
        
        script = """
        (function() {
            var forms = [];
            document.querySelectorAll('form').forEach(function(form, index) {
                var formData = {
                    index: index,
                    action: form.action,
                    method: form.method,
                    id: form.id,
                    name: form.name,
                    inputs: []
                };
                form.querySelectorAll('input, select, textarea').forEach(function(input) {
                    formData.inputs.push({
                        type: input.type || input.tagName.toLowerCase(),
                        name: input.name,
                        id: input.id,
                        value: input.value,
                        placeholder: input.placeholder
                    });
                });
                forms.push(formData);
            });
            return forms;
        })();
        """
        
        try:
            result = await tab.execute_script(script)
            return {
                "status": "success",
                "forms": result,
                "count": len(result) if isinstance(result, list) else 0,
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def get_links(self) -> dict:
        """Get all links on the page."""
        tab = browser_manager.get_tab()
        if tab is None:
            return {"status": "error", "message": "No browser tab available"}
        
        script = """
        (function() {
            var links = [];
            document.querySelectorAll('a[href]').forEach(function(a) {
                links.push({
                    href: a.href,
                    text: a.textContent.trim().substring(0, 100),
                    title: a.title,
                    target: a.target
                });
            });
            return links;
        })();
        """
        
        try:
            result = await tab.execute_script(script)
            return {
                "status": "success",
                "links": result[:200],  # Limit to 200 links
                "count": len(result) if isinstance(result, list) else 0,
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}


js_manager = JSManager()
