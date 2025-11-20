"""
Test script for AWS Diagram MCP Server
Tests the diagram server directly to verify functionality and understand response format
"""

import asyncio
import logging
import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from services.mcp_client_manager import mcp_client_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_diagram_mcp_server():
    """Test the AWS Diagram MCP Server directly"""
    
    print("=" * 80)
    print("Testing AWS Diagram MCP Server")
    print("=" * 80)
    
    # Use the same MCP client manager as the application
    diagram_servers = ["aws-diagram-server"]
    
    try:
        # Get MCP client wrapper from singleton manager
        print("\n1. Connecting to MCP server...")
        mcp_client_wrapper = await mcp_client_manager.get_mcp_client_wrapper(diagram_servers)
        
        # Execute with MCP tools - use the wrapper for proper context management
        async with mcp_client_wrapper as mcp_client:
            # List available tools
            print("\n2. Listing available tools...")
            tools = mcp_client.list_tools_sync()
            print(f"   Found {len(tools)} tools:")
            for tool in tools:
                tool_name = getattr(tool, 'tool_name', tool.__class__.__name__)
                print(f"   - {tool_name}")
            
            # Find the diagram tools
            diagram_tools = {}
            for tool in tools:
                tool_name = getattr(tool, 'tool_name', tool.__class__.__name__)
                if 'diagram' in tool_name.lower():
                    diagram_tools[tool_name] = tool
            
            if not diagram_tools:
                print("   ⚠ No diagram tools found!")
                return False
            
            # Test 1: Get diagram examples
            print("\n3. Testing get_diagram_examples...")
            try:
                # Use the underlying MCP session directly
                # The mcp_client should have a _session or similar attribute
                if hasattr(mcp_client, '_background_thread_session'):
                    session = mcp_client._background_thread_session
                    examples_result = await session.call_tool("get_diagram_examples", {})
                elif hasattr(mcp_client, 'call_tool'):
                    examples_result = await mcp_client.call_tool("get_diagram_examples", {})
                else:
                    # Try call_tool_async with correct signature
                    examples_result = await mcp_client.call_tool_async("get_diagram_examples", {})
                print(f"   ✓ get_diagram_examples succeeded")
                print(f"   Result type: {type(examples_result)}")
                
                # Try to extract the examples
                if isinstance(examples_result, dict):
                    print(f"   Result keys: {list(examples_result.keys())}")
                    if 'content' in examples_result:
                        content = examples_result['content']
                        if isinstance(content, list):
                            print(f"   Content is a list with {len(content)} items")
                            for i, item in enumerate(content[:3]):  # Show first 3
                                print(f"   Item {i}: {str(item)[:200]}...")
                        else:
                            print(f"   Content preview: {str(content)[:500]}...")
                    else:
                        print(f"   Full result: {json.dumps(examples_result, indent=2)[:1000]}...")
                else:
                    print(f"   Result preview: {str(examples_result)[:500]}...")
                    
            except Exception as e:
                print(f"   ✗ get_diagram_examples failed: {e}")
                import traceback
                traceback.print_exc()
            
            # Test 2: Generate a simple diagram
            print("\n4. Testing generate_diagram with simple example...")
            
            # First, let's try with imports (as shown in documentation)
            simple_diagram_code = """from diagrams import Diagram
from diagrams.aws.compute import Lambda
from diagrams.aws.database import Dynamodb
from diagrams.aws.network import APIGateway

with Diagram("Test Serverless Application", show=False):
    api = APIGateway("API Gateway")
    function = Lambda("Function")
    database = Dynamodb("DynamoDB")
    api >> function >> database"""
            
            try:
                print("   Attempting with imports...")
                if hasattr(mcp_client, '_background_thread_session'):
                    session = mcp_client._background_thread_session
                    generate_result = await session.call_tool("generate_diagram", {"code": simple_diagram_code})
                elif hasattr(mcp_client, 'call_tool'):
                    generate_result = await mcp_client.call_tool("generate_diagram", {"code": simple_diagram_code})
                else:
                    generate_result = await mcp_client.call_tool_async("generate_diagram", {"code": simple_diagram_code})
                print(f"   ✓ generate_diagram succeeded (with imports)")
                print(f"   Result type: {type(generate_result)}")
                
                if isinstance(generate_result, dict):
                    print(f"   Result keys: {list(generate_result.keys())}")
                    if 'content' in generate_result:
                        content = generate_result['content']
                        if isinstance(content, list):
                            for i, item in enumerate(content):
                                if isinstance(item, dict) and 'text' in item:
                                    text = item['text']
                                    print(f"   Content item {i} (text): {len(text)} chars")
                                    if '<svg' in text.lower():
                                        print(f"   ✓ Contains SVG!")
                                        print(f"   SVG preview: {text[:300]}...")
                                    else:
                                        print(f"   Preview: {text[:200]}...")
                                else:
                                    print(f"   Content item {i}: {str(item)[:200]}...")
                        else:
                            content_str = str(content)
                            print(f"   Content length: {len(content_str)} chars")
                            if '<svg' in content_str.lower():
                                print(f"   ✓ Contains SVG!")
                                print(f"   SVG preview: {content_str[:300]}...")
                            else:
                                print(f"   Preview: {content_str[:500]}...")
                    else:
                        print(f"   Full result: {json.dumps(generate_result, indent=2)[:2000]}...")
                else:
                    result_str = str(generate_result)
                    print(f"   Result length: {len(result_str)} chars")
                    if '<svg' in result_str.lower():
                        print(f"   ✓ Contains SVG!")
                        print(f"   SVG preview: {result_str[:300]}...")
                    else:
                        print(f"   Preview: {result_str[:500]}...")
                        
            except Exception as e:
                print(f"   ✗ generate_diagram failed (with imports): {e}")
                import traceback
                traceback.print_exc()
                
                # Try without imports (in case library is pre-imported)
                print("\n   Attempting without imports...")
                simple_diagram_code_no_imports = """with Diagram("Test Serverless Application", show=False):
    api = APIGateway("API Gateway")
    function = Lambda("Function")
    database = Dynamodb("DynamoDB")
    api >> function >> database"""
                
                try:
                    if hasattr(mcp_client, '_background_thread_session'):
                        session = mcp_client._background_thread_session
                        generate_result = await session.call_tool("generate_diagram", {"code": simple_diagram_code_no_imports})
                    elif hasattr(mcp_client, 'call_tool'):
                        generate_result = await mcp_client.call_tool("generate_diagram", {"code": simple_diagram_code_no_imports})
                    else:
                        generate_result = await mcp_client.call_tool_async("generate_diagram", {"code": simple_diagram_code_no_imports})
                    print(f"   ✓ generate_diagram succeeded (without imports)")
                    print(f"   Result type: {type(generate_result)}")
                    if isinstance(generate_result, dict):
                        print(f"   Result keys: {list(generate_result.keys())}")
                    else:
                        result_str = str(generate_result)
                        if '<svg' in result_str.lower():
                            print(f"   ✓ Contains SVG!")
                            print(f"   SVG preview: {result_str[:300]}...")
                except Exception as e2:
                    print(f"   ✗ generate_diagram failed (without imports): {e2}")
                    import traceback
                    traceback.print_exc()
            
            # Test 3: List icons
            print("\n5. Testing list_icons...")
            try:
                if hasattr(mcp_client, '_background_thread_session'):
                    session = mcp_client._background_thread_session
                    icons_result = await session.call_tool("list_icons", {})
                elif hasattr(mcp_client, 'call_tool'):
                    icons_result = await mcp_client.call_tool("list_icons", {})
                else:
                    icons_result = await mcp_client.call_tool_async("list_icons", {})
                print(f"   ✓ list_icons succeeded")
                print(f"   Result type: {type(icons_result)}")
                if isinstance(icons_result, dict):
                    print(f"   Result keys: {list(icons_result.keys())}")
                else:
                    print(f"   Preview: {str(icons_result)[:500]}...")
            except Exception as e:
                print(f"   ✗ list_icons failed: {e}")
                import traceback
                traceback.print_exc()
        
            # Release the MCP client usage
            await mcp_client_manager.release_mcp_client()
        
        print("\n" + "=" * 80)
        print("Test completed!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n✗ Failed to connect to MCP server: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = asyncio.run(test_diagram_mcp_server())
    sys.exit(0 if success else 1)

