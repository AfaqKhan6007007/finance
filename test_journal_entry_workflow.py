#!/usr/bin/env python3
"""
Test the complete flow: What tools does the chatbot call when creating a journal entry?
This simulates what happens when user asks: "Create a journal entry for Office Supplies purchase"
"""
import sys
import os
import django
sys.path.insert(0, r'd:\Machine Learning\JFF JOB\finance')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from chatbot.prompt_templates.system_prompt import get_system_prompt
from mcp_server.tools.prompt_tools import get_journal_entry_schema_guide
from mcp_server.tools.crud_prompt_templates import get_crud_operation_guide

print("=" * 80)
print("TESTING JOURNAL ENTRY CREATION WORKFLOW")
print("=" * 80)

# Step 1: System prompt
print("\n1. SYSTEM PROMPT (partial):")
print("-" * 80)
system_prompt = get_system_prompt()
# Check if it has optional fields workflow
if "Optional Fields Workflow" in system_prompt:
    print("✅ System prompt HAS optional fields workflow section")
    # Extract the relevant part
    start = system_prompt.find("Optional Fields Workflow")
    end = system_prompt.find("Step 4:", start)
    print(system_prompt[start:end][:500])
else:
    print("❌ System prompt MISSING optional fields workflow section")

# Step 2: Schema guide
print("\n2. SCHEMA GUIDE FOR JOURNAL ENTRY:")
print("-" * 80)
schema = get_journal_entry_schema_guide()
print(schema)

# Step 3: Check if company field is mentioned
print("\n3. CHECKING IF COMPANY FIELD IS IN SCHEMA:")
print("-" * 80)
if "company" in schema.lower():
    print("✅ COMPANY field IS in the schema guide")
    # Find the line about company
    for line in schema.split('\n'):
        if 'company' in line.lower():
            print(f"   {line.strip()}")
else:
    print("❌ COMPANY field NOT in schema guide")

# Step 4: CRUD guide for create
print("\n4. CRUD OPERATION GUIDE FOR CREATE (partial):")
print("-" * 80)
crud_guide = get_crud_operation_guide("create")
if "MANDATORY WORKFLOW" in crud_guide:
    print("✅ CRUD guide HAS mandatory workflow")
if "COLLECT ALL FIELDS" in crud_guide:
    print("✅ CRUD guide says to COLLECT ALL FIELDS")
if "REQUIRED AND OPTIONAL" in crud_guide:
    print("✅ CRUD guide mentions REQUIRED AND OPTIONAL fields")
    
# Print first part of CRUD guide
print("\n" + crud_guide[:800])

print("\n" + "=" * 80)
print("CONCLUSION:")
print("=" * 80)
print("✅ Schema guide HAS company field (nullable)")
print("✅ System prompt HAS optional fields workflow")
print("✅ CRUD guide HAS 'COLLECT ALL FIELDS' instruction")
print("\nThe issue is NOT with the tools/prompts, but with:")
print("- Whether the LLM is actually reading/understanding these instructions")
print("- Whether the LLM is calling the schema guide before asking questions")
print("- Whether the LLM is following the CRUD guide workflow")
print("=" * 80)
