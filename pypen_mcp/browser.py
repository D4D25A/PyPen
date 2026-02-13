"""
Browser management module for PyPen MCP.

Handles browser lifecycle, tab management, and navigation operations.
"""

import asyncio
from typing import Optional
from pydoll.browser.chromium import Chrome
from pydoll.browser.options import ChromiumOptions


class BrowserManager:
    """Manages browser instances and tabs for pentesting operations."""
    
    _instance: Optional["BrowserManager"] = None
    _browser: Optional[Chrome] = None
    _tab = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    async def launch(
        self,
        headless: bool = False,
        proxy: Optional[str] = None,
        user_agent: Optional[str] = None,
        binary_location: Optional[str] = None,
        window_size: Optional[tuple[int, int]] = None,
        incognito: bool = False,
        disable_images: bool = False,
        arguments: Optional[list[str]] = None,
    ) -> dict:
        """Launch a new browser instance with specified options."""
        if self._browser is not None:
            return {"status": "error", "message": "Browser already running. Close it first."}
        
        options = ChromiumOptions()
        
        if headless:
            options.add_argument("--headless=new")
        
        if proxy:
            options.add_argument(f"--proxy-server={proxy}")
        
        if user_agent:
            options.add_argument(f"--user-agent={user_agent}")
        
        if binary_location:
            options.binary_location = binary_location
        
        if window_size:
            options.add_argument(f"--window-size={window_size[0]},{window_size[1]}")
        
        if incognito:
            options.add_argument("--incognito")
        
        if disable_images:
            options.browser_preferences = {
                "profile": {
                    "managed_default_content_settings": {
                        "images": 2
                    }
                }
            }
        
        if arguments:
            for arg in arguments:
                options.add_argument(arg)
        
        self._browser = Chrome(options=options)
        self._tab = await self._browser.start()
        
        return {
            "status": "success",
            "message": "Browser launched successfully",
            "headless": headless,
            "proxy": proxy,
        }
    
    async def close(self) -> dict:
        """Close the browser instance."""
        if self._browser is None:
            return {"status": "error", "message": "No browser instance running"}
        
        await self._browser.stop()
        self._browser = None
        self._tab = None
        
        return {"status": "success", "message": "Browser closed"}
    
    async def navigate(self, url: str) -> dict:
        """Navigate to a URL."""
        if self._tab is None:
            return {"status": "error", "message": "No browser tab available"}
        
        await self._tab.go_to(url)
        
        return {
            "status": "success",
            "url": url,
            "title": await self._tab.title,
            "current_url": await self._tab.current_url,
        }
    
    async def go_back(self) -> dict:
        """Navigate back in history using JavaScript."""
        if self._tab is None:
            return {"status": "error", "message": "No browser tab available"}
        
        await self._tab.execute_script("history.back()")
        await asyncio.sleep(0.5)
        
        return {
            "status": "success",
            "current_url": await self._tab.current_url,
        }
    
    async def go_forward(self) -> dict:
        """Navigate forward in history using JavaScript."""
        if self._tab is None:
            return {"status": "error", "message": "No browser tab available"}
        
        await self._tab.execute_script("history.forward()")
        await asyncio.sleep(0.5)
        
        return {
            "status": "success",
            "current_url": await self._tab.current_url,
        }
    
    async def refresh(self) -> dict:
        """Refresh the current page."""
        if self._tab is None:
            return {"status": "error", "message": "No browser tab available"}
        
        await self._tab.refresh()
        return {
            "status": "success",
            "current_url": await self._tab.current_url,
        }
    
    async def get_page_info(self) -> dict:
        """Get information about the current page."""
        if self._tab is None:
            return {"status": "error", "message": "No browser tab available"}
        
        return {
            "status": "success",
            "url": await self._tab.current_url,
            "title": await self._tab.title,
        }
    
    def get_tab(self):
        """Get the current tab instance."""
        return self._tab
    
    def is_running(self) -> bool:
        """Check if browser is running."""
        return self._browser is not None


browser_manager = BrowserManager()
