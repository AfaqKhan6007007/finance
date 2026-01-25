"""
Test script to verify chatbot calls schema guide before data operations
"""

import os
import sys
import django
import logging

# Setup Django environment
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from finance.services.chatbot_service_enhanced import EnhancedChatbotService

# Enable detailed logging to see tool calls
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_schema_guide_calls():
    """Test that schema guide is called before data operations"""
    
    test_cases = [
        {
            "query": "List all companies",
            "expected_schema_call": "get_company_schema_guide",
            "expected_data_call": "query_records"
        },
        {
            "query": "Show me invoice with ID 5",
            "expected_schema_call": "get_invoice_schema_guide",
            "expected_data_call": "get_record"
        },
        {
            "query": "Find all suppliers in USA",
            "expected_schema_call": "get_supplier_schema_guide",
            "expected_data_call": "query_records"
        }
    ]
    
    chatbot = EnhancedChatbotService()
    
    print("=" * 100)
    print("TESTING: Schema Guide Calls Before Data Operations")
    print("=" * 100)
    
    for idx, test_case in enumerate(test_cases, 1):
        print(f"\n{'=' * 100}")
        print(f"TEST CASE {idx}: {test_case['query']}")
        print("=" * 100)
        
        print(f"\n[Expected Workflow:]")
        print(f"   1. Call {test_case['expected_schema_call']}()")
        print(f"   2. Call {test_case['expected_data_call']}()")
        print(f"\n[Watching tool calls in logs above...]")
        print(f"   Look for lines with 'Executing tool:' to verify order")
        
        session = {'conversation': []}
        
        # Send query
        response = chatbot.send_message(test_case['query'], session)
        
        print(f"\n[Response received (showing first 300 chars):]")
        print(f"   {response[:300]}...")
        
        print(f"\n{'=' * 100}\n")
    
    print("\n" + "=" * 100)
    print("VERIFICATION INSTRUCTIONS:")
    print("=" * 100)
    print("Look at the logs above for each test case.")
    print("You should see tool execution in this order:")
    print("  1. 'Executing tool: get_<table>_schema_guide'")
    print("  2. 'Executing tool: get_record' or 'query_records'")
    print("\nIf schema guide is NOT called first, the system prompt needs adjustment.")
    print("=" * 100)

if __name__ == "__main__":
    test_schema_guide_calls()
