"""
Test with simplest possible diagram to verify generate_diagram works
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


async def test_simple_diagram():
    """Test with the simplest possible diagram"""
    
    print("=" * 80)
    print("Testing Simplest Diagram")
    print("=" * 80)
    
    diagram_servers = ["aws-diagram-server"]
    
    try:
        mcp_client_wrapper = await mcp_client_manager.get_mcp_client_wrapper(diagram_servers)
        
        async with mcp_client_wrapper as mcp_client:
            tools = mcp_client.list_tools_sync()
            print(f"\nFound {len(tools)} tools")
            
            # Create agent
            model = None
            if os.getenv('AWS_REGION'):
                try:
                    model_id = os.getenv('BEDROCK_MODEL_ID', "anthropic.claude-3-5-sonnet-20240620-v1:0")
                    model = BedrockModel(model_id=model_id)
                except Exception as e:
                    print(f"⚠ Could not create Bedrock model: {e}")
            
            agent = Agent(
                name="simple-diagram-test",
                model=model,
                tools=tools,
                system_prompt="""You are a helpful assistant. When asked to generate a diagram:
1. Call get_diagram_examples first
2. Use the SIMPLEST possible code matching the examples
3. DO NOT include any import statements
4. Call generate_diagram with the code
5. Return the result directly"""
            )
            
            # Simplest possible diagram
            print("\nTesting with simplest diagram code...")
            prompt = """Call get_diagram_examples first, then generate a diagram using the SIMPLEST possible code from the examples. Use code like: with Diagram("Test", show=False): ELB("lb") >> EC2("web")"""
            
            try:
                response = await agent.invoke_async(prompt)
                print(f"\n✓ Agent responded")
                
                if hasattr(response, 'message') and isinstance(response.message, dict):
                    content = response.message.get('content', [])
                    if isinstance(content, list):
                        for i, item in enumerate(content):
                            if isinstance(item, dict):
                                if 'text' in item:
                                    text = item['text']
                                    print(f"\nContent {i} (text): {len(text)} chars")
                                    
                                    # Check for image data
                                    if 'data:image' in text.lower():
                                        print("✓ Contains image data!")
                                        # Extract image type
                                        if 'data:image/png' in text.lower():
                                            print("✓ PNG image detected")
                                        elif 'data:image/svg' in text.lower():
                                            print("✓ SVG image detected")
                                        # Save to file
                                        import re
                                        img_match = re.search(r'data:image/([^;]+);base64,([A-Za-z0-9+/=]+)', text, re.IGNORECASE)
                                        if img_match:
                                            img_type = img_match.group(1)
                                            img_data = img_match.group(2)
                                            filename = f'simple_test_diagram.{img_type}'
                                            import base64
                                            with open(filename, 'wb') as f:
                                                f.write(base64.b64decode(img_data))
                                            print(f"✓ Saved image to {filename}")
                                    elif '<svg' in text.lower():
                                        print("✓ Contains SVG!")
                                        import re
                                        svg_match = re.search(r'<svg[^>]*>.*?</svg>', text, re.DOTALL | re.IGNORECASE)
                                        if svg_match:
                                            with open('simple_test_diagram.svg', 'w', encoding='utf-8') as f:
                                                f.write(svg_match.group(0))
                                            print("✓ Saved SVG to simple_test_diagram.svg")
                                    else:
                                        print(f"Preview: {text[:300]}...")
                                        
            except Exception as e:
                print(f"\n✗ Failed: {e}")
                import traceback
                traceback.print_exc()
        
        await mcp_client_manager.release_mcp_client()
        
        print("\n" + "=" * 80)
        print("Simple diagram test completed!")
        print("=" * 80)
        return True
        
    except Exception as e:
        print(f"\n✗ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_simple_diagram())
    sys.exit(0 if success else 1)

