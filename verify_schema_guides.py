"""
Comprehensive verification of all schema guide tools
Checks coverage, completeness, and quality
"""

import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from finance.models import (
    Company, Account, Invoice, JournalEntry, Supplier, Customer,
    Budget, CostCenter, CostCenterAllocation, AccountingDimension,
    TaxItemTemplate, TaxCategory, TaxRule,
    TaxWithholdingCategory, TaxWithholdingRate, TaxCategoryAccount,
    DeductionCertificate, BankAccountType, BankAccountSubtype, BankAccount,
    UserProfile
)

def get_model_field_count(model_class):
    """Count fields in a Django model"""
    return len([f for f in model_class._meta.fields])

def get_model_foreign_keys(model_class):
    """Get list of foreign key field names"""
    return [f.name for f in model_class._meta.fields if f.is_relation]

def get_model_choice_fields(model_class):
    """Get list of fields with choices"""
    return [f.name for f in model_class._meta.fields if f.choices]

def analyze_schema_guide(schema_text, model_name, model_class):
    """Analyze completeness of a schema guide"""
    results = {
        'model': model_name,
        'has_purpose': '**Purpose**:' in schema_text,
        'has_fields': '**Fields**:' in schema_text,
        'has_foreign_keys': '**Foreign Keys**:' in schema_text,
        'has_choices': '**Choices**:' in schema_text,
        'has_business_logic': '**Business Logic**:' in schema_text or '**Business Rules**:' in schema_text,
        'field_count_mentioned': 0,
        'fk_count_mentioned': 0,
        'choice_count_mentioned': 0,
        'length': len(schema_text),
        'line_count': schema_text.count('\n'),
    }
    
    # Count mentions of actual fields
    actual_fields = [f.name for f in model_class._meta.fields]
    results['field_count_mentioned'] = sum(1 for field in actual_fields if f'- {field}' in schema_text or f'`{field}`' in schema_text)
    
    # Count FK mentions
    actual_fks = get_model_foreign_keys(model_class)
    results['fk_count_mentioned'] = sum(1 for fk in actual_fks if fk in schema_text)
    
    # Count choice fields mentioned
    actual_choices = get_model_choice_fields(model_class)
    results['choice_count_mentioned'] = sum(1 for choice_field in actual_choices if choice_field in schema_text)
    
    # Get actual counts
    results['actual_field_count'] = len(actual_fields)
    results['actual_fk_count'] = len(actual_fks)
    results['actual_choice_count'] = len(actual_choices)
    
    # Calculate completeness score
    field_coverage = (results['field_count_mentioned'] / results['actual_field_count'] * 100) if results['actual_field_count'] > 0 else 100
    fk_coverage = (results['fk_count_mentioned'] / results['actual_fk_count'] * 100) if results['actual_fk_count'] > 0 else 100
    choice_coverage = (results['choice_count_mentioned'] / results['actual_choice_count'] * 100) if results['actual_choice_count'] > 0 else 100
    
    results['field_coverage'] = field_coverage
    results['fk_coverage'] = fk_coverage
    results['choice_coverage'] = choice_coverage
    results['overall_score'] = (field_coverage + fk_coverage + choice_coverage) / 3
    
    return results

def main():
    """Main verification function"""
    
    # Map of models to schema guide methods
    models_and_guides = [
        (Company, 'get_company_schema_guide', 'company'),
        (Account, 'get_account_schema_guide', 'account'),
        (Invoice, 'get_invoice_schema_guide', 'invoice'),
        (JournalEntry, 'get_journal_entry_schema_guide', 'journal_entry'),
        (Supplier, 'get_supplier_schema_guide', 'supplier'),
        (Customer, 'get_customer_schema_guide', 'customer'),
        (Budget, 'get_budget_schema_guide', 'budget'),
        (CostCenter, 'get_cost_center_schema_guide', 'cost_center'),
        (CostCenterAllocation, 'get_cost_center_allocation_schema_guide', 'cost_center_allocation'),
        (AccountingDimension, 'get_accounting_dimension_schema_guide', 'accounting_dimension'),
        (TaxItemTemplate, 'get_tax_item_template_schema_guide', 'tax_item_template'),
        (TaxCategory, 'get_tax_category_schema_guide', 'tax_category'),
        (TaxRule, 'get_tax_rule_schema_guide', 'tax_rule'),
        (TaxWithholdingCategory, 'get_tax_withholding_category_schema_guide', 'tax_withholding_category'),
        (TaxWithholdingRate, 'get_tax_withholding_rate_schema_guide', 'tax_withholding_rate'),
        (TaxCategoryAccount, 'get_tax_category_account_schema_guide', 'tax_category_account'),
        (DeductionCertificate, 'get_deduction_certificate_schema_guide', 'deduction_certificate'),
        (BankAccountType, 'get_bank_account_type_schema_guide', 'bank_account_type'),
        (BankAccountSubtype, 'get_bank_account_subtype_schema_guide', 'bank_account_subtype'),
        (BankAccount, 'get_bank_account_schema_guide', 'bank_account'),
        (UserProfile, 'get_user_profile_schema_guide', 'user_profile'),
    ]
    
    print("=" * 100)
    print("SCHEMA GUIDE VERIFICATION REPORT")
    print("=" * 100)
    print(f"\nTotal Models: {len(models_and_guides)}")
    print(f"Expected Schema Guides: {len(models_and_guides)}")
    print("\n" + "=" * 100)
    
    # Import the tool functions directly
    sys.path.insert(0, 'mcp_server/tools')
    import prompt_tools
    
    all_results = []
    
    for model_class, method_name, table_name in models_and_guides:
        print(f"\n[{table_name.upper()}]")
        
        # Get schema guide - call it directly from the module
        # The functions are defined inside register_prompt_tools, so we need to extract them
        # For now, let's just test if they exist by calling the MCP server
        try:
            # We'll use a simpler approach - just check if the guide text exists
            from finance.services.chatbot_service_enhanced import EnhancedChatbotService
            
            chatbot = EnhancedChatbotService()
            chatbot.ensure_mcp_connection()
            
            # Call the schema guide tool
            schema_result = chatbot.mcp_connector.call_tool(method_name, {})
            
            # Extract text from MCP response format
            if isinstance(schema_result, dict) and 'content' in schema_result:
                schema_text = schema_result['content'][0]['text']
            else:
                schema_text = str(schema_result)
            
            # Analyze
            results = analyze_schema_guide(schema_text, table_name, model_class)
            all_results.append(results)
            
            # Print summary
            print(f"  Model Fields: {results['actual_field_count']}")
            print(f"  Fields Documented: {results['field_count_mentioned']} ({results['field_coverage']:.1f}%)")
            print(f"  Foreign Keys: {results['actual_fk_count']} / {results['fk_count_mentioned']} documented ({results['fk_coverage']:.1f}%)")
            print(f"  Choice Fields: {results['actual_choice_count']} / {results['choice_count_mentioned']} documented ({results['choice_coverage']:.1f}%)")
            print(f"  Schema Text: {results['length']} chars, {results['line_count']} lines")
            print(f"  Sections: Purpose={results['has_purpose']}, Fields={results['has_fields']}, FKs={results['has_foreign_keys']}, Choices={results['has_choices']}, Logic={results['has_business_logic']}")
            print(f"  Overall Score: {results['overall_score']:.1f}%")
            
            if results['overall_score'] >= 90:
                print("  Status: EXCELLENT")
            elif results['overall_score'] >= 70:
                print("  Status: GOOD")
            elif results['overall_score'] >= 50:
                print("  Status: ADEQUATE")
            else:
                print("  Status: NEEDS IMPROVEMENT")
                
        except AttributeError:
            print(f"  ERROR: Method {method_name} not found!")
            all_results.append({'model': table_name, 'error': 'Method not found'})
    
    # Summary statistics
    print("\n" + "=" * 100)
    print("OVERALL SUMMARY")
    print("=" * 100)
    
    valid_results = [r for r in all_results if 'error' not in r]
    
    print(f"\nTotal Schema Guides: {len(all_results)}")
    print(f"Successfully Analyzed: {len(valid_results)}")
    print(f"Errors: {len(all_results) - len(valid_results)}")
    
    if valid_results:
        avg_field_coverage = sum(r['field_coverage'] for r in valid_results) / len(valid_results)
        avg_fk_coverage = sum(r['fk_coverage'] for r in valid_results) / len(valid_results)
        avg_choice_coverage = sum(r['choice_coverage'] for r in valid_results) / len(valid_results)
        avg_overall = sum(r['overall_score'] for r in valid_results) / len(valid_results)
        
        print(f"\nAverage Field Coverage: {avg_field_coverage:.1f}%")
        print(f"Average FK Coverage: {avg_fk_coverage:.1f}%")
        print(f"Average Choice Coverage: {avg_choice_coverage:.1f}%")
        print(f"Average Overall Score: {avg_overall:.1f}%")
        
        excellent_count = sum(1 for r in valid_results if r['overall_score'] >= 90)
        good_count = sum(1 for r in valid_results if 70 <= r['overall_score'] < 90)
        adequate_count = sum(1 for r in valid_results if 50 <= r['overall_score'] < 70)
        poor_count = sum(1 for r in valid_results if r['overall_score'] < 50)
        
        print(f"\nQuality Distribution:")
        print(f"  EXCELLENT (>=90%): {excellent_count}")
        print(f"  GOOD (70-89%): {good_count}")
        print(f"  ADEQUATE (50-69%): {adequate_count}")
        print(f"  NEEDS IMPROVEMENT (<50%): {poor_count}")
        
        # Identify any issues
        issues = []
        for r in valid_results:
            if r['field_coverage'] < 80:
                issues.append(f"{r['model']}: Only {r['field_coverage']:.1f}% fields documented")
            if r['fk_coverage'] < 80 and r['actual_fk_count'] > 0:
                issues.append(f"{r['model']}: Only {r['fk_coverage']:.1f}% FKs documented")
        
        if issues:
            print(f"\nPotential Issues Found: {len(issues)}")
            for issue in issues[:10]:  # Show first 10
                print(f"  - {issue}")
        else:
            print("\nNo significant issues found! All schema guides are comprehensive.")
    
    print("\n" + "=" * 100)
    print("VERIFICATION COMPLETE")
    print("=" * 100)

if __name__ == "__main__":
    main()
