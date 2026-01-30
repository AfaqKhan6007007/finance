"""
Script to verify if a specific account exists in the database
"""
import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from finance.models import Account

def verify_account():
    """Check if the account with given details exists"""
    
    # Expected account details
    expected = {
        'id': 97,
        'name': 'testing 1',
        'account_number': '122322',
        'company_name': 'Retail Solutions Inc',
        'currency': 'USD',
        'account_type': 'Asset',
        'balance_must_be': 'Debit',
        'created_by': 'bob_wilson'
    }
    
    print("=" * 70)
    print("ACCOUNT VERIFICATION")
    print("=" * 70)
    print("\nSearching for account with:")
    print(f"  ID: {expected['id']}")
    print(f"  Name: {expected['name']}")
    print(f"  Account Number: {expected['account_number']}")
    print("\n" + "-" * 70)
    
    try:
        # Try to find the account by ID
        account = Account.objects.filter(id=expected['id']).first()
        
        if not account:
            print("\n[RESULT] Account NOT FOUND by ID")
            print("\nSearching by name and account number...")
            
            # Try to find by name and account number
            account = Account.objects.filter(
                name=expected['name'],
                account_number=expected['account_number']
            ).first()
            
            if not account:
                print("[RESULT] Account NOT FOUND by name/account_number either")
                print("\n[VERDICT] ACCOUNT DOES NOT EXIST IN DATABASE")
                return False
            else:
                print(f"[RESULT] Account FOUND with different ID: {account.id}")
        
        # Account found - verify details
        print("\n[RESULT] ACCOUNT FOUND!")
        print("\n" + "=" * 70)
        print("ACTUAL DATABASE RECORD:")
        print("=" * 70)
        
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
        print(f"Company: {company_name}")
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
        
        # Summary
        print("\n" + "=" * 70)
        print("FIELD VERIFICATION:")
        print("=" * 70)
        
        all_match = True
        for field_name, expected_val, actual_val, matches in results:
            status = "[OK]" if matches else "[MISMATCH]"
            print(f"{status} {field_name:20} | Expected: {expected_val:25} | Actual: {actual_val}")
            if not matches:
                all_match = False
        
        print("\n" + "=" * 70)
        if all_match:
            print("[VERDICT] ACCOUNT EXISTS AND ALL FIELDS MATCH!")
            print("=" * 70)
            return True
        else:
            print("[VERDICT] ACCOUNT EXISTS BUT SOME FIELDS DON'T MATCH")
            print("=" * 70)
            return False
            
    except Exception as e:
        print(f"\n[ERROR] Exception occurred: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    verify_account()
