#!/usr/bin/env python3
"""
Verify that system_prompt.py has been updated with optional fields workflow.
"""
import sys
sys.path.insert(0, r'd:\Machine Learning\JFF JOB\finance')

from chatbot.prompt_templates.system_prompt import get_system_prompt

def verify_system_prompt():
    """Check if system prompt contains the new optional fields workflow"""
    prompt = get_system_prompt()
    
    print("=" * 80)
    print("VERIFYING SYSTEM PROMPT UPDATE")
    print("=" * 80)
    
    # Check for critical sections
    checks = [
        ("Optional Fields Workflow", "Optional Fields Workflow"),
        ("Don't auto-populate", "auto-populate optional fields"),
        ("Only include provided fields", "Only include fields"),
        ("Journal entry example", "journal entry for account 95"),
        ("Company field is optional", "company field is OPTIONAL"),
        ("Ask for company field", "Should this entry have a company"),
        ("Company NOT included when user says no", "company NOT included"),
        ("Auto-assignment is wrong", "auto-assign optional fields"),
    ]
    
    all_passed = True
    
    for check_name, check_text in checks:
        if check_text in prompt:
            print(f"✅ {check_name}: FOUND")
        else:
            print(f"❌ {check_name}: NOT FOUND")
            all_passed = False
    
    print("\n" + "=" * 80)
    if all_passed:
        print("✅ ALL CHECKS PASSED - System prompt has been properly updated!")
    else:
        print("❌ SOME CHECKS FAILED - System prompt needs more updates")
    print("=" * 80)
    
    return all_passed

if __name__ == "__main__":
    success = verify_system_prompt()
    sys.exit(0 if success else 1)
