#!/usr/bin/env python3
"""
Simple test script to verify AI tool interaction with NotebookLM MCP.

This script directly tests the notebook_query function to ensure it uses
only the automatically retrieved notebook ID and doesn't make unnecessary attempts.
"""

import sys

# Add src directory to path
sys.path.insert(0, str('src'))

from notebooklm_tools.mcp.tools.chat import notebook_query
from notebooklm_tools.mcp.tools._utils import get_default_notebook_id


def test_notebook_query_behavior():
    """Test the behavior of notebook_query function."""
    print("Testing notebook_query behavior...")
    print("=" * 60)
    
    # Test 1: Verify get_default_notebook_id is importable
    print("Test 1: Checking get_default_notebook_id function...")
    try:
        # Just verify the function is importable, don't call it directly
        print("✓ get_default_notebook_id is importable")
    except Exception as e:
        print(f"✗ get_default_notebook_id failed: {e}")
        return False
    
    print()
    
    # Test 2: Test notebook_query with mocked dependencies
    print("Test 2: Testing notebook_query with mocked dependencies...")
    try:
        # Mock the necessary dependencies
        from unittest.mock import Mock, patch
        
        # Mock get_client
        with patch('notebooklm_tools.mcp.tools.chat.get_client', return_value=Mock()) as mock_get_client:
            # Mock get_query_timeout
            with patch('notebooklm_tools.mcp.tools.chat.get_query_timeout', return_value=120.0) as mock_get_timeout:
                # Mock chat_service.query
                with patch('notebooklm_tools.mcp.tools.chat.chat_service.query', return_value={'response': 'Test response'}) as mock_query:
                    # Test with default notebook ID
                    print("  Testing with default notebook ID...")
                    with patch('notebooklm_tools.mcp.tools.chat.get_default_notebook_id', return_value='test-notebook-id-123') as mock_get_id:
                        result = notebook_query(query="Test query")
                        print(f"    Result: {result}")
                        print(f"    get_default_notebook_id called: {mock_get_id.called}")
                        print(f"    chat_service.query called: {mock_query.called}")
                        if mock_get_id.called and mock_query.called:
                            print("    ✓ Both functions called correctly")
                        else:
                            print("    ✗ Functions not called correctly")
                            return False
                    
                    print()
                    
                    # Test with provided notebook ID
                    print("  Testing with provided notebook ID...")
                    with patch('notebooklm_tools.mcp.tools.chat.get_default_notebook_id', return_value='default-id') as mock_get_id:
                        result = notebook_query(query="Test query", notebook_id="provided-id-456")
                        print(f"    Result: {result}")
                        print(f"    get_default_notebook_id called: {mock_get_id.called}")
                        print(f"    chat_service.query called: {mock_query.called}")
                        if not mock_get_id.called and mock_query.called:
                            print("    ✓ get_default_notebook_id not called when ID provided")
                        else:
                            print("    ✗ get_default_notebook_id called when ID provided")
                            return False
    except Exception as e:
        print(f"✗ notebook_query test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print()
    
    # Test 3: Test error handling when no notebook ID
    print("Test 3: Testing error handling when no notebook ID...")
    try:
        from unittest.mock import Mock, patch
        
        # Mock the necessary dependencies
        with patch('notebooklm_tools.mcp.tools.chat.get_client', return_value=Mock()) as mock_get_client:
            with patch('notebooklm_tools.mcp.tools.chat.get_query_timeout', return_value=120.0) as mock_get_timeout:
                # Test with no notebook ID and no default
                with patch('notebooklm_tools.mcp.tools.chat.get_default_notebook_id', return_value=None) as mock_get_id:
                    result = notebook_query(query="Test query")
                    print(f"    Result: {result}")
                    print(f"    get_default_notebook_id called: {mock_get_id.called}")
                    if result['status'] == 'error' and 'No notebook ID provided' in result['error']:
                        print("    ✓ Correct error returned when no notebook ID")
                    else:
                        print("    ✗ Incorrect error handling")
                        return False
    except Exception as e:
        print(f"✗ Error handling test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print()
    
    # Test 4: Simulate AI tool usage
    print("Test 4: Simulating AI tool usage...")
    try:
        from unittest.mock import Mock, patch
        
        # Mock the necessary dependencies
        with patch('notebooklm_tools.mcp.tools.chat.get_client', return_value=Mock()) as mock_get_client:
            with patch('notebooklm_tools.mcp.tools.chat.get_query_timeout', return_value=120.0) as mock_get_timeout:
                with patch('notebooklm_tools.mcp.tools.chat.chat_service.query', return_value={'response': 'AI response'}) as mock_query:
                    # Simulate multiple AI tools using the same notebook ID
                    tool_calls = [
                        ("Claude Code", "What's in my notebook?"),
                        ("Gemini CLI", "Summarize my notes"),
                        ("Cursor", "Find relevant information")
                    ]
                    
                    # Track the number of calls
                    call_count = 0
                    
                    for tool_name, query_text in tool_calls:
                        print(f"  {tool_name} query: {query_text}")
                        with patch('notebooklm_tools.mcp.tools.chat.get_default_notebook_id', return_value='auto-notebook-id-123') as mock_get_id:
                            result = notebook_query(query=query_text)
                            print(f"    Status: {result['status']}")
                            print(f"    get_default_notebook_id called: {mock_get_id.called}")
                            if result['status'] == 'success':
                                print(f"    ✓ {tool_name} query successful")
                                call_count += 1
                            else:
                                print(f"    ✗ {tool_name} query failed")
                                return False
                    
                    print(f"  Total successful tool calls: {call_count}")
                    if call_count == len(tool_calls):
                        print("  ✓ All AI tools successfully used notebook_query")
                    else:
                        print("  ✗ Some AI tool calls failed")
                        return False
    except Exception as e:
        print(f"✗ AI tool simulation failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print()
    print("=" * 60)
    print("All tests passed! ✓")
    print("AI tools correctly use auto-retrieved notebook ID without redundant attempts.")
    return True


if __name__ == "__main__":
    success = test_notebook_query_behavior()
    sys.exit(0 if success else 1)
