"""
Network monitoring and interception module for PyPen MCP.

Provides tools for monitoring, intercepting, and manipulating network traffic.
"""

import asyncio
import base64
import json
from typing import Optional, Callable, Any
from pydoll.protocol.network.events import NetworkEvent, RequestWillBeSentEvent, ResponseReceivedEvent, LoadingFailedEvent
from pydoll.protocol.fetch.events import FetchEvent, RequestPausedEvent, AuthRequiredEvent
from pydoll.protocol.network.types import ErrorReason
from pydoll.protocol.fetch.types import AuthChallengeResponseType, HeaderEntry

from .browser import browser_manager


class NetworkManager:
    """Manages network monitoring and interception for pentesting."""
    
    def __init__(self):
        self._network_enabled = False
        self._fetch_enabled = False
        self._intercept_handlers: list[Callable] = []
        self._captured_requests: list[dict] = []
        self._captured_responses: list[dict] = []
    
    async def enable_monitoring(self) -> dict:
        """Enable network event monitoring."""
        tab = browser_manager.get_tab()
        if tab is None:
            return {"status": "error", "message": "No browser tab available"}
        
        await tab.enable_network_events()
        self._network_enabled = True
        
        async def capture_request(event: RequestWillBeSentEvent):
            self._captured_requests.append(dict(event))
        
        async def capture_response(event: ResponseReceivedEvent):
            self._captured_responses.append(dict(event))
        
        await tab.on(NetworkEvent.REQUEST_WILL_BE_SENT, capture_request)
        await tab.on(NetworkEvent.RESPONSE_RECEIVED, capture_response)
        
        return {"status": "success", "message": "Network monitoring enabled"}
    
    async def disable_monitoring(self) -> dict:
        """Disable network event monitoring."""
        tab = browser_manager.get_tab()
        if tab is None:
            return {"status": "error", "message": "No browser tab available"}
        
        await tab.disable_network_events()
        self._network_enabled = False
        
        return {"status": "success", "message": "Network monitoring disabled"}
    
    async def get_network_logs(self, filter_url: Optional[str] = None) -> dict:
        """Get captured network logs."""
        tab = browser_manager.get_tab()
        if tab is None:
            return {"status": "error", "message": "No browser tab available"}
        
        logs = await tab.get_network_logs(filter=filter_url) if filter_url else await tab.get_network_logs()
        
        formatted_logs = []
        for log in logs:
            params = log.get("params", {})
            request = params.get("request", {})
            formatted_logs.append({
                "request_id": params.get("requestId"),
                "url": request.get("url"),
                "method": request.get("method"),
                "headers": request.get("headers", {}),
                "post_data": request.get("postData"),
                "resource_type": params.get("type"),
                "timestamp": params.get("timestamp"),
            })
        
        return {
            "status": "success",
            "count": len(formatted_logs),
            "logs": formatted_logs,
        }
    
    async def get_response_body(self, request_id: str) -> dict:
        """Get the response body for a specific request."""
        tab = browser_manager.get_tab()
        if tab is None:
            return {"status": "error", "message": "No browser tab available"}
        
        try:
            body = await tab.get_network_response_body(request_id)
            return {
                "status": "success",
                "request_id": request_id,
                "body": body,
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def enable_interception(
        self,
        resource_type: Optional[str] = None,
        request_stage: str = "Request",
    ) -> dict:
        """Enable request/response interception."""
        tab = browser_manager.get_tab()
        if tab is None:
            return {"status": "error", "message": "No browser tab available"}
        
        from pydoll.protocol.fetch.types import RequestStage
        
        stage = RequestStage.REQUEST if request_stage == "Request" else RequestStage.RESPONSE
        
        if resource_type:
            await tab.enable_fetch_events(resource_type=resource_type, request_stage=stage)
        else:
            await tab.enable_fetch_events(request_stage=stage)
        
        self._fetch_enabled = True
        
        return {
            "status": "success",
            "message": f"Interception enabled for {resource_type or 'all resources'}",
            "request_stage": request_stage,
        }
    
    async def disable_interception(self) -> dict:
        """Disable request interception."""
        tab = browser_manager.get_tab()
        if tab is None:
            return {"status": "error", "message": "No browser tab available"}
        
        await tab.disable_fetch_events()
        self._fetch_enabled = False
        
        return {"status": "success", "message": "Interception disabled"}
    
    async def block_request(self, request_id: str, reason: str = "BLOCKED_BY_CLIENT") -> dict:
        """Block a request with specified error reason."""
        tab = browser_manager.get_tab()
        if tab is None:
            return {"status": "error", "message": "No browser tab available"}
        
        try:
            error_reason = ErrorReason(reason)
            await tab.fail_request(request_id, error_reason)
            return {"status": "success", "message": f"Request {request_id} blocked"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def continue_request(
        self,
        request_id: str,
        url: Optional[str] = None,
        method: Optional[str] = None,
        headers: Optional[list[dict]] = None,
        post_data: Optional[str] = None,
    ) -> dict:
        """Continue a paused request with optional modifications."""
        tab = browser_manager.get_tab()
        if tab is None:
            return {"status": "error", "message": "No browser tab available"}
        
        try:
            encoded_post_data = base64.b64encode(post_data.encode()).decode() if post_data else None
            await tab.continue_request(
                request_id,
                url=url,
                method=method,
                headers=headers,
                post_data=encoded_post_data,
            )
            return {"status": "success", "message": f"Request {request_id} continued"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def fulfill_request(
        self,
        request_id: str,
        response_code: int = 200,
        headers: Optional[list[dict]] = None,
        body: Optional[str] = None,
    ) -> dict:
        """Fulfill a request with a mock response."""
        tab = browser_manager.get_tab()
        if tab is None:
            return {"status": "error", "message": "No browser tab available"}
        
        try:
            encoded_body = base64.b64encode(body.encode()).decode() if body else None
            await tab.fulfill_request(
                request_id,
                response_code=response_code,
                response_headers=headers,
                body=encoded_body,
            )
            return {"status": "success", "message": f"Request {request_id} fulfilled with mock response"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def setup_interception_handler(
        self,
        block_patterns: Optional[list[str]] = None,
        modify_headers: Optional[dict] = None,
        mock_responses: Optional[dict] = None,
    ) -> dict:
        """Set up automatic interception handler with rules."""
        tab = browser_manager.get_tab()
        if tab is None:
            return {"status": "error", "message": "No browser tab available"}
        
        block_patterns = block_patterns or []
        modify_headers = modify_headers or {}
        mock_responses = mock_responses or {}
        
        stats = {"blocked": 0, "modified": 0, "mocked": 0, "passed": 0}
        
        async def handler(event: RequestPausedEvent):
            request_id = event["params"]["requestId"]
            url = event["params"]["request"]["url"]
            
            try:
                for pattern in block_patterns:
                    if pattern in url:
                        await tab.fail_request(request_id, ErrorReason.BLOCKED_BY_CLIENT)
                        stats["blocked"] += 1
                        return
                
                for pattern, response_data in mock_responses.items():
                    if pattern in url:
                        body = json.dumps(response_data.get("body", {}))
                        encoded_body = base64.b64encode(body.encode()).decode()
                        await tab.fulfill_request(
                            request_id,
                            response_code=response_data.get("status", 200),
                            body=encoded_body,
                        )
                        stats["mocked"] += 1
                        return
                
                if modify_headers:
                    headers_list = [{"name": k, "value": v} for k, v in modify_headers.items()]
                    await tab.continue_request(request_id, headers=headers_list)
                    stats["modified"] += 1
                    return
                
                await tab.continue_request(request_id)
                stats["passed"] += 1
                
            except Exception as e:
                await tab.continue_request(request_id)
        
        await tab.enable_fetch_events()
        await tab.on(FetchEvent.REQUEST_PAUSED, handler)
        self._fetch_enabled = True
        
        return {
            "status": "success",
            "message": "Interception handler configured",
            "block_patterns": block_patterns,
            "modify_headers": modify_headers,
        }
    
    async def clear_logs(self) -> dict:
        """Clear captured network logs."""
        self._captured_requests.clear()
        self._captured_responses.clear()
        return {"status": "success", "message": "Network logs cleared"}


network_manager = NetworkManager()
