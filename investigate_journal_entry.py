"""
Investigate the journal entry creation issue to identify root causes
"""
import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from finance.models import JournalEntry, Account, Company

def investigate_journal_entry():
    """Investigate the journal entry and its company assignment"""
    
    print("=" * 90)
    print("JOURNAL ENTRY INVESTIGATION - Root Cause Analysis")
    print("=" * 90)
    
    # Find the journal entry with ID 41 and entry_number 55
    try:
        journal = JournalEntry.objects.filter(id=41).first()
        
        if not journal:
            print("\n[ERROR] Journal entry with ID 41 not found")
            return
        
        print("\n[FOUND] Journal Entry Details:")
        print("-" * 90)
        print(f"ID: {journal.id}")
        print(f"Entry Number: {journal.entry_number}")
        print(f"Date: {journal.date}")
        print(f"Description: {journal.description}")
        print(f"Debit Amount: {journal.debit_amount}")
        print(f"Credit Amount: {journal.credit_amount}")
        print(f"Created By: {journal.created_by.username if journal.created_by else 'None'}")
        print(f"Created At: {journal.created_at}")
        
        # Account details
        print("\n[ACCOUNT LINKED TO JOURNAL ENTRY]:")
        print("-" * 90)
        account = journal.account
        print(f"Account ID: {account.id}")
        print(f"Account Name: {account.name}")
        print(f"Account Number: {account.account_number}")
        print(f"Account Type: {account.account_type}")
        print(f"Currency: {account.currency}")
        
        # **KEY FINDING: Check account's company**
        print(f"\n[CRITICAL] Account's Company FK:")
        print("-" * 90)
        print(f"Account.company ID: {account.company.id if account.company else 'NULL'}")
        print(f"Account.company Name: {account.company.name if account.company else 'NULL'}")
        print(f"Account.company Country: {account.company.country if account.company else 'NULL'}")
        
        # Journal entry's direct company field
        print(f"\n[CRITICAL] Journal Entry's Direct Company Field:")
        print("-" * 90)
        print(f"JournalEntry.company ID: {journal.company.id if journal.company else 'NULL'}")
        print(f"JournalEntry.company Name: {journal.company.name if journal.company else 'NULL'}")
        
        # **ROOT CAUSE ANALYSIS**
        print("\n" + "=" * 90)
        print("ROOT CAUSE ANALYSIS:")
        print("=" * 90)
        
        print("\n[FINDING #1] Account vs Journal Entry Company Assignment")
        print("-" * 90)
        
        if account.company and journal.company:
            if account.company.id == journal.company.id:
                print(f"✓ Both Account and Journal Entry point to the SAME company: {journal.company.name}")
                print(f"  This is CORRECT behavior.")
            else:
                print(f"✗ MISMATCH: Account points to '{account.company.name}' (ID: {account.company.id})")
                print(f"            Journal Entry points to '{journal.company.name}' (ID: {journal.company.id})")
                print(f"  This is INCORRECT!")
        
        print("\n[FINDING #2] Why is TechCorp Solutions USA assigned?")
        print("-" * 90)
        
        # Check the account used
        if account.id == 95:
            print(f"✓ Account ID 95 (Operating Expenses) belongs to: {account.company.name}")
            print(f"  When you selected Account ID 95 for the journal entry,")
            print(f"  the chatbot automatically inherited the company from that account.")
            print(f"  This is the ROOT CAUSE of the issue.")
        
        print("\n[FINDING #3] Data Model Relationship Chain:")
        print("-" * 90)
        print(f"User Action: 'Please choose account with ID 95'")
        print(f"   ↓")
        print(f"Account ID 95 → Belongs to Company ID {account.company.id} ({account.company.name})")
        print(f"   ↓")
        print(f"JournalEntry created with:")
        print(f"   - account_id = 95")
        print(f"   - company_id = {account.company.id} (INHERITED from Account.company)")
        print(f"   - Result: JournalEntry.company = {journal.company.name}")
        
        print("\n" + "=" * 90)
        print("ROOT CAUSE SUMMARY:")
        print("=" * 90)
        print("""
1. **Primary Root Cause**: Account Model has mandatory Company FK
   - In Account model: company = ForeignKey(Company, on_delete=models.CASCADE)
   - This means EVERY account MUST belong to a company
   - When you selected Account ID 95, that account inherently carries its company association

2. **Secondary Root Cause**: JournalEntry Model also has Company FK (non-mandatory)
   - In JournalEntry model: company = ForeignKey(..., null=True, blank=True)
   - The chatbot code likely auto-fills this from account.company when creating journal entry
   - This happens WITHOUT asking the user explicitly

3. **Why TechCorp Solutions USA?**
   - Account ID 95 (Operating Expenses) is owned by TechCorp India Pvt Ltd
   - Wait - the output shows TechCorp Solutions USA, but the account belongs to TechCorp India
   - This suggests the chatbot may have overridden the account's company

4. **Workflow Issue**:
   - User asked to create journal entry without specifying company
   - User selected Account ID 95 (which has company = TechCorp India)
   - Chatbot assigned company = TechCorp Solutions USA instead
   - This means the chatbot is NOT using account.company directly
   - Instead, it's determining company from some other source

5. **Serious Issue**: 
   - Accounts belong to specific companies
   - Journal entries should also belong to the same company as their linked account
   - If chatbot assigns wrong company, it breaks the data integrity
   - In this case: Account belongs to Company X, but JournalEntry points to Company Y
        """)
        
        print("\n" + "=" * 90)
        print("VERIFICATION:")
        print("=" * 90)
        
        # Verify the discrepancy
        print(f"\nAccount ID 95:")
        print(f"  Company: {account.company.name}")
        print(f"\nJournal Entry ID 41:")
        print(f"  Company: {journal.company.name}")
        
        if account.company.name != journal.company.name:
            print(f"\n✗ CRITICAL ISSUE FOUND:")
            print(f"  Account's company ≠ Journal Entry's company")
            print(f"  This violates data integrity!")
        
    except Exception as e:
        print(f"\n[ERROR] Exception occurred: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    investigate_journal_entry()
