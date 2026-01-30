"""
Test script to verify schema guide restructuring
Confirms that REQUIRED and OPTIONAL fields are clearly separated
"""
import sys
sys.path.insert(0, 'mcp_server')

# Import directly
from tools.prompt_tools import *

# Test by calling functions directly
test_functions = [
    ('Company', lambda: get_company_schema_guide()),
    ('Journal Entry', lambda: get_journal_entry_schema_guide()),
    ('Account', lambda: get_account_schema_guide()),
    ('Invoice', lambda: get_invoice_schema_guide()),
    ('Supplier', lambda: get_supplier_schema_guide()),
    ('Customer', lambda: get_customer_schema_guide()),
    ('Budget', lambda: get_budget_schema_guide()),
    ('Cost Center', lambda: get_cost_center_schema_guide()),
]

print("=" * 80)
print("SCHEMA GUIDE VERIFICATION TEST")
print("=" * 80)

for name, func in test_functions:
    try:
        schema_output = func()
        
        # Check for restructured format
        has_required = 'REQUIRED Fields' in schema_output
        has_optional = 'OPTIONAL Fields' in schema_output
        has_auto = 'Auto-generated Fields' in schema_output
        
        status = '✅' if (has_required and has_optional and has_auto) else '❌'
        
        print(f"\n{status} {name}")
        print(f"   - Has 'REQUIRED Fields' section: {has_required}")
        print(f"   - Has 'OPTIONAL Fields' section: {has_optional}")
        print(f"   - Has 'Auto-generated Fields' section: {has_auto}")
    except Exception as e:
        print(f"\n❌ {name} - ERROR: {e}")

# Detailed check for Journal Entry (most critical)
print("\n" + "=" * 80)
print("DETAILED CHECK: Journal Entry Schema")
print("=" * 80)
je_schema = get_journal_entry_schema_guide()
print(je_schema)

# Check specifically for company field in OPTIONAL section
print("\n" + "=" * 80)
print("CRITICAL VERIFICATION")
print("=" * 80)
if 'OPTIONAL Fields' in je_schema:
    # Find the OPTIONAL section
    parts = je_schema.split('OPTIONAL Fields')
    if len(parts) > 1:
        # Get everything after "OPTIONAL Fields" and before next major section
        optional_section = parts[1].split('**Foreign Keys**')[0] if '**Foreign Keys**' in parts[1] else parts[1].split('**Auto-generated')[0] if '**Auto-generated' in parts[1] else parts[1]
        has_company_in_optional = 'company (FK)' in optional_section
        print(f"✅ Company field is in OPTIONAL section: {has_company_in_optional}")
        if has_company_in_optional:
            # Extract the line with company
            for line in optional_section.split('\n'):
                if 'company' in line.lower():
                    print(f"   Line: {line.strip()}")
else:
    print("❌ No OPTIONAL Fields section found!")

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)
