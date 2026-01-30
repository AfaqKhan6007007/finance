"""
Script to verify if the 'nemro' account exists in the database
and verify that the foreign key is correctly linked
"""
import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from finance.models import Account, Company

def verify_nemro_account():
    """Check if the nemro account with given details exists and verify FK"""
    
    # Expected account details
    expected = {
        'id': 98,
        'name': 'nemro',
        'account_number': '1160',
        'company_name': 'TechCorp Solutions USA',
        'currency': 'PKR',
        'account_type': 'Asset',
        'balance_must_be': 'Debit',
        'created_by': 'bob_wilson'
    }
    
    print("=" * 80)
    print("ACCOUNT VERIFICATION - 'nemro' Account")
    print("=" * 80)
    print("\nSearching for account with:")
    print(f"  ID: {expected['id']}")
    print(f"  Name: {expected['name']}")
    print(f"  Account Number: {expected['account_number']}")
    print("\n" + "-" * 80)
    
    try:
        # Try to find the account by ID
        account = Account.objects.filter(id=expected['id']).first()
        
        if not account:
            print("\n[RESULT] Account NOT FOUND by ID")
            print("\nSearching by name...")
            
            # Try to find by name
            account = Account.objects.filter(name=expected['name']).first()
            
            if not account:
                print("[RESULT] Account NOT FOUND by name either")
                print("\n[VERDICT] ACCOUNT DOES NOT EXIST IN DATABASE")
                return False
            else:
                print(f"[RESULT] Account FOUND with ID: {account.id}")
        
        # Account found - verify details
        print("\n[RESULT] ACCOUNT FOUND!")
        print("\n" + "=" * 80)
        print("ACTUAL DATABASE RECORD:")
        print("=" * 80)
        
        results = []
        
        # Check each field
        print(f"\nID: {account.id}")
        results.append(('ID', expected['id'], account.id, expected['id'] == account.id))
        
        print(f"Name: {account.name}")
        results.append(('Name', expected['name'], account.name, expected['name'] == account.name))
        
        print(f"Account Number: {account.account_number}")
        results.append(('Account Number', expected['account_number'], account.account_number, 
                       expected['account_number'] == account.account_number))
        
        company_name = account.company.name if account.company else None
        company_id = account.company.id if account.company else None
        print(f"Company: {company_name} (ID: {company_id})")
        results.append(('Company', expected['company_name'], company_name, 
                       expected['company_name'] == company_name))
        
        print(f"Currency: {account.currency}")
        results.append(('Currency', expected['currency'], account.currency, 
                       expected['currency'] == account.currency))
        
        print(f"Account Type: {account.account_type}")
        results.append(('Account Type', expected['account_type'], account.account_type, 
                       expected['account_type'] == account.account_type))
        
        print(f"Balance Must Be: {account.balance_must_be}")
        results.append(('Balance Must Be', expected['balance_must_be'], account.balance_must_be, 
                       expected['balance_must_be'] == account.balance_must_be))
        
        created_by = account.created_by.username if account.created_by else None
        print(f"Created By: {created_by}")
        results.append(('Created By', expected['created_by'], created_by, 
                       expected['created_by'] == created_by))
        
        print(f"Created At: {account.created_at}")
        
        # Summary of field verification
        print("\n" + "=" * 80)
        print("FIELD VERIFICATION:")
        print("=" * 80)
        
        all_match = True
        for field_name, expected_val, actual_val, matches in results:
            status = "[OK]" if matches else "[MISMATCH]"
            print(f"{status} {field_name:20} | Expected: {str(expected_val):30} | Actual: {actual_val}")
            if not matches:
                all_match = False
        
        # Foreign Key Verification
        print("\n" + "=" * 80)
        print("FOREIGN KEY VERIFICATION:")
        print("=" * 80)
        
        if account.company:
            print(f"\n[OK] Company FK is LINKED")
            print(f"  Company ID: {account.company.id}")
            print(f"  Company Name: {account.company.name}")
            print(f"  Company Country: {account.company.country}")
            
            # Verify the company exists
            try:
                tech_corp = Company.objects.get(name='TechCorp Solutions USA')
                fk_matches = account.company.id == tech_corp.id
                status = "[OK]" if fk_matches else "[MISMATCH]"
                print(f"\n{status} FK correctly points to the expected company")
                print(f"  Expected Company ID: {tech_corp.id}")
                print(f"  Account's Company FK: {account.company.id}")
                print(f"  Match: {fk_matches}")
            except Company.DoesNotExist:
                print("\n[WARNING] 'TechCorp Solutions USA' company not found in database")
        else:
            print("\n[ERROR] Company FK is NOT LINKED (NULL)")
            all_match = False
        
        # Summary
        print("\n" + "=" * 80)
        if all_match:
            print("[VERDICT] ACCOUNT EXISTS, ALL FIELDS MATCH, AND FK IS CORRECTLY LINKED!")
            print("=" * 80)
            return True
        else:
            print("[VERDICT] ACCOUNT EXISTS BUT SOME FIELDS OR FK DON'T MATCH")
            print("=" * 80)
            return False
            
    except Exception as e:
        print(f"\n[ERROR] Exception occurred: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    verify_nemro_account()
