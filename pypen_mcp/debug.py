"""
Screenshot and debugging module for PyPen MCP.

Provides tools for capturing screenshots and debugging browser state.
"""

import os
import base64
from typing import Optional
from datetime import datetime

from .browser import browser_manager


class DebugManager:
    """Manages screenshots and debugging for pentesting."""
    
    async def take_screenshot(
        self,
        path: Optional[str] = None,
        full_page: bool = False,
        as_base64: bool = False,
    ) -> dict:
        """Take a screenshot of the current page."""
        tab = browser_manager.get_tab()
        if tab is None:
            return {"status": "error", "message": "No browser tab available"}
        
        try:
            if as_base64:
                b64_data = await tab.take_screenshot(as_base64=True)
                return {
                    "status": "success",
                    "base64": b64_data,
                    "format": "png",
                }
            
            if path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                path = f"/tmp/pypen_screenshot_{timestamp}.png"
            
            await tab.take_screenshot(path=path)
            
            return {
                "status": "success",
                "path": path,
                "message": f"Screenshot saved to {path}",
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def take_element_screenshot(
        self,
        selector: str,
        path: Optional[str] = None,
        timeout: int = 10,
    ) -> dict:
        """Take a screenshot of a specific element."""
        tab = browser_manager.get_tab()
        if tab is None:
            return {"status": "error", "message": "No browser tab available"}
        
        try:
            element = await tab.query(selector, timeout=timeout, raise_exc=False)
            if element is None:
                return {"status": "error", "message": "Element not found"}
            
            if path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                path = f"/tmp/pypen_element_{timestamp}.png"
            
            await element.take_screenshot(path=path)
            
            return {
                "status": "success",
                "path": path,
                "message": f"Element screenshot saved to {path}",
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def get_viewport_size(self) -> dict:
        """Get the current viewport size."""
        tab = browser_manager.get_tab()
        if tab is None:
            return {"status": "error", "message": "No browser tab available"}
        
        script = """
        ({
            width: window.innerWidth,
            height: window.innerHeight,
            devicePixelRatio: window.devicePixelRatio
        });
        """
        
        try:
            result = await tab.execute_script(script)
            return {
                "status": "success",
                "viewport": result,
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def set_viewport_size(self, width: int, height: int) -> dict:
        """Set the viewport size using JavaScript window resize."""
        tab = browser_manager.get_tab()
        if tab is None:
            return {"status": "error", "message": "No browser tab available"}
        
        try:
            # Use JavaScript to resize window
            await tab.execute_script(f"window.resizeTo({width}, {height})")
            return {
                "status": "success",
                "message": f"Viewport resize requested to {width}x{height}",
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def get_performance_metrics(self) -> dict:
        """Get performance metrics from the page."""
        tab = browser_manager.get_tab()
        if tab is None:
            return {"status": "error", "message": "No browser tab available"}
        
        script = """
        (function() {
            var perf = performance.getEntriesByType('navigation')[0] || {};
            var resources = performance.getEntriesByType('resource');
            return {
                timing: {
                    domContentLoaded: perf.domContentLoadedEventEnd - perf.domContentLoadedEventStart,
                    loadComplete: perf.loadEventEnd - perf.loadEventStart,
                    domInteractive: perf.domInteractive,
                    responseStart: perf.responseStart,
                    requestStart: perf.requestStart,
                    domainLookupEnd: perf.domainLookupEnd,
                    domainLookupStart: perf.domainLookupStart,
                    connectEnd: perf.connectEnd,
                    connectStart: perf.connectStart,
                },
                resources: resources.length,
                memory: performance.memory ? {
                    usedJSHeapSize: performance.memory.usedJSHeapSize,
                    totalJSHeapSize: performance.memory.totalJSHeapSize,
                } : null
            };
        })();
        """
        
        try:
            result = await tab.execute_script(script)
            return {
                "status": "success",
                "metrics": result,
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def get_console_messages(self) -> dict:
        """Get console messages from the page (via JavaScript interception)."""
        tab = browser_manager.get_tab()
        if tab is None:
            return {"status": "error", "message": "No browser tab available"}
        
        try:
            # PyDoll doesn't have built-in console log capture
            # Return message about alternative approaches
            return {
                "status": "success",
                "message": "Console messages require JavaScript interception setup",
                "logs": [],
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def get_dom_snapshot(self) -> dict:
        """Get a snapshot of the DOM structure."""
        tab = browser_manager.get_tab()
        if tab is None:
            return {"status": "error", "message": "No browser tab available"}
        
        script = """
        (function() {
            function walkDOM(node, depth) {
                depth = depth || 0;
                var result = {
                    tag: node.tagName ? node.tagName.toLowerCase() : 'text',
                    depth: depth
                };
                
                if (node.id) result.id = node.id;
                if (node.className && typeof node.className === 'string') result.class = node.className;
                
                if (node.nodeType === 3) {
                    var text = node.textContent.trim();
                    if (text) result.text = text.substring(0, 100);
                }
                
                if (node.childNodes && depth < 5) {
                    result.children = [];
                    for (var i = 0; i < Math.min(node.childNodes.length, 20); i++) {
                        var child = walkDOM(node.childNodes[i], depth + 1);
                        if (child) result.children.push(child);
                    }
                }
                
                return result;
            }
            
            return walkDOM(document.body);
        })();
        """
        
        try:
            result = await tab.execute_script(script)
            return {
                "status": "success",
                "snapshot": result,
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def get_network_waterfall(self) -> dict:
        """Get network request timing waterfall."""
        tab = browser_manager.get_tab()
        if tab is None:
            return {"status": "error", "message": "No browser tab available"}
        
        script = """
        (function() {
            var entries = performance.getEntriesByType('resource');
            return entries.map(function(entry) {
                return {
                    name: entry.name,
                    duration: entry.duration,
                    startTime: entry.startTime,
                    initiatorType: entry.initiatorType,
                    transferSize: entry.transferSize
                };
            }).slice(0, 50);
        })();
        """
        
        try:
            result = await tab.execute_script(script)
            return {
                "status": "success",
                "waterfall": result,
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def inject_debug_script(self) -> dict:
        """Inject a debug helper script into the page."""
        tab = browser_manager.get_tab()
        if tab is None:
            return {"status": "error", "message": "No browser tab available"}
        
        script = """
        window.PyPenDebug = {
            getEventListeners: function(element) {
                return getEventListeners ? getEventListeners(element) : 'Not available';
            },
            highlight: function(selector) {
                var el = document.querySelector(selector);
                if (el) {
                    el.style.outline = '3px solid red';
                    return true;
                }
                return false;
            },
            unhighlight: function(selector) {
                var el = document.querySelector(selector);
                if (el) {
                    el.style.outline = '';
                    return true;
                }
                return false;
            },
            getXPath: function(element) {
                if (element.id) return '//*[@id="' + element.id + '"]';
                if (element === document.body) return '/html/body';
                
                var ix = 0;
                var siblings = element.parentNode.childNodes;
                for (var i = 0; i < siblings.length; i++) {
                    var sibling = siblings[i];
                    if (sibling === element) {
                        return this.getXPath(element.parentNode) + '/' + element.tagName.toLowerCase() + '[' + (ix + 1) + ']';
                    }
                    if (sibling.nodeType === 1 && sibling.tagName === element.tagName) {
                        ix++;
                    }
                }
            }
        };
        'PyPen debug helpers injected';
        """
        
        try:
            result = await tab.execute_script(script)
            return {
                "status": "success",
                "message": result,
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def get_element_bounding_box(self, selector: str, timeout: int = 10) -> dict:
        """Get the bounding box of an element."""
        tab = browser_manager.get_tab()
        if tab is None:
            return {"status": "error", "message": "No browser tab available"}
        
        try:
            element = await tab.query(selector, timeout=timeout, raise_exc=False)
            if element is None:
                return {"status": "error", "message": "Element not found"}
            
            box = await element.get_bounding_box()
            return {
                "status": "success",
                "bounding_box": box,
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def highlight_elements(self, selector: str, color: str = "red") -> dict:
        """Highlight all elements matching a selector."""
        tab = browser_manager.get_tab()
        if tab is None:
            return {"status": "error", "message": "No browser tab available"}
        
        script = f"""
        (function() {{
            var elements = document.querySelectorAll('{selector}');
            elements.forEach(function(el) {{
                el.style.outline = '3px solid {color}';
            }});
            return elements.length;
        }})();
        """
        
        try:
            count = await tab.execute_script(script)
            return {
                "status": "success",
                "message": f"Highlighted {count} elements",
                "count": count,
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def print_to_pdf(self, path: Optional[str] = None) -> dict:
        """Print the page to PDF."""
        tab = browser_manager.get_tab()
        if tab is None:
            return {"status": "error", "message": "No browser tab available"}
        
        if path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            path = f"/tmp/pypen_page_{timestamp}.pdf"
        
        try:
            await tab.print_to_pdf(path=path)
            return {
                "status": "success",
                "path": path,
                "message": f"PDF saved to {path}",
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}


debug_manager = DebugManager()
