"""
Test script to verify that chatbot returns ALL fields when user requests "all data"
"""

import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from finance.services.chatbot_service_enhanced import EnhancedChatbotService
import json

def test_all_fields_query():
    """Test that chatbot returns all fields when user asks for "all data" """
    
    print("=" * 80)
    print("Testing: Query for ALL DATA should return ALL FIELDS")
    print("=" * 80)
    
    chatbot = EnhancedChatbotService()
    conversation = []
    
    # Test queries that should return all fields
    test_queries = [
        "Show me all data for TechCorp Solutions USA",
        "Give me complete details for company with ID 22",
        "I want to see all fields for the company TechCorp Solutions USA",
        "List all information about company ID 22"
    ]
    
    for query in test_queries:
        print(f"\n{'=' * 80}")
        print(f"Query: {query}")
        print("=" * 80)
        
        # Get response
        response = chatbot.process_message(query, conversation, user=None)
        
        print(f"\nResponse:\n{response}")
        
        # Count fields mentioned in response
        expected_fields = [
            "abbreviation", "country", "date_of_establishment", "default_currency",
            "tax_id", "parent_company", "is_parent_company", "is_group", 
            "company_type", "created_at", "updated_at", "created_by",
            "account_number", "account_type", "balance_must_be", "tax_rate",
            "is_disabled", "default_letter_head", "domain", "registration_details"
        ]
        
        fields_found = []
        for field in expected_fields:
            if field in response.lower() or field.replace("_", " ") in response.lower():
                fields_found.append(field)
        
        print(f"\n{'=' * 80}")
        print(f"Fields found in response: {len(fields_found)}/{len(expected_fields)}")
        print(f"Fields: {', '.join(fields_found)}")
        print("=" * 80)
        
        if len(fields_found) >= 15:  # At least 75% of fields
            print("✅ PASS: Response includes most/all fields")
        else:
            print("❌ FAIL: Response only includes few fields")
            print(f"Missing fields: {set(expected_fields) - set(fields_found)}")
        
        # Reset conversation for next query
        conversation = []
        print("\n" + "=" * 80 + "\n")

if __name__ == "__main__":
    test_all_fields_query()
