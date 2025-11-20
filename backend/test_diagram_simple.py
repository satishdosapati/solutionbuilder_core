"""
Simple test for AWS Diagram MCP Server using Strands Agent
This matches how the application actually uses the tools
"""

import asyncio
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from strands import Agent
from strands.models import BedrockModel
from services.mcp_client_manager import mcp_client_manager
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_diagram_with_agent():
    """Test diagram generation using Strands Agent (like the app does)"""
    
    print("=" * 80)
    print("Testing AWS Diagram MCP Server via Strands Agent")
    print("=" * 80)
    
    diagram_servers = ["aws-diagram-server"]
    
    try:
        # Get MCP client wrapper
        print("\n1. Connecting to MCP server...")
        mcp_client_wrapper = await mcp_client_manager.get_mcp_client_wrapper(diagram_servers)
        
        async with mcp_client_wrapper as mcp_client:
            # Get tools
            print("\n2. Getting tools...")
            tools = mcp_client.list_tools_sync()
            print(f"   Found {len(tools)} tools:")
            for tool in tools:
                tool_name = getattr(tool, 'tool_name', tool.__class__.__name__)
                print(f"   - {tool_name}")
            
            # Create agent with tools
            print("\n3. Creating agent with tools...")
            # Try to create Bedrock model
            model = None
            if os.getenv('AWS_REGION'):
                try:
                    model_id = os.getenv('BEDROCK_MODEL_ID', "anthropic.claude-3-5-sonnet-20240620-v1:0")
                    model = BedrockModel(model_id=model_id)
                    print(f"   Using Bedrock model: {model_id}")
                except Exception as e:
                    print(f"   ⚠ Could not create Bedrock model: {e}")
            
            agent = Agent(
                name="diagram-test",
                model=model,
                tools=tools,
                system_prompt="You are a helpful assistant that generates AWS architecture diagrams. Call tools directly when asked."
            )
            
            # Test 1: Get examples
            print("\n4. Testing get_diagram_examples via agent...")
            prompt1 = "Call the get_diagram_examples tool to show me example diagram code."
            try:
                response1 = await agent.invoke_async(prompt1)
                print(f"   ✓ Agent responded")
                if hasattr(response1, 'message') and isinstance(response1.message, dict):
                    content = response1.message.get('content', [])
                    print(f"   Response content type: {type(content)}")
                    if isinstance(content, list):
                        for i, item in enumerate(content[:2]):
                            if isinstance(item, dict) and 'text' in item:
                                text = item['text']
                                print(f"   Content {i}: {len(text)} chars")
                                print(f"   Preview: {text[:300]}...")
            except Exception as e:
                print(f"   ✗ Failed: {e}")
                import traceback
                traceback.print_exc()
            
            # Test 2: Generate diagram
            print("\n5. Testing generate_diagram via agent...")
            diagram_code = """from diagrams import Diagram
from diagrams.aws.compute import Lambda
from diagrams.aws.database import Dynamodb
from diagrams.aws.network import APIGateway

with Diagram("Test App", show=False):
    api = APIGateway("API")
    func = Lambda("Function")
    db = Dynamodb("Database")
    api >> func >> db"""
            
            prompt2 = f"""Call the generate_diagram tool with this Python code:
{diagram_code}

Return the SVG diagram directly."""
            
            try:
                response2 = await agent.invoke_async(prompt2)
                print(f"   ✓ Agent responded")
                if hasattr(response2, 'message') and isinstance(response2.message, dict):
                    content = response2.message.get('content', [])
                    if isinstance(content, list):
                        for i, item in enumerate(content):
                            if isinstance(item, dict):
                                if 'text' in item:
                                    text = item['text']
                                    print(f"   Content {i} (text): {len(text)} chars")
                                    if '<svg' in text.lower():
                                        print(f"   ✓ Contains SVG!")
                                        # Save SVG to file for inspection
                                        with open('test_diagram_output.svg', 'w', encoding='utf-8') as f:
                                            # Extract SVG if wrapped
                                            import re
                                            svg_match = re.search(r'<svg[^>]*>.*?</svg>', text, re.DOTALL | re.IGNORECASE)
                                            if svg_match:
                                                f.write(svg_match.group(0))
                                                print(f"   ✓ Saved SVG to test_diagram_output.svg")
                                            else:
                                                f.write(text)
                                                print(f"   ⚠ Saved raw content to test_diagram_output.svg")
                                    else:
                                        print(f"   Preview: {text[:200]}...")
                                elif 'tool_use_id' in item:
                                    print(f"   Content {i}: Tool use result")
            except Exception as e:
                print(f"   ✗ Failed: {e}")
                import traceback
                traceback.print_exc()
        
        await mcp_client_manager.release_mcp_client()
        
        print("\n" + "=" * 80)
        print("Test completed! Check test_diagram_output.svg if generated.")
        print("=" * 80)
        return True
        
    except Exception as e:
        print(f"\n✗ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_diagram_with_agent())
    sys.exit(0 if success else 1)

