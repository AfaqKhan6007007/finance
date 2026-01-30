"""
Check what validate_required_fields says about JournalEntry
"""
import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from finance.models import JournalEntry

def check_journalentry_fields():
    """Check which fields JournalEntry considers as required"""
    
    print("=" * 90)
    print("JOURNALENTRY FIELD ANALYSIS")
    print("=" * 90)
    
    print("\n[FIELD REQUIREMENTS ANALYSIS]:")
    print("-" * 90)
    
    for field in JournalEntry._meta.fields:
        # Skip auto fields
        if field.auto_created or field.name in ['id', 'created_at', 'updated_at']:
            continue
        
        is_required = not field.null and not field.has_default()
        is_fk = field.is_relation
        
        print(f"\nField: {field.name}")
        print(f"  Type: {field.get_internal_type()}")
        print(f"  Nullable: {field.null}")
        print(f"  Has Default: {field.has_default()}")
        print(f"  Is FK: {is_fk}")
        print(f"  IS REQUIRED: {is_required}")
        
        if is_fk:
            print(f"  Related Model: {field.related_model.__name__}")
    
    print("\n" + "=" * 90)
    print("SUMMARY:")
    print("=" * 90)
    
    required = []
    for field in JournalEntry._meta.fields:
        if field.auto_created or field.name in ['id', 'created_at', 'updated_at']:
            continue
        is_required = not field.null and not field.has_default()
        if is_required:
            required.append(field.name)
    
    print(f"\nRequired Fields: {required}")
    print(f"\nTotal Required: {len(required)}")
    
    # Check the company field specifically
    print("\n" + "-" * 90)
    print("COMPANY FIELD DETAILS:")
    print("-" * 90)
    company_field = JournalEntry._meta.get_field('company')
    print(f"Nullable: {company_field.null}")
    print(f"Has Default: {company_field.has_default()}")
    print(f"Blank: {company_field.blank}")
    print(f"Is REQUIRED: {not company_field.null and not company_field.has_default()}")
    
    if not company_field.null:
        print("\n⚠️ COMPANY IS A REQUIRED FIELD!")
        print("   It should be asked to the user during creation.")
    else:
        print("\n✓ Company field is OPTIONAL (null=True)")
        print("   This allows creation without specifying company.")

if __name__ == "__main__":
    check_journalentry_fields()
