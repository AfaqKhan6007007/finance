"""
CRUD Operation Prompt Templates - CONCISE VERSION
"""

CREATE_OPERATION_GUIDE = """CREATE WORKFLOW:

1. Call get_<table>_schema_guide() → Learn required + optional fields
2. Ask user for ALL fields (required + optional) from schema
3. Call validate_required_fields_tool(table, data)
4. If invalid: Show missing fields, STOP
5. If valid: Call create_record(table, {ONLY user-provided fields})

CRITICAL: Never auto-populate optional fields. Only include fields user explicitly provides.

Example - Journal Entry:
User: "Create journal entry for office supplies"
1. get_journal_entry_schema_guide() → Required: entry_number, date, account, debit/credit | Optional: company, description
2. Ask: Entry number? Date? Account? Debit/credit? Company (optional)? Description (optional)?
3. User says: entry_number=JE001, date=2026-01-28, account=50, debit=1000, company=NO, description=NO
4. validate_required_fields_tool("journal_entry", {entry_number, date, account, debit_amount}) → valid=true
5. create_record("journal_entry", {entry_number, date, account, debit_amount}) ← company NOT included

For FKs: Use list_foreign_key_options_tool(table, fk_field) to show options"""
────────────────────────────────────────────────────────────────────────────────
User: "Create a company called Tech Solutions"

LLM WORKFLOW:
1. Call get_company_schema_guide()
   → Learn required fields: name (✓ provided), country (✗ missing)

2. Call validate_required_fields_tool:
   validate_required_fields_tool(
       table="company",
       provided_data={"name": "Tech Solutions"}
   )
   
   RESPONSE:
   {
       "is_valid": false,
       "missing_required_fields": ["country"],
       "required_fields_info": {
           "country": "Operating country (required, max 100 chars)"
       }
   }

3. 🛑 STOP! Ask user for missing field:

   CHATBOT RESPONSE TO USER:
   "To create a company, I need the following required information:
   
   ❌ **Missing Required Fields:**
   - **country**: Operating country (required, max 100 chars)
   
   You provided:
   - name: Tech Solutions ✓
   
   Please provide the country (e.g., USA, India, UK)."

4. WAIT for user response. DO NOT create yet!

User: "USA"

5. Now validate again:
   validate_required_fields_tool(
       table="company",
       provided_data={"name": "Tech Solutions", "country": "USA"}
   )
   
   RESPONSE: {"is_valid": true}

6.  Now create:
   create_record_tool(
       table="company",
       data={"name": "Tech Solutions", "country": "USA", "default_currency": "USD"}
   )

RESULT:  Company created successfully!


EXAMPLE 2: Create Account - Missing FK (Foreign Key)
────────────────────────────────────────────────────────────────────────────────
User: "Create a Cash account"

LLM WORKFLOW:
1. Call get_account_schema_guide()
   → Learn required: name (✓), company (✗ FK), account_type (✗)

2. Call validate_required_fields_tool:
   validate_required_fields_tool(
       table="account",
       provided_data={"name": "Cash"}
   )
   
   RESPONSE:
   {
       "is_valid": false,
       "missing_required_fields": ["company", "account_type"],
       "missing_foreign_keys": ["company"],
       "required_fields_info": {
           "company": "Foreign key to Company table (required)",
           "account_type": "Choice field: asset/liability/equity/income/expense (required)"
       }
   }

3. 🛑 STOP! Get FK options and ask user:

   Call list_foreign_key_options_tool(
       table="account",
       foreign_key_field="company"
   )
   
   RESPONSE:
   {
       "options": [
           {"id": 22, "display": "TechCorp Solutions USA"},
           {"id": 23, "display": "Global Corp International"},
           {"id": 24, "display": "SmartTech Industries"}
       ]
   }

   CHATBOT RESPONSE TO USER:
   "To create an account, I need the following required information:
   
   ❌ **Missing Required Fields:**
   - **company**: Which company should this account belong to?
   - **account_type**: Type of account (asset/liability/equity/income/expense)
   
   **Available Companies:**
   - TechCorp Solutions USA (ID: 22)
   - Global Corp International (ID: 23)
   - SmartTech Industries (ID: 24)
   
   Please select a company and provide the account type (e.g., 'asset' for cash account)."

4. WAIT for user response!

User: "TechCorp Solutions USA, type is asset"

5. Now validate:
   validate_required_fields_tool(
       table="account",
       provided_data={
           "name": "Cash",
           "company": 22,
           "account_type": "asset"
       }
   )
   
   RESPONSE: {"is_valid": true}

6. ✅ Create:
   create_record_tool(
       table="account",
       data={
           "name": "Cash",
           "company": 22,
           "account_type": "asset",
           "balance_must_be": "debit"
       }
   )

RESULT: ✅ Account created linked to TechCorp Solutions USA!


EXAMPLE 3: Create Invoice - Multiple FKs with User Providing Info
────────────────────────────────────────────────────────────────────────────────
User: "Create invoice INV-2024-001 for supplier ABC Corp, company TechCorp, amount 5000"

LLM WORKFLOW:
1. Call get_invoice_schema_guide()
   → Learn required: invoice_id (✓), invoice_number (✓), date (✗), supplier (by name), company (by name), amount fields (✓)

2. First, resolve FK references by name:
   - User said "ABC Corp" - need supplier_id
   - User said "TechCorp" - need company_id

3. Call query_records_tool(table="supplier", text_search="ABC Corp")
   → Get supplier_id = 15

4. Call query_records_tool(table="company", text_search="TechCorp")
   → Get company_id = 22

5. Call validate_required_fields_tool:
   validate_required_fields_tool(
       table="invoice",
       provided_data={
           "invoice_id": "INV-2024-001",
           "invoice_number": "2024-001",
           "supplier": 15,
           "company": 22,
           "amount_before_vat": 5000.00,
           "total_vat": 0.00,
           "total_amount": 5000.00
       }
   )
   
   RESPONSE:
   {
       "is_valid": false,
       "missing_required_fields": ["date"],
       "required_fields_info": {
           "date": "Invoice date (required)"
       }
   }

6. 🛑 Ask for missing field:

   CHATBOT RESPONSE:
   "I need one more piece of information to create the invoice:
   
   ❌ **Missing Required Field:**
   - **date**: Invoice date (e.g., 2024-01-15)
   
   Please provide the invoice date."

7. WAIT for user!

User: "Today's date"

8. Interpret "today" as 2026-01-25, validate:
   validate_required_fields_tool(
       table="invoice",
       provided_data={
           "invoice_id": "INV-2024-001",
           "invoice_number": "2024-001",
           "date": "2026-01-25",
           "supplier": 15,
           "company": 22,
           "amount_before_vat": 5000.00,
           "total_vat": 0.00,
           "total_amount": 5000.00,
           "status": "draft"
       }
   )
   
   RESPONSE: {"is_valid": true}

9. ✅ Create:
   create_record_tool(table="invoice", data={...})

RESULT: ✅ Invoice created!


EXAMPLE 4: Create with All Info Provided Upfront - Direct Creation
────────────────────────────────────────────────────────────────────────────────
User: "Create company 'SmartTech Inc' in USA with currency USD"

LLM WORKFLOW:
1. Call get_company_schema_guide()

2. Call validate_required_fields_tool:
   validate_required_fields_tool(
       table="company",
       provided_data={
           "name": "SmartTech Inc",
           "country": "USA",
           "default_currency": "USD"
       }
   )
   
   RESPONSE: {"is_valid": true} ✅

3. All required fields present! Create immediately:
   create_record_tool(
       table="company",
       data={"name": "SmartTech Inc", "country": "USA", "default_currency": "USD"}
   )

RESULT: ✅ Company created! No interaction needed.


═══════════════════════════════════════════════════════════════════════════════
KEY RULES FOR CREATE OPERATIONS
═══════════════════════════════════════════════════════════════════════════════

✅ DO:
1. ALWAYS call validate_required_fields_tool BEFORE create_record_tool
2. If is_valid=false, STOP and ask user for missing fields
3. For missing FKs, call list_foreign_key_options_tool and show options
4. Accept FK references by name/description, resolve to IDs internally
5. Display missing fields in a clear, friendly format
6. Wait for user to provide all required information before creating

❌ DO NOT:
1. NEVER call create_record_tool without validating first
2. NEVER proceed if is_valid=false
3. NEVER ask for optional fields (only required ones)
4. NEVER make up FK IDs - always query or list options
5. NEVER say "I don't have enough information" without showing what's missing

═══════════════════════════════════════════════════════════════════════════════
DISPLAYING MISSING FIELDS TO USER (TEMPLATE)
═══════════════════════════════════════════════════════════════════════════════

Use this format when asking for missing information:

"To create a [TABLE], I need the following required information:

❌ **Missing Required Fields:**
- **[field1]**: [description from required_fields_info]
- **[field2]**: [description]

[If FK fields exist:]
**Available [Related Table]:**
- [Option 1] (ID: X)
- [Option 2] (ID: Y)
- [Option 3] (ID: Z)

You provided:
- [field_a]: [value] ✓
- [field_b]: [value] ✓

Please provide the missing information."

═══════════════════════════════════════════════════════════════════════════════


═══════════════════════════════════════════════════════════════════════════════
COMMON MISTAKES TO AVOID
═══════════════════════════════════════════════════════════════════════════════

❌ WRONG: Passing FK field names instead of IDs
   data={"company": "Tech Solutions"}  ← Wrong! Use ID

✅ CORRECT: Pass FK as integer ID
   data={"company": 5}  ← Correct!

❌ WRONG: Not checking if FK record exists
   data={"supplier": 999}  ← May not exist!

✅ CORRECT: First query to verify record exists
   query_records(table="supplier", filters={"id": 999}) → then use

❌ WRONG: Missing required fields
   data={"name": "Test"}  ← Missing other required fields!

✅ CORRECT: Include all required fields from schema guide

❌ WRONG: Invalid choice values
   data={"status": "active"}  ← If choices are draft/sent/paid

✅ CORRECT: Use exact choice values from schema guide
   data={"status": "draft"}


═══════════════════════════════════════════════════════════════════════════════
DATA TYPE GUIDELINES
═══════════════════════════════════════════════════════════════════════════════

Date fields:        "2024-01-15" (YYYY-MM-DD format)
Decimal fields:     5000.00 (not "5000" string)
Boolean fields:     true/false (not "yes"/"no")
FK fields:          42 (integer ID only)
Choice fields:      Use EXACT value from schema choices

"""


# ============================================
# UPDATE OPERATION TEMPLATE
# ============================================
UPDATE_OPERATION_GUIDE = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                         UPDATE OPERATION GUIDE                               ║
╚══════════════════════════════════════════════════════════════════════════════╝

WORKFLOW FOR UPDATING A RECORD:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Step 1: Get the schema guide to understand available fields
Step 2: Get the current record to verify it exists and see current values
Step 3: Identify which fields need to change
Step 4: Call update_record with ONLY the changed fields
Step 5: Verify the update in the response

═══════════════════════════════════════════════════════════════════════════════
FEW-SHOT EXAMPLES
═══════════════════════════════════════════════════════════════════════════════

EXAMPLE 1: Update Company Name
────────────────────────────────────────────────────────────────────────────────
User: "Change company Tech Solutions name to Tech Solutions Inc"

LLM WORKFLOW:
1. Call query_records(table="company", text_search="Tech Solutions") → Find ID=5
2. Call get_record(table="company", record_id=5) → Verify it exists
3. Call update_record:

   update_record(
       table="company",
       record_id=5,
       data={
           "name": "Tech Solutions Inc"  # Only changed field
       }
   )

RESULT: ✅ Returns old_value and new_value for verification


EXAMPLE 2: Update Invoice Status
────────────────────────────────────────────────────────────────────────────────
User: "Mark invoice INV-2024-001 as paid"

LLM WORKFLOW:
1. Call get_invoice_schema_guide() → Learn status choices: draft/sent/paid/cancelled
2. Call query_records(table="invoice", text_search="INV-2024-001") → ID=123
3. Call get_record(table="invoice", record_id=123) → Current status="sent"
4. Call update_record:

   update_record(
       table="invoice",
       record_id=123,
       data={
           "status": "paid"
       }
   )


EXAMPLE 3: Update Multiple Fields
────────────────────────────────────────────────────────────────────────────────
User: "Update supplier ABC Corp - change email to new@abc.com and city to New York"

LLM WORKFLOW:
1. Call query_records(table="supplier", text_search="ABC Corp") → ID=10
2. Call get_record(table="supplier", record_id=10) → Verify and see current values
3. Call update_record:

   update_record(
       table="supplier",
       record_id=10,
       data={
           "contact_email": "new@abc.com",
           "city": "New York"
       }
   )


EXAMPLE 4: Update Foreign Key Reference
────────────────────────────────────────────────────────────────────────────────
User: "Move account Cash to company XYZ Corp"

LLM WORKFLOW:
1. Call query_records(table="account", text_search="Cash") → ID=15
2. Call query_records(table="company", text_search="XYZ Corp") → ID=8
3. Call update_record:

   update_record(
       table="account",
       record_id=15,
       data={
           "company": 8  # New company FK
       }
   )


═══════════════════════════════════════════════════════════════════════════════
COMMON MISTAKES TO AVOID
═══════════════════════════════════════════════════════════════════════════════

❌ WRONG: Including unchanged fields
   data={"name": "Same Name", "country": "Same Country", "status": "new"}

✅ CORRECT: Only include fields that are changing
   data={"status": "new"}

❌ WRONG: Updating without verifying record exists
   update_record(table="company", record_id=9999, data={...})

✅ CORRECT: First get_record to verify
   get_record(table="company", record_id=9999) → then update

❌ WRONG: Updating protected/auto fields
   data={"id": 100, "created_at": "2024-01-01"}

✅ CORRECT: Never update id, created_at, or auto-generated fields

❌ WRONG: Breaking unique constraints
   data={"account_number": "EXISTING-NUMBER"}  ← If already exists

✅ CORRECT: Check unique constraints in schema guide first


═══════════════════════════════════════════════════════════════════════════════
VERIFICATION AFTER UPDATE
═══════════════════════════════════════════════════════════════════════════════

The response includes "changes" with old_values and new_values:

{
    "updated": true,
    "id": 5,
    "record": { ... full updated record ... },
    "changes": {
        "old_values": {"name": "Tech Solutions"},
        "new_values": {"name": "Tech Solutions Inc"}
    }
}

Always verify the changes match what user requested!

"""


# ============================================
# DELETE OPERATION TEMPLATE
# ============================================
DELETE_OPERATION_GUIDE = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                         DELETE OPERATION GUIDE                               ║
╚══════════════════════════════════════════════════════════════════════════════╝

⚠️  DELETE IS A DESTRUCTIVE OPERATION - ALWAYS CONFIRM WITH USER FIRST!

WORKFLOW FOR DELETING A RECORD:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Step 1: Get the schema guide to understand relationships
Step 2: Get the record to verify it exists and show user what will be deleted
Step 3: Check for related/dependent records that might be affected
Step 4: ASK USER FOR CONFIRMATION before proceeding
Step 5: Call delete_record with confirm=True

═══════════════════════════════════════════════════════════════════════════════
FEW-SHOT EXAMPLES
═══════════════════════════════════════════════════════════════════════════════

EXAMPLE 1: Delete a Simple Record
────────────────────────────────────────────────────────────────────────────────
User: "Delete the accounting dimension called 'Region'"

LLM WORKFLOW:
1. Call get_accounting_dimension_schema_guide() → No critical relationships
2. Call query_records(table="accounting_dimension", text_search="Region") → ID=7
3. Call get_record(table="accounting_dimension", record_id=7) → Show details
4. ASK USER: "I found 'Region' dimension (ID: 7). Are you sure you want to delete it?"
5. User confirms → Call delete_record:

   delete_record(
       table="accounting_dimension",
       record_id=7,
       confirm=True
   )


EXAMPLE 2: Delete Record with Dependencies Check
────────────────────────────────────────────────────────────────────────────────
User: "Delete supplier ABC Corp"

LLM WORKFLOW:
1. Call get_supplier_schema_guide() → Has relationships: invoices, certificates
2. Call query_records(table="supplier", text_search="ABC Corp") → ID=10
3. Call get_record(table="supplier", record_id=10) → Check total_invoices=5
4. WARN USER: "Supplier ABC Corp has 5 related invoices. Deletion may fail if 
   invoices are protected. Do you want to proceed?"
5. User confirms → Call delete_record:

   delete_record(
       table="supplier",
       record_id=10,
       confirm=True
   )

If protected error: Report to user that they must delete related records first.


EXAMPLE 3: Safe Delete - No Related Records
────────────────────────────────────────────────────────────────────────────────
User: "Remove tax category 'Exempt Services'"

LLM WORKFLOW:
1. Call get_tax_category_schema_guide() → Related: tax_rules
2. Call query_records(table="tax_category", text_search="Exempt") → ID=3
3. Call get_record(table="tax_category", record_id=3) → total_rules=0
4. ASK USER: "Tax category 'Exempt Services' has no related rules. Safe to delete?"
5. User confirms → delete_record(table="tax_category", record_id=3, confirm=True)


EXAMPLE 4: Handling Protected Delete Failure
────────────────────────────────────────────────────────────────────────────────
User: "Delete company XYZ Corp"

LLM WORKFLOW:
1. Call get_company_schema_guide() → Many relationships (accounts, invoices, etc.)
2. Call query_records(table="company", text_search="XYZ Corp") → ID=8
3. Call get_record(table="company", record_id=8) → 
   total_accounts=15, total_invoices=50, total_suppliers=20
4. WARN USER: "Company XYZ Corp has 15 accounts, 50 invoices, and 20 suppliers. 
   This cannot be deleted directly. You must first:
   1. Delete or reassign all invoices
   2. Delete or reassign all accounts
   3. Delete or reassign all suppliers
   Do you want me to show you the related records?"


═══════════════════════════════════════════════════════════════════════════════
IMPORTANT SAFETY RULES
═══════════════════════════════════════════════════════════════════════════════

🔒 NEVER delete without user confirmation
🔒 ALWAYS show what will be deleted before proceeding
🔒 ALWAYS check related record counts
🔒 ALWAYS explain consequences to user
🔒 If protected error occurs, explain how to resolve


═══════════════════════════════════════════════════════════════════════════════
COMMON MISTAKES TO AVOID
═══════════════════════════════════════════════════════════════════════════════

❌ WRONG: Deleting without confirmation
   delete_record(table="company", record_id=5, confirm=True)  ← Without asking!

✅ CORRECT: Always ask user first
   "Found company X with Y related records. Confirm delete?" → then proceed

❌ WRONG: Not checking dependencies
   delete_record(table="company", ...) → Fails with ProtectedError

✅ CORRECT: Check related counts first
   get_record(table="company", record_id=5) → Check totals → Warn user

❌ WRONG: Setting confirm=False
   delete_record(table="invoice", record_id=123, confirm=False)  ← Won't delete!

✅ CORRECT: Must explicitly set confirm=True after user confirmation


═══════════════════════════════════════════════════════════════════════════════
RESPONSE AFTER DELETE
═══════════════════════════════════════════════════════════════════════════════

{
    "deleted": true,
    "id": 7,
    "deleted_record": {
        "id": 7,
        "name": "Region",
        ... full record data preserved for reference ...
    }
}

The deleted_record is returned so user can see exactly what was removed.

"""


# ============================================
# READ OPERATION TEMPLATE (GET/QUERY)
# ============================================
READ_OPERATION_GUIDE = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                         READ OPERATION GUIDE                                 ║
╚══════════════════════════════════════════════════════════════════════════════╝

TWO TOOLS FOR READING DATA:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

• get_record    → Get ONE record by ID (with related counts)
• query_records → Get MULTIPLE records with filters/search

═══════════════════════════════════════════════════════════════════════════════
WHEN TO USE EACH TOOL
═══════════════════════════════════════════════════════════════════════════════

USE get_record WHEN:
─────────────────────────────────────────────────────────────────────────────
✓ You have the exact ID
✓ User asks for "full details" of one record
✓ After search/query to get complete profile
✓ Before update/delete to verify existence

Example queries:
• "Show me company with ID 5"
• "Get full details of invoice 123"
• "What are the details of that supplier?"

USE query_records WHEN:
─────────────────────────────────────────────────────────────────────────────
✓ User wants to FIND records (doesn't know ID)
✓ User wants to LIST/FILTER records
✓ User wants to SEARCH by text
✓ User wants to see MULTIPLE records

Example queries:
• "Find companies in USA"
• "List all pending invoices"
• "Search for suppliers with 'tech' in name"
• "Show me accounts of type asset"


═══════════════════════════════════════════════════════════════════════════════
FEW-SHOT EXAMPLES
═══════════════════════════════════════════════════════════════════════════════

EXAMPLE 1: Simple Search → Get Details
────────────────────────────────────────────────────────────────────────────────
User: "Find company Tech Solutions and show full details"

LLM WORKFLOW:
1. query_records(table="company", text_search="Tech Solutions") → Returns list with ID=5
2. get_record(table="company", record_id=5) → Full details with related counts


EXAMPLE 2: List with Filters
────────────────────────────────────────────────────────────────────────────────
User: "Show all paid invoices from January 2024"

LLM WORKFLOW:
1. Call get_invoice_schema_guide() → Learn filter fields
2. query_records(
       table="invoice",
       filters={
           "status": "paid",
           "date__gte": "2024-01-01",
           "date__lte": "2024-01-31"
       }
   )


EXAMPLE 3: Complex Search with Filters
────────────────────────────────────────────────────────────────────────────────
User: "Find suppliers in Pakistan with 'import' in their name"

LLM WORKFLOW:
1. query_records(
       table="supplier",
       text_search="import",
       filters={"country": "Pakistan"}
   )


EXAMPLE 4: Paginated Results
────────────────────────────────────────────────────────────────────────────────
User: "Show me accounts page 2, 50 per page, sorted by name"

LLM WORKFLOW:
1. query_records(
       table="account",
       page=2,
       page_size=50,
       order_by="name"
   )


═══════════════════════════════════════════════════════════════════════════════
FILTER SYNTAX REFERENCE
═══════════════════════════════════════════════════════════════════════════════

EXACT MATCH:        {"field": "value"}
CONTAINS:           {"field__icontains": "text"}
GREATER THAN:       {"field__gt": value}
LESS THAN:          {"field__lt": value}
GREATER OR EQUAL:   {"field__gte": value}
LESS OR EQUAL:      {"field__lte": value}
IN LIST:            {"field__in": ["val1", "val2"]}
DATE RANGE:         {"field__range": ["2024-01-01", "2024-12-31"]}
IS NULL:            {"field__isnull": true}
STARTS WITH:        {"field__istartswith": "prefix"}
ENDS WITH:          {"field__iendswith": "suffix"}

COMBINE FILTERS (AND):
{
    "status": "paid",
    "amount__gte": 1000,
    "date__range": ["2024-01-01", "2024-06-30"]
}

"""


# ============================================
# TOOL FUNCTION TO GET OPERATION GUIDE
# ============================================

OPERATION_GUIDES = {
    "create": CREATE_OPERATION_GUIDE,
    "update": UPDATE_OPERATION_GUIDE,
    "delete": DELETE_OPERATION_GUIDE,
    "read": READ_OPERATION_GUIDE,
    "get": READ_OPERATION_GUIDE,
    "query": READ_OPERATION_GUIDE,
}


def get_crud_operation_guide(operation: str) -> str:
    """
    Get the detailed guide for a specific CRUD operation.
    
    Args:
        operation: One of "create", "update", "delete", "read" (or "get"/"query")
        
    Returns:
        Detailed guide with workflow and few-shot examples
    """
    operation_lower = operation.lower().strip()
    
    if operation_lower in OPERATION_GUIDES:
        return OPERATION_GUIDES[operation_lower]
    
    return f"""
Invalid operation: {operation}

Available operations:
• create - Guide for creating new records
• update - Guide for updating existing records  
• delete - Guide for deleting records
• read   - Guide for querying/getting records (also: get, query)

Usage: get_crud_operation_guide(operation="create")
"""


# Quick reference for system prompt
CRUD_WORKFLOW_SUMMARY = """
CRUD OPERATION WORKFLOW:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

For ANY data operation:
1. FIRST: Call get_<table>_schema_guide() to understand the table structure
2. THEN: Call get_crud_operation_guide(operation) for few-shot examples
3. FINALLY: Use the appropriate generic tool:
   • get_record(table, id)           → Read one record
   • query_records(table, ...)       → Read multiple records
   • create_record(table, data)      → Create new record
   • update_record(table, id, data)  → Update existing record
   • delete_record(table, id, True)  → Delete record (with confirmation)

CRITICAL: Never skip steps 1 and 2 - they prevent hallucination!
"""
