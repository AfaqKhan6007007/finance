"""
Test the enhanced CREATE workflow with validation and FK selection
"""

import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from finance.services.chatbot_service_enhanced import EnhancedChatbotService

def print_separator(title=""):
    print("\n" + "=" * 100)
    if title:
        print(f"  {title}")
        print("=" * 100)

def test_case_1_missing_required_fields():
    """Test: Create company without providing country (required field)"""
    print_separator("TEST CASE 1: Create Company - Missing Required Field")
    
    chatbot = EnhancedChatbotService()
    session = {'conversation': []}
    
    query = "Create a company called TestTech Solutions"
    
    print(f"\nUser Query: {query}")
    print("\nExpected Behavior:")
    print("  1. Chatbot should call get_company_schema_guide()")
    print("  2. Chatbot should call validate_required_fields_tool()")
    print("  3. Chatbot should find 'country' is missing")
    print("  4. Chatbot should ASK USER for country")
    print("  5. Chatbot should NOT create the record yet")
    
    print("\n" + "-" * 100)
    print("Chatbot Response:")
    print("-" * 100)
    
    response = chatbot.send_message(query, session)
    print(response)
    
    # Check if response asks for country
    if "country" in response.lower() and ("missing" in response.lower() or "need" in response.lower() or "provide" in response.lower()):
        print("\n✅ PASS: Chatbot correctly identified missing 'country' field")
    else:
        print("\n❌ FAIL: Chatbot did not ask for missing country field")
    
    return session

def test_case_2_provide_missing_field(session):
    """Test: User provides the missing country field"""
    print_separator("TEST CASE 2: User Provides Missing Field")
    
    chatbot = EnhancedChatbotService()
    
    query = "USA"
    
    print(f"\nUser Query: {query}")
    print("\nExpected Behavior:")
    print("  1. Chatbot should validate again with country='USA'")
    print("  2. All required fields now present")
    print("  3. Chatbot should call create_record_tool()")
    print("  4. Chatbot should confirm creation success")
    
    print("\n" + "-" * 100)
    print("Chatbot Response:")
    print("-" * 100)
    
    response = chatbot.send_message(query, session)
    print(response)
    
    if "created" in response.lower() or "success" in response.lower():
        print("\n✅ PASS: Company created successfully")
    else:
        print("\n⚠️ WARNING: Creation status unclear")

def test_case_3_create_with_fk():
    """Test: Create account (requires company FK) - chatbot should list companies"""
    print_separator("TEST CASE 3: Create Account - Foreign Key Required")
    
    chatbot = EnhancedChatbotService()
    session = {'conversation': []}
    
    query = "Create a Petty Cash account of type asset"
    
    print(f"\nUser Query: {query}")
    print("\nExpected Behavior:")
    print("  1. Chatbot should call get_account_schema_guide()")
    print("  2. Chatbot should call validate_required_fields_tool()")
    print("  3. Chatbot should find 'company' FK is missing")
    print("  4. Chatbot should call list_foreign_key_options_tool(table='account', foreign_key_field='company')")
    print("  5. Chatbot should display list of companies to user")
    print("  6. Chatbot should ask user to select a company")
    
    print("\n" + "-" * 100)
    print("Chatbot Response:")
    print("-" * 100)
    
    response = chatbot.send_message(query, session)
    print(response)
    
    # Check if response lists companies
    has_company_list = False
    has_company_names = ("techcorp" in response.lower() or "global" in response.lower() or "smarttech" in response.lower())
    has_selection_prompt = ("select" in response.lower() or "choose" in response.lower() or "which company" in response.lower())
    
    if has_company_names and has_selection_prompt:
        print("\n✅ PASS: Chatbot listed companies and asked user to select")
        has_company_list = True
    else:
        print("\n❌ FAIL: Chatbot did not properly list companies for selection")
    
    return session, has_company_list

def test_case_4_select_fk_option(session):
    """Test: User selects a company from the list"""
    print_separator("TEST CASE 4: User Selects Company")
    
    chatbot = EnhancedChatbotService()
    
    query = "Use TechCorp Solutions USA"
    
    print(f"\nUser Query: {query}")
    print("\nExpected Behavior:")
    print("  1. Chatbot should resolve 'TechCorp Solutions USA' to company ID")
    print("  2. Chatbot should validate again with all required fields")
    print("  3. Chatbot should create the account")
    print("  4. Chatbot should confirm success")
    
    print("\n" + "-" * 100)
    print("Chatbot Response:")
    print("-" * 100)
    
    response = chatbot.send_message(query, session)
    print(response)
    
    if "created" in response.lower() or "success" in response.lower():
        print("\n✅ PASS: Account created successfully with FK link")
    else:
        print("\n⚠️ WARNING: Creation status unclear")

def test_case_5_complete_info_upfront():
    """Test: User provides all required info upfront - direct creation"""
    print_separator("TEST CASE 5: Complete Info Provided Upfront")
    
    chatbot = EnhancedChatbotService()
    session = {'conversation': []}
    
    query = "Create a company 'DirectTech Industries' in India with currency INR"
    
    print(f"\nUser Query: {query}")
    print("\nExpected Behavior:")
    print("  1. Chatbot should validate and find all required fields present")
    print("  2. Chatbot should create directly without asking for more info")
    print("  3. Chatbot should confirm success")
    
    print("\n" + "-" * 100)
    print("Chatbot Response:")
    print("-" * 100)
    
    response = chatbot.send_message(query, session)
    print(response)
    
    # Check if created without additional prompts
    if ("created" in response.lower() or "success" in response.lower()) and "missing" not in response.lower():
        print("\n✅ PASS: Company created directly with all info provided")
    else:
        print("\n⚠️ WARNING: May have asked for additional info unnecessarily")

def main():
    """Run all test cases"""
    print("=" * 100)
    print("ENHANCED CREATE WORKFLOW - COMPREHENSIVE TEST SUITE")
    print("=" * 100)
    print("\nThis test suite validates:")
    print("  - Missing required field detection and user prompting")
    print("  - Foreign key option listing and selection")
    print("  - Complete workflow with user interaction")
    print("  - Direct creation when all info provided")
    
    try:
        # Test Case 1: Missing required field
        session1 = test_case_1_missing_required_fields()
        
        # Test Case 2: Provide missing field
        test_case_2_provide_missing_field(session1)
        
        # Test Case 3: Create with FK requirement
        session3, has_list = test_case_3_create_with_fk()
        
        # Test Case 4: Select FK option (only if Case 3 worked)
        if has_list:
            test_case_4_select_fk_option(session3)
        
        # Test Case 5: Complete info upfront
        test_case_5_complete_info_upfront()
        
        print_separator("TEST SUITE COMPLETE")
        print("\nAll test cases executed. Review results above.")
        print("\nKey Success Criteria:")
        print("  ✅ Chatbot asks for missing required fields")
        print("  ✅ Chatbot lists FK options when needed")
        print("  ✅ Chatbot accepts user selections and creates records")
        print("  ✅ Chatbot creates directly when all info provided")
        
    except Exception as e:
        print(f"\n❌ ERROR during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
