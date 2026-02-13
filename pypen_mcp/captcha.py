"""
Captcha handling module for PyPen MCP.

Provides tools for automated captcha bypass (Turnstile) and human intervention
request for captchas that cannot be automatically solved.
"""

import asyncio
from typing import Optional
from datetime import datetime
from enum import Enum

from .browser import browser_manager


class CaptchaType(str, Enum):
    """Types of captchas that may be encountered."""
    TURNSTILE = "turnstile"
    RECAPTCHA_V2 = "recaptcha_v2"
    RECAPTCHA_V3 = "recaptcha_v3"
    HCAPTCHA = "hcaptcha"
    IMAGE_CHALLENGE = "image_challenge"
    PUZZLE = "puzzle"
    UNKNOWN = "unknown"


class HumanInterventionRequest:
    """Represents a request for human intervention."""
    
    def __init__(
        self,
        request_id: str,
        captcha_type: CaptchaType,
        message: str,
        url: str,
        screenshot_path: Optional[str] = None,
        created_at: Optional[datetime] = None,
    ):
        self.request_id = request_id
        self.captcha_type = captcha_type
        self.message = message
        self.url = url
        self.screenshot_path = screenshot_path
        self.created_at = created_at or datetime.now()
        self.resolved = False
        self.resolution: Optional[str] = None


class CaptchaManager:
    """Manages captcha interactions and human intervention requests."""
    
    def __init__(self):
        self._auto_solve_enabled = False
        self._pending_interventions: dict[str, HumanInterventionRequest] = []
    
    async def enable_turnstile_bypass(
        self,
        time_to_wait_captcha: float = 5.0,
    ) -> dict:
        """Enable automatic Cloudflare Turnstile bypass.
        
        This enables PyDoll's built-in Turnstile interaction, which automatically
        detects and clicks the Turnstile checkbox. Success depends on IP reputation
        and browser fingerprint - this is NOT a magic bypass.
        """
        tab = browser_manager.get_tab()
        if tab is None:
            return {"status": "error", "message": "No browser tab available"}
        
        try:
            await tab.enable_auto_solve_cloudflare_captcha()
            self._auto_solve_enabled = True
            
            return {
                "status": "success",
                "message": "Turnstile auto-bypass enabled. Navigate to the protected page.",
                "time_to_wait_captcha": time_to_wait_captcha,
                "notes": [
                    "Success depends on IP reputation and browser fingerprint",
                    "This clicks the checkbox - it does NOT solve image challenges",
                    "Use residential proxies for best results",
                ],
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def disable_turnstile_bypass(self) -> dict:
        """Disable automatic Turnstile bypass."""
        tab = browser_manager.get_tab()
        if tab is None:
            return {"status": "error", "message": "No browser tab available"}
        
        try:
            await tab.disable_auto_solve_cloudflare_captcha()
            self._auto_solve_enabled = False
            
            return {"status": "success", "message": "Turnstile auto-bypass disabled"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def bypass_turnstile_context(
        self,
        time_to_wait_captcha: float = 5.0,
    ) -> dict:
        """
        Use context manager for Turnstile bypass.
        
        This waits for the captcha to appear, clicks it, and waits for resolution.
        Use this when you want to block until the captcha is handled.
        
        Note: The actual bypass must be done during navigation. This method
        returns instructions for using the context manager pattern.
        """
        tab = browser_manager.get_tab()
        if tab is None:
            return {"status": "error", "message": "No browser tab available"}
        
        return {
            "status": "success",
            "message": "Use the context manager pattern for blocking bypass",
            "pattern": """
# Python code pattern for context manager bypass:
async with tab.expect_and_bypass_cloudflare_captcha(time_to_wait_captcha=5.0):
    await tab.go_to('https://protected-site.com')
# Code here runs after captcha is clicked
""",
            "alternative": "Use enable_turnstile_bypass for background processing",
        }
    
    async def request_human_intervention(
        self,
        captcha_type: str,
        message: str,
        take_screenshot: bool = True,
    ) -> dict:
        """
        Request human intervention for an unsolvable captcha.
        
        Use this when the automation encounters a captcha it cannot solve
        (e.g., ReCAPTCHA v2 image challenges, hCaptcha puzzles, etc.).
        
        This creates an intervention request that the human operator must
        acknowledge and resolve. The automation should wait for resolution.
        """
        tab = browser_manager.get_tab()
        if tab is None:
            return {"status": "error", "message": "No browser tab available"}
        
        try:
            import uuid
            request_id = str(uuid.uuid4())[:8]
            
            # Get current URL
            current_url = await tab.current_url
            
            # Take screenshot if requested
            screenshot_path = None
            if take_screenshot:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                screenshot_path = f"/tmp/pypen_intervention_{request_id}_{timestamp}.png"
                try:
                    await tab.take_screenshot(path=screenshot_path)
                except:
                    screenshot_path = None
            
            # Create intervention request
            intervention = HumanInterventionRequest(
                request_id=request_id,
                captcha_type=CaptchaType(captcha_type.lower()) if captcha_type.lower() in [c.value for c in CaptchaType] else CaptchaType.UNKNOWN,
                message=message,
                url=current_url,
                screenshot_path=screenshot_path,
            )
            
            self._pending_interventions.append(intervention)
            
            return {
                "status": "intervention_required",
                "request_id": request_id,
                "captcha_type": captcha_type,
                "message": message,
                "url": current_url,
                "screenshot": screenshot_path,
                "instructions": [
                    "HUMAN INTERVENTION REQUIRED",
                    f"Request ID: {request_id}",
                    f"URL: {current_url}",
                    f"Captcha Type: {captcha_type}",
                    f"Message: {message}",
                    "",
                    "Please solve the captcha in the browser window.",
                    f"After solving, use 'captcha_resolve' with request_id: {request_id}",
                ],
                "action_required": "human_intervention",
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def get_pending_interventions(self) -> dict:
        """Get all pending human intervention requests."""
        pending = [
            {
                "request_id": req.request_id,
                "captcha_type": req.captcha_type.value,
                "message": req.message,
                "url": req.url,
                "screenshot": req.screenshot_path,
                "created_at": req.created_at.isoformat(),
                "resolved": req.resolved,
            }
            for req in self._pending_interventions
            if not req.resolved
        ]
        
        return {
            "status": "success",
            "pending_count": len(pending),
            "interventions": pending,
        }
    
    async def resolve_intervention(
        self,
        request_id: str,
        resolution: str = "solved",
    ) -> dict:
        """
        Mark an intervention request as resolved.
        
        Call this after a human has solved the captcha to allow
        the automation to continue.
        """
        for intervention in self._pending_interventions:
            if intervention.request_id == request_id and not intervention.resolved:
                intervention.resolved = True
                intervention.resolution = resolution
                return {
                    "status": "success",
                    "message": f"Intervention {request_id} marked as resolved",
                    "resolution": resolution,
                }
        
        return {
            "status": "error",
            "message": f"No pending intervention found with ID: {request_id}",
        }
    
    async def wait_for_intervention_resolution(
        self,
        request_id: str,
        timeout: float = 300.0,
        poll_interval: float = 2.0,
    ) -> dict:
        """
        Wait for a human intervention to be resolved.
        
        This blocks until the intervention is marked as resolved or timeout expires.
        Use this to pause automation while waiting for human to solve captcha.
        """
        start_time = asyncio.get_event_loop().time()
        
        while True:
            for intervention in self._pending_interventions:
                if intervention.request_id == request_id:
                    if intervention.resolved:
                        return {
                            "status": "success",
                            "message": f"Intervention {request_id} resolved",
                            "resolution": intervention.resolution,
                        }
                    break
            
            elapsed = asyncio.get_event_loop().time() - start_time
            if elapsed >= timeout:
                return {
                    "status": "timeout",
                    "message": f"Intervention {request_id} not resolved within {timeout}s",
                }
            
            await asyncio.sleep(poll_interval)
    
    async def detect_captcha_type(self) -> dict:
        """
        Detect what type of captcha is present on the current page.
        
        Scans the page for common captcha indicators and returns the likely type.
        """
        tab = browser_manager.get_tab()
        if tab is None:
            return {"status": "error", "message": "No browser tab available"}
        
        detection_script = """
        (function() {
            var result = {
                detected: false,
                type: 'none',
                indicators: []
            };
            
            // Check for Cloudflare Turnstile
            if (document.querySelector('iframe[src*="challenges.cloudflare.com"]') ||
                document.querySelector('[data-sitekey]')) {
                result.detected = true;
                result.type = 'turnstile';
                result.indicators.push('Cloudflare Turnstile iframe or sitekey found');
            }
            
            // Check for reCAPTCHA
            if (document.querySelector('.g-recaptcha') ||
                document.querySelector('iframe[src*="recaptcha"]') ||
                document.querySelector('#recaptcha-element') ||
                window.grecaptcha) {
                result.detected = true;
                result.type = 'recaptcha_v2';
                result.indicators.push('reCAPTCHA element found');
            }
            
            // Check for hCaptcha
            if (document.querySelector('.h-captcha') ||
                document.querySelector('iframe[src*="hcaptcha"]') ||
                window.hcaptcha) {
                result.detected = true;
                result.type = 'hcaptcha';
                result.indicators.push('hCaptcha element found');
            }
            
            // Check for image challenge indicators
            if (document.querySelector('[class*="challenge"]') ||
                document.querySelector('[class*="puzzle"]') ||
                document.querySelector('img[src*="captcha"]')) {
                result.detected = true;
                if (result.type === 'none') {
                    result.type = 'image_challenge';
                }
                result.indicators.push('Challenge/puzzle elements found');
            }
            
            return result;
        })();
        """
        
        try:
            result = await tab.execute_script(detection_script)
            
            # Parse the result
            if isinstance(result, dict) and 'result' in result:
                inner = result.get('result', {}).get('result', {})
                if isinstance(inner, dict):
                    return {
                        "status": "success",
                        "detected": inner.get('detected', False),
                        "type": inner.get('type', 'none'),
                        "indicators": inner.get('indicators', []),
                    }
            
            return {
                "status": "success",
                "detected": False,
                "type": "none",
                "indicators": [],
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def handle_captcha_automatically(
        self,
        timeout: float = 30.0,
    ) -> dict:
        """
        Attempt to automatically handle any detected captcha.
        
        For Turnstile: Uses built-in bypass mechanism.
        For others: Returns need for human intervention.
        """
        tab = browser_manager.get_tab()
        if tab is None:
            return {"status": "error", "message": "No browser tab available"}
        
        # First detect what type of captcha we have
        detection = await self.detect_captcha_type()
        
        if not detection.get("detected"):
            return {
                "status": "success",
                "message": "No captcha detected on page",
            }
        
        captcha_type = detection.get("type", "unknown")
        
        if captcha_type == "turnstile":
            # Try automatic bypass
            try:
                await tab.enable_auto_solve_cloudflare_captcha()
                await asyncio.sleep(5)  # Wait for processing
                await tab.disable_auto_solve_cloudflare_captcha()
                
                # Check if solved
                new_detection = await self.detect_captcha_type()
                if not new_detection.get("detected"):
                    return {
                        "status": "success",
                        "message": "Turnstile captcha automatically solved",
                    }
                
                # Still detected - need intervention
                return await self.request_human_intervention(
                    captcha_type="turnstile",
                    message="Turnstile bypass failed - likely IP/fingerprint issue",
                )
            except Exception as e:
                return await self.request_human_intervention(
                    captcha_type="turnstile",
                    message=f"Turnstile bypass error: {str(e)}",
                )
        
        # For ReCAPTCHA v2, hCaptcha, image challenges - need human
        return await self.request_human_intervention(
            captcha_type=captcha_type,
            message=f"Automatic bypass not available for {captcha_type}",
        )


captcha_manager = CaptchaManager()
