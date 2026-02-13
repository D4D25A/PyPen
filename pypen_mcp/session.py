"""
Cookie and session management module for PyPen MCP.

Provides tools for managing cookies, sessions, and authentication state.
"""

from typing import Optional, Any
import json

from .browser import browser_manager


class SessionManager:
    """Manages cookies and session state for pentesting."""
    
    async def get_cookies(self) -> dict:
        """Get all cookies from the browser."""
        tab = browser_manager.get_tab()
        if tab is None:
            return {"status": "error", "message": "No browser tab available"}
        
        try:
            cookies = await tab.get_cookies()
            return {
                "status": "success",
                "cookies": cookies,
                "count": len(cookies),
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def get_cookie(self, name: str) -> dict:
        """Get a specific cookie by name."""
        tab = browser_manager.get_tab()
        if tab is None:
            return {"status": "error", "message": "No browser tab available"}
        
        try:
            cookies = await tab.get_cookies()
            for cookie in cookies:
                if cookie.get("name") == name:
                    return {
                        "status": "success",
                        "cookie": cookie,
                    }
            return {"status": "error", "message": f"Cookie '{name}' not found"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def set_cookie(
        self,
        name: str,
        value: str,
        domain: Optional[str] = None,
        path: str = "/",
        secure: bool = False,
        http_only: bool = False,
        same_site: Optional[str] = None,
        expiry: Optional[int] = None,
    ) -> dict:
        """Set a cookie in the browser."""
        tab = browser_manager.get_tab()
        if tab is None:
            return {"status": "error", "message": "No browser tab available"}
        
        cookie = {
            "name": name,
            "value": value,
            "path": path,
            "secure": secure,
            "httpOnly": http_only,
        }
        
        if domain:
            cookie["domain"] = domain
        if same_site:
            cookie["sameSite"] = same_site
        if expiry:
            cookie["expires"] = expiry
        
        try:
            # Tab.set_cookies expects a list
            await tab.set_cookies([cookie])
            return {
                "status": "success",
                "message": f"Cookie '{name}' set",
                "cookie": cookie,
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def delete_cookie(self, name: str, domain: Optional[str] = None) -> dict:
        """Delete a cookie by name using JavaScript."""
        tab = browser_manager.get_tab()
        if tab is None:
            return {"status": "error", "message": "No browser tab available"}
        
        try:
            # Use JavaScript to delete a specific cookie
            domain_str = f"domain={domain}; " if domain else ""
            await tab.execute_script(f"document.cookie = '{name}=; {domain_str}path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT';")
            return {
                "status": "success",
                "message": f"Cookie '{name}' deleted",
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def clear_cookies(self) -> dict:
        """Clear all cookies."""
        tab = browser_manager.get_tab()
        if tab is None:
            return {"status": "error", "message": "No browser tab available"}
        
        try:
            await tab.delete_all_cookies()
            return {"status": "success", "message": "All cookies cleared"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def export_cookies(self, format: str = "json") -> dict:
        """Export cookies in various formats."""
        tab = browser_manager.get_tab()
        if tab is None:
            return {"status": "error", "message": "No browser tab available"}
        
        try:
            cookies = await tab.get_cookies()
            
            if format == "json":
                return {
                    "status": "success",
                    "format": "json",
                    "data": json.dumps(cookies, indent=2),
                }
            elif format == "netscape":
                lines = []
                for c in cookies:
                    flag = "TRUE" if c.get("secure") else "FALSE"
                    expiry = str(c.get("expires", 0))
                    lines.append(f".{c.get('domain', '')}\tTRUE\t{c.get('path', '/')}\t{flag}\t{expiry}\t{c.get('name')}\t{c.get('value')}")
                return {
                    "status": "success",
                    "format": "netscape",
                    "data": "\n".join(lines),
                }
            elif format == "header":
                header = "; ".join(f"{c.get('name')}={c.get('value')}" for c in cookies)
                return {
                    "status": "success",
                    "format": "header",
                    "data": header,
                }
            else:
                return {"status": "error", "message": f"Unknown format: {format}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def import_cookies(self, cookies_json: str) -> dict:
        """Import cookies from JSON string."""
        tab = browser_manager.get_tab()
        if tab is None:
            return {"status": "error", "message": "No browser tab available"}
        
        try:
            cookies = json.loads(cookies_json)
            if not isinstance(cookies, list):
                cookies = [cookies]
            
            imported = 0
            for cookie in cookies:
                try:
                    await tab.set_cookie(cookie)
                    imported += 1
                except:
                    pass
            
            return {
                "status": "success",
                "message": f"Imported {imported} cookies",
                "imported": imported,
                "total": len(cookies),
            }
        except json.JSONDecodeError:
            return {"status": "error", "message": "Invalid JSON format"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def get_session_info(self) -> dict:
        """Get comprehensive session information."""
        tab = browser_manager.get_tab()
        if tab is None:
            return {"status": "error", "message": "No browser tab available"}
        
        try:
            cookies = await tab.get_cookies()
            url = await tab.url
            title = await tab.title
            
            script = """
            (function() {
                return {
                    localStorage: Object.keys(localStorage).length,
                    sessionStorage: Object.keys(sessionStorage).length,
                    userAgent: navigator.userAgent,
                    platform: navigator.platform,
                    language: navigator.language,
                    cookiesEnabled: navigator.cookieEnabled
                };
            })();
            """
            
            browser_info = await tab.execute_script(script)
            
            return {
                "status": "success",
                "url": url,
                "title": title,
                "cookies_count": len(cookies),
                "cookies": cookies,
                "browser_info": browser_info,
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def make_request(
        self,
        url: str,
        method: str = "GET",
        headers: Optional[dict] = None,
        body: Optional[str] = None,
        params: Optional[dict] = None,
    ) -> dict:
        """Make an HTTP request using the browser's session."""
        tab = browser_manager.get_tab()
        if tab is None:
            return {"status": "error", "message": "No browser tab available"}
        
        try:
            headers_list = None
            if headers:
                headers_list = [{"name": k, "value": v} for k, v in headers.items()]
            
            method_lower = method.lower()
            
            if method_lower == "get":
                response = await tab.request.get(url, headers=headers_list, params=params)
            elif method_lower == "post":
                response = await tab.request.post(url, headers=headers_list, data=body, params=params)
            elif method_lower == "put":
                response = await tab.request.put(url, headers=headers_list, data=body, params=params)
            elif method_lower == "patch":
                response = await tab.request.patch(url, headers=headers_list, data=body, params=params)
            elif method_lower == "delete":
                response = await tab.request.delete(url, headers=headers_list, params=params)
            elif method_lower == "head":
                response = await tab.request.head(url, headers=headers_list, params=params)
            else:
                return {"status": "error", "message": f"Unsupported method: {method}"}
            
            return {
                "status": "success",
                "status_code": response.status_code,
                "ok": response.ok,
                "url": response.url,
                "headers": response.headers,
                "text": response.text[:10000] if response.text else None,
                "content_length": len(response.content) if response.content else 0,
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def check_authentication(
        self,
        check_url: str,
        indicators: Optional[list[str]] = None,
    ) -> dict:
        """Check if the session is authenticated."""
        tab = browser_manager.get_tab()
        if tab is None:
            return {"status": "error", "message": "No browser tab available"}
        
        try:
            response = await tab.request.get(check_url)
            
            if response.status_code == 401:
                return {
                    "status": "success",
                    "authenticated": False,
                    "reason": "401 Unauthorized",
                }
            
            if response.status_code == 302 or response.status_code == 301:
                return {
                    "status": "success",
                    "authenticated": False,
                    "reason": "Redirected (likely to login)",
                }
            
            if indicators:
                text = response.text or ""
                for indicator in indicators:
                    if indicator in text:
                        return {
                            "status": "success",
                            "authenticated": False,
                            "reason": f"Found indicator: {indicator}",
                        }
            
            return {
                "status": "success",
                "authenticated": response.ok,
                "status_code": response.status_code,
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}


session_manager = SessionManager()
