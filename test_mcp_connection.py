"""
Test MCP Server Connection
Quick test to verify MCP server starts and responds correctly
"""
import os
import sys
import django
from pathlib import Path

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

# Now import MCP components
from chatbot.mcp_client.server_manager import MCPServerManager
from chatbot.mcp_client.connector import MCPClientConnector
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_mcp_connection():
    """Test MCP server startup and connection"""
    
    # Get paths
    django_root = Path(__file__).resolve().parent
    mcp_server_path = django_root / "mcp_server" / "server.py"
    python_executable = sys.executable
    
    print("=" * 60)
    print("MCP Connection Test")
    print("=" * 60)
    print(f"Server path: {mcp_server_path}")
    print(f"Python: {python_executable}")
    print()
    
    # Create server manager
    print("[1/5] Creating server manager...")
    server_manager = MCPServerManager(
        server_path=mcp_server_path,
        python_executable=python_executable
    )
    print("✓ Server manager created")
    
    try:
        # Start server
        print("\n[2/5] Starting MCP server...")
        if not server_manager.start():
            print("✗ Failed to start server")
            return False
        print("✓ Server started")
        
        # Create connector
        print("\n[3/5] Creating connector...")
        connector = MCPClientConnector(server_manager)
        print("✓ Connector created")
        
        # Connect
        print("\n[4/5] Connecting to server...")
        connector.connect()
        print("✓ Connected successfully")
        
        # Discover tools
        print("\n[5/5] Discovering tools...")
        tools = connector.discover_tools()
        print(f"✓ Discovered {len(tools)} tools")
        
        # List some tools
        print("\nFirst 10 tools:")
        for i, tool in enumerate(tools[:10]):
            print(f"  {i+1}. {tool['function']['name']}")
        
        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED")
        print("=" * 60)
        
        # Cleanup
        connector.disconnect()
        server_manager.stop()
        
        return True
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        
        # Cleanup
        try:
            server_manager.stop()
        except:
            pass
        
        return False

if __name__ == "__main__":
    success = test_mcp_connection()
    sys.exit(0 if success else 1)
