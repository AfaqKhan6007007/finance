"""
Detailed MCP Chatbot Test
Tests the full chatbot flow with detailed logging
"""
import os
import sys
import django
import logging

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

# Enable detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from finance.services.chatbot_service_enhanced import EnhancedChatbotService

def test_chatbot():
    """Test chatbot with detailed output"""
    
    print("=" * 60)
    print("CHATBOT TEST - Generic Data Tools Architecture")
    print("=" * 60)
    
    # Create service
    print("\n[1] Initializing EnhancedChatbotService...")
    service = EnhancedChatbotService()
    print("[OK] Service initialized")
    
    # Check MCP status
    print("\n[2] Checking MCP status...")
    status = service.get_mcp_status()
    print(f"  - Server running: {status.get('server_running')}")
    print(f"  - Tools connected: {status.get('tools_connected')}")
    print(f"  - Server PID: {status.get('server_pid')}")
    
    # Create session
    session = {'conversation': []}
    
    # Test query
    print("\n[3] Sending test query: 'List all companies'")
    print("-" * 60)
    
    try:
        response = service.send_message('List all companies', session)
        
        print("\n[4] RESPONSE RECEIVED:")
        print("-" * 60)
        print(response)
        print("-" * 60)
        
        # Show conversation details
        print(f"\n[5] Conversation details:")
        print(f"  - Total messages: {len(session.get('conversation', []))}")
        
        # Show message roles
        for i, msg in enumerate(session.get('conversation', [])):
            role = msg.get('role')
            content_preview = str(msg.get('content', ''))[:50]
            tool_calls = msg.get('tool_calls')
            print(f"  [{i+1}] {role:10s} - {content_preview}... {f'({len(tool_calls)} tools)' if tool_calls else ''}")
        
        print("\n" + "=" * 60)
        print("[OK] TEST COMPLETED SUCCESSFULLY")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        if hasattr(service, 'server_manager') and service.server_manager:
            service.server_manager.stop()
            print("\n[OK] MCP server stopped")

if __name__ == "__main__":
    test_chatbot()
