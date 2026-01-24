"""
Quick Test Script for MCP-Enhanced Chatbot
Run this to verify MCP tools load correctly
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

print("=" * 70)
print("MCP-Enhanced Chatbot - Subprocess Test")
print("=" * 70)

# Test 1: Import chatbot service
print("\n[1/5] Importing EnhancedChatbotService...")
try:
    from finance.services.chatbot_service_enhanced import EnhancedChatbotService
    print("✓ Successfully imported EnhancedChatbotService")
except Exception as e:
    print(f"✗ Failed to import: {e}")
    sys.exit(1)

# Test 2: Initialize chatbot service
print("\n[2/5] Initializing chatbot service...")
try:
    chatbot = EnhancedChatbotService()
    print("✓ Successfully initialized chatbot service")
except Exception as e:
    print(f"✗ Failed to initialize: {e}")
    sys.exit(1)

# Test 3: Start MCP server and connect
print("\n[3/5] Starting MCP server subprocess...")
try:
    chatbot.ensure_mcp_connection()
    print("✓ MCP server started and connected successfully")
except Exception as e:
    print(f"✗ Failed to start MCP server: {e}")
    sys.exit(1)

# Test 4: Get tool definitions
print("\n[4/5] Discovering available tools from server...")
try:
    # Get MCP tools from server
    mcp_tools = chatbot.mcp_connector.discover_tools()
    # Add schema tool
    schema_tool = chatbot._get_schema_tool()
    all_tools = mcp_tools + [schema_tool]
    
    print(f"✓ Successfully discovered {len(all_tools)} tools ({len(mcp_tools)} MCP + 1 schema)")
    print("\nAvailable tool categories:")
    for tool in all_tools[:10]:  # Show first 10
        func = tool.get('function', {})
        print(f"  • {func.get('name', 'Unknown')}")
    if len(all_tools) > 10:
        print(f"  ... and {len(all_tools) - 10} more")
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: Get MCP status
print("\n[5/5] Checking MCP status...")
try:
    status = chatbot.get_mcp_status()
    print(f"✓ MCP Status:")
    for key, value in status.items():
        print(f"  {key}: {value}")
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)

print("\n" + "=" * 70)
print("✓ All tests passed! MCP server is running and tools are available.")
print("=" * 70)
print("\nMCP Server Status:")
print("  • Running as subprocess")
print("  • JSON-RPC communication via stdio")
print("  • Tools accessible from Django")
print("\nYou can now:")
print("  1. Start Django: python manage.py runserver")
print("  2. Make a request: POST /finance/chatbot/send/")
print("  3. Try a query: {\"message\": \"How many companies do we have?\"}")
print("\nFor more info, see MCP_SUBPROCESS_ARCHITECTURE.md")

# Cleanup
print("\nCleaning up...")
try:
    chatbot.cleanup()
    print("✓ MCP server stopped successfully")
except Exception as e:
    print(f"Note: {e}")
