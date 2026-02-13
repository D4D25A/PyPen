"""
Test script to validate browser session persistence across MCP operations.
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pypen_mcp.browser import browser_manager
from pypen_mcp.dom import dom_manager
from pypen_mcp.javascript import js_manager
from pypen_mcp.session import session_manager
from pypen_mcp.network import network_manager


async def test_session_persistence():
    """Test that browser session persists across multiple operations."""
    
    print("=" * 60)
    print("Testing Browser Session Persistence")
    print("=" * 60)
    
    # Test 1: Verify no browser initially
    print("\n[1] Checking initial state...")
    assert not browser_manager.is_running(), "Browser should not be running initially"
    assert browser_manager.get_tab() is None, "Tab should be None initially"
    print("    ✓ No browser running initially")
    
    # Test 2: Launch browser
    print("\n[2] Launching browser...")
    result = await browser_manager.launch(headless=True)
    assert result["status"] == "success", f"Launch failed: {result}"
    assert browser_manager.is_running(), "Browser should be running after launch"
    assert browser_manager.get_tab() is not None, "Tab should not be None after launch"
    print(f"    ✓ Browser launched: {result['message']}")
    
    # Store tab reference to verify it's the same instance
    tab_ref = browser_manager.get_tab()
    print(f"    ✓ Tab reference stored: {id(tab_ref)}")
    
    # Test 3: Navigate to a page
    print("\n[3] Navigating to example.com...")
    result = await browser_manager.navigate("https://example.com")
    assert result["status"] == "success", f"Navigation failed: {result}"
    print(f"    ✓ Navigated to: {result['current_url']}")
    print(f"    ✓ Page title: {result['title']}")
    
    # Test 4: Verify same tab instance after navigation
    assert browser_manager.get_tab() is tab_ref, "Tab instance should persist after navigation"
    print("    ✓ Same tab instance after navigation")
    
    # Test 5: DOM operations on the same session
    print("\n[4] Testing DOM operations on active session...")
    result = await dom_manager.get_page_source()
    assert result["status"] == "success", f"Get source failed: {result}"
    assert "example" in result["source"].lower(), "Page source should contain 'example'"
    print(f"    ✓ Got page source ({len(result['source'])} chars)")
    
    result = await dom_manager.find_element(tag_name="h1")
    assert result["status"] == "success", f"Find element failed: {result}"
    print(f"    ✓ Found h1 element: {result.get('text', 'N/A')}")
    
    # Test 6: JavaScript execution on the same session
    print("\n[5] Testing JavaScript execution on active session...")
    result = await js_manager.execute_script("return document.title")
    assert result["status"] == "success", f"JS execute failed: {result}"
    print(f"    ✓ JS returned: {result['result']}")
    
    result = await js_manager.get_local_storage()
    assert result["status"] == "success", f"Get localStorage failed: {result}"
    print(f"    ✓ Got localStorage ({len(result['storage'])} items)")
    
    # Test 7: Session operations
    print("\n[6] Testing session operations...")
    result = await session_manager.get_cookies()
    assert result["status"] == "success", f"Get cookies failed: {result}"
    print(f"    ✓ Got cookies ({result['count']} cookies)")
    
    # Test 8: Navigate to another page and verify session persists
    print("\n[7] Navigating to another page...")
    result = await browser_manager.navigate("https://httpbin.org")
    assert result["status"] == "success", f"Navigation failed: {result}"
    print(f"    ✓ Navigated to: {result['current_url']}")
    
    # Verify same tab still
    assert browser_manager.get_tab() is tab_ref, "Tab instance should persist across navigations"
    print("    ✓ Same tab instance across navigations")
    
    # Test 9: Set a cookie and verify persistence
    print("\n[8] Testing cookie persistence...")
    result = await session_manager.set_cookie(
        name="test_cookie",
        value="test_value_123",
        domain="httpbin.org"
    )
    assert result["status"] == "success", f"Set cookie failed: {result}"
    print("    ✓ Set test_cookie")
    
    result = await session_manager.get_cookie("test_cookie")
    assert result["status"] == "success", f"Get cookie failed: {result}"
    print(f"    ✓ Retrieved cookie: {result['cookie']}")
    
    # Test 10: Multiple DOM operations in sequence
    print("\n[9] Testing multiple sequential operations...")
    for i in range(3):
        result = await dom_manager.scroll_page(direction="down", amount=100)
        assert result["status"] == "success", f"Scroll {i+1} failed: {result}"
    print("    ✓ Completed 3 scroll operations")
    
    result = await js_manager.execute_script("return window.scrollY")
    assert result["status"] == "success", f"Get scrollY failed: {result}"
    print(f"    ✓ Scroll position: {result['result']}")
    
    # Test 11: Verify browser still running
    print("\n[10] Final state verification...")
    assert browser_manager.is_running(), "Browser should still be running"
    assert browser_manager.get_tab() is tab_ref, "Tab instance should still be the same"
    print("    ✓ Browser still running with same session")
    
    # Test 12: Close browser
    print("\n[11] Closing browser...")
    result = await browser_manager.close()
    assert result["status"] == "success", f"Close failed: {result}"
    assert not browser_manager.is_running(), "Browser should not be running after close"
    assert browser_manager.get_tab() is None, "Tab should be None after close"
    print("    ✓ Browser closed successfully")
    
    # Test 13: Verify operations fail after close
    print("\n[12] Verifying operations fail after close...")
    result = await browser_manager.navigate("https://example.com")
    assert result["status"] == "error", "Navigate should fail after close"
    print(f"    ✓ Navigate correctly failed: {result['message']}")
    
    result = await dom_manager.get_page_source()
    assert result["status"] == "error", "DOM operation should fail after close"
    print(f"    ✓ DOM operation correctly failed: {result['message']}")
    
    result = await js_manager.execute_script("return 1")
    assert result["status"] == "error", "JS execution should fail after close"
    print(f"    ✓ JS execution correctly failed: {result['message']}")
    
    print("\n" + "=" * 60)
    print("All tests passed! Session persistence validated.")
    print("=" * 60)
    
    return True


async def test_singleton_pattern():
    """Test that BrowserManager is truly a singleton."""
    print("\n" + "=" * 60)
    print("Testing Singleton Pattern")
    print("=" * 60)
    
    from pypen_mcp.browser import BrowserManager
    
    # Get multiple instances
    manager1 = BrowserManager()
    manager2 = BrowserManager()
    browser_manager_ref = browser_manager
    
    print(f"\n[1] Instance IDs:")
    print(f"    manager1: {id(manager1)}")
    print(f"    manager2: {id(manager2)}")
    print(f"    browser_manager: {id(browser_manager_ref)}")
    
    assert manager1 is manager2, "Manager instances should be identical"
    assert manager1 is browser_manager, "Manager should be same as module instance"
    print("\n    ✓ All instances are identical (singleton works)")
    
    # Test state sharing
    print("\n[2] Testing state sharing...")
    result = await manager1.launch(headless=True)
    assert result["status"] == "success", f"Launch failed: {result}"
    print("    ✓ Launched browser via manager1")
    
    assert manager2.is_running(), "manager2 should see browser running"
    print("    ✓ manager2 sees browser running")
    
    assert browser_manager_ref.is_running(), "browser_manager should see browser running"
    print("    ✓ browser_manager sees browser running")
    
    # Close via different reference
    result = await browser_manager_ref.close()
    assert result["status"] == "success", f"Close failed: {result}"
    print("    ✓ Closed browser via browser_manager_ref")
    
    assert not manager1.is_running(), "manager1 should see browser closed"
    assert not manager2.is_running(), "manager2 should see browser closed"
    print("    ✓ All references show browser closed")
    
    print("\n" + "=" * 60)
    print("Singleton pattern validated!")
    print("=" * 60)
    
    return True


async def main():
    """Run all tests."""
    try:
        await test_singleton_pattern()
        await test_session_persistence()
        print("\n✅ All validation tests passed!")
        return 0
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        # Try to close browser if it's still running
        if browser_manager.is_running():
            await browser_manager.close()
        return 1


if __name__ == "__main__":
    exit(asyncio.run(main()))
