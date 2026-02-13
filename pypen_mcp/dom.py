"""
DOM manipulation and element interaction module for PyPen MCP.

Provides tools for finding, extracting, and interacting with DOM elements.
"""

import asyncio
from typing import Optional, Any

from .browser import browser_manager


class DOMManager:
    """Manages DOM operations for pentesting."""
    
    async def find_element(
        self,
        tag_name: Optional[str] = None,
        id: Optional[str] = None,
        class_name: Optional[str] = None,
        name: Optional[str] = None,
        text: Optional[str] = None,
        css_selector: Optional[str] = None,
        xpath: Optional[str] = None,
        timeout: int = 10,
    ) -> dict:
        """Find an element on the page using various selectors."""
        tab = browser_manager.get_tab()
        if tab is None:
            return {"status": "error", "message": "No browser tab available"}
        
        try:
            if xpath:
                element = await tab.query(xpath, timeout=timeout, raise_exc=False)
            elif css_selector:
                element = await tab.query(css_selector, timeout=timeout, raise_exc=False)
            else:
                element = await tab.find(
                    tag_name=tag_name,
                    id=id,
                    class_name=class_name,
                    name=name,
                    text=text,
                    timeout=timeout,
                    raise_exc=False,
                )
            
            if element is None:
                return {"status": "error", "message": "Element not found"}
            
            # tag_name is direct, text needs await
            elem_tag = element.tag_name
            elem_text = await element.text
            
            return {
                "status": "success",
                "found": True,
                "tag": elem_tag,
                "text": elem_text,
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def find_elements(
        self,
        tag_name: Optional[str] = None,
        class_name: Optional[str] = None,
        css_selector: Optional[str] = None,
        xpath: Optional[str] = None,
        timeout: int = 10,
    ) -> dict:
        """Find multiple elements on the page."""
        tab = browser_manager.get_tab()
        if tab is None:
            return {"status": "error", "message": "No browser tab available"}
        
        try:
            elements = []
            
            if xpath or css_selector:
                element = await tab.query(xpath or css_selector, timeout=timeout, raise_exc=False)
                if element:
                    elements = [element]
            else:
                element = await tab.find(
                    tag_name=tag_name,
                    class_name=class_name,
                    timeout=timeout,
                    raise_exc=False,
                )
                if element:
                    elements = [element]
            
            if not elements:
                return {"status": "success", "count": 0, "elements": []}
            
            results = []
            for elem in elements[:50]:  # Limit to 50 elements
                try:
                    text_val = await elem.text
                    results.append({
                        "tag": elem.tag_name,
                        "text": text_val[:200] if text_val else None,
                    })
                except:
                    pass
            
            return {
                "status": "success",
                "count": len(results),
                "total_found": len(elements),
                "elements": results,
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def get_element_attribute(
        self,
        selector: str,
        attribute: str,
        timeout: int = 10,
    ) -> dict:
        """Get an attribute value from an element."""
        tab = browser_manager.get_tab()
        if tab is None:
            return {"status": "error", "message": "No browser tab available"}
        
        try:
            element = await tab.query(selector, timeout=timeout, raise_exc=False)
            if element is None:
                return {"status": "error", "message": "Element not found"}
            
            value = await element.get_attribute(attribute)
            return {
                "status": "success",
                "attribute": attribute,
                "value": value,
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def get_element_text(
        self,
        selector: str,
        timeout: int = 10,
    ) -> dict:
        """Get the text content of an element."""
        tab = browser_manager.get_tab()
        if tab is None:
            return {"status": "error", "message": "No browser tab available"}
        
        try:
            element = await tab.query(selector, timeout=timeout, raise_exc=False)
            if element is None:
                return {"status": "error", "message": "Element not found"}
            
            text = await element.text
            return {
                "status": "success",
                "text": text,
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def get_element_html(
        self,
        selector: str,
        timeout: int = 10,
    ) -> dict:
        """Get the inner HTML of an element."""
        tab = browser_manager.get_tab()
        if tab is None:
            return {"status": "error", "message": "No browser tab available"}
        
        try:
            element = await tab.query(selector, timeout=timeout, raise_exc=False)
            if element is None:
                return {"status": "error", "message": "Element not found"}
            
            html = await element.inner_html
            return {
                "status": "success",
                "html": html[:5000] if html else None,  # Limit output size
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def click_element(
        self,
        selector: str,
        timeout: int = 10,
        humanize: bool = True,
    ) -> dict:
        """Click on an element. Scrolls into view first, falls back to JS click."""
        tab = browser_manager.get_tab()
        if tab is None:
            return {"status": "error", "message": "No browser tab available"}
        
        try:
            element = await tab.query(selector, timeout=timeout, raise_exc=False)
            if element is None:
                return {"status": "error", "message": f"Element not found: {selector}"}
            
            # Scroll element into view first
            try:
                await element.scroll_into_view()
            except Exception:
                pass  # Best effort, continue with click anyway
            
            # Wait briefly for scroll/animations to settle
            await asyncio.sleep(0.3)
            
            # Try simulated mouse click first (more realistic)
            try:
                await element.click(humanize=humanize)
                return {"status": "success", "message": "Element clicked"}
            except Exception:
                # Fall back to JavaScript click (works even if element is obscured)
                await element.click_using_js()
                return {"status": "success", "message": "Element clicked (via JS fallback)"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def type_text(
        self,
        selector: str,
        text: str,
        timeout: int = 10,
        clear_first: bool = False,
        humanize: bool = True,
    ) -> dict:
        """Type text into an input element."""
        tab = browser_manager.get_tab()
        if tab is None:
            return {"status": "error", "message": "No browser tab available"}
        
        try:
            element = await tab.query(selector, timeout=timeout, raise_exc=False)
            if element is None:
                return {"status": "error", "message": "Element not found"}
            
            if clear_first:
                await element.clear()
            
            await element.type_text(text, humanize=humanize)
            return {"status": "success", "message": f"Typed text: {text[:50]}..."}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def insert_text(
        self,
        selector: str,
        text: str,
        timeout: int = 10,
    ) -> dict:
        """Insert text into an element (faster, no typing simulation)."""
        tab = browser_manager.get_tab()
        if tab is None:
            return {"status": "error", "message": "No browser tab available"}
        
        try:
            element = await tab.query(selector, timeout=timeout, raise_exc=False)
            if element is None:
                return {"status": "error", "message": "Element not found"}
            
            await element.insert_text(text)
            return {"status": "success", "message": "Text inserted"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def select_option(
        self,
        selector: str,
        value: Optional[str] = None,
        text: Optional[str] = None,
        timeout: int = 10,
    ) -> dict:
        """Select an option from a select element."""
        tab = browser_manager.get_tab()
        if tab is None:
            return {"status": "error", "message": "No browser tab available"}
        
        try:
            element = await tab.query(selector, timeout=timeout, raise_exc=False)
            if element is None:
                return {"status": "error", "message": "Element not found"}
            
            if value:
                await element.select_option(value=value)
            elif text:
                await element.select_option(text=text)
            else:
                return {"status": "error", "message": "Either value or text must be provided"}
            
            return {"status": "success", "message": "Option selected"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def scroll_page(
        self,
        direction: str = "down",
        amount: int = 500,
        humanize: bool = True,
    ) -> dict:
        """Scroll the page."""
        tab = browser_manager.get_tab()
        if tab is None:
            return {"status": "error", "message": "No browser tab available"}
        
        try:
            from pydoll.interactions.scroll import ScrollPosition
            
            if direction.lower() == "down":
                await tab.scroll.by(ScrollPosition.DOWN, amount, humanize=humanize)
            elif direction.lower() == "up":
                await tab.scroll.by(ScrollPosition.UP, amount, humanize=humanize)
            elif direction.lower() == "bottom":
                await tab.scroll.to_bottom(humanize=humanize)
            elif direction.lower() == "top":
                await tab.scroll.to_top(humanize=humanize)
            
            return {"status": "success", "message": f"Scrolled {direction}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def hover_element(
        self,
        selector: str,
        timeout: int = 10,
    ) -> dict:
        """Hover over an element."""
        tab = browser_manager.get_tab()
        if tab is None:
            return {"status": "error", "message": "No browser tab available"}
        
        try:
            element = await tab.query(selector, timeout=timeout, raise_exc=False)
            if element is None:
                return {"status": "error", "message": "Element not found"}
            
            await element.hover()
            return {"status": "success", "message": "Hovered over element"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def get_page_source(self) -> dict:
        """Get the full page source HTML."""
        tab = browser_manager.get_tab()
        if tab is None:
            return {"status": "error", "message": "No browser tab available"}
        
        try:
            source = await tab.page_source
            return {
                "status": "success",
                "source": source[:50000],  # Limit to 50KB
                "truncated": len(source) > 50000,
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def wait_for_element(
        self,
        selector: str,
        timeout: int = 30,
    ) -> dict:
        """Wait for an element to appear on the page."""
        tab = browser_manager.get_tab()
        if tab is None:
            return {"status": "error", "message": "No browser tab available"}
        
        try:
            element = await tab.query(selector, timeout=timeout, raise_exc=False)
            if element is None:
                return {"status": "error", "message": f"Element not found within {timeout}s"}
            
            return {"status": "success", "message": "Element appeared"}
        except Exception as e:
            return {"status": "error", "message": str(e)}


dom_manager = DOMManager()
