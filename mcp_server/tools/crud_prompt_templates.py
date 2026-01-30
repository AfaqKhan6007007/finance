"""
CRUD Operation Prompt Templates - CONCISE VERSION
"""

CREATE_OPERATION_GUIDE = """CREATE WORKFLOW:

1. get_<table>_schema_guide() → Identifies REQUIRED vs OPTIONAL fields
2. ASK user for EVERY field (required + optional)
   - For optional: "Do you want to set [field]?" 
   - User says NO → Don't include in create_record
   - User says YES → Ask for value, include in create_record
3. validate_required_fields_tool(table, data) → Check required fields present
4. If invalid: Show missing required fields, STOP
5. If valid: create_record(table, {ONLY fields user explicitly provided})

CRITICAL: Never auto-populate optional fields. If user doesn't provide it, don't include it.

JOURNAL ENTRY Example:
User: "Create journal entry for office supplies"
→ Schema shows: Required(entry_number, date, account, debit/credit) Optional(company, description)
→ Ask: "Entry#? Date? Account? Debit/Credit? Do you want a company (optional)? Description (optional)?"
→ User: "JE056, today, account 95, debit 1000, NO company, YES desc: Office supplies"
→ validate → valid
→ create_record(journal_entry, {entry_number, date, account, debit_amount, description})
→ Result: company NOT in data because user said NO

WRONG: Auto-assigning company without asking, skipping optional field questions
The above one shot example MUST be followed EXACTLY for all schemas and tables.
For FKs: Use list_foreign_key_options_tool(table, fk_field)"""


UPDATE_OPERATION_GUIDE = """UPDATE WORKFLOW:

⚠️ CRITICAL RESTRICTION:
- ONLY ONE RECORD AT A TIME - Never update multiple records in batch
- ALWAYS confirm exact record ID with user before updating

Mandatory Steps:
1. get_<table>_schema_guide() → Learn available fields and constraints
2. Identify exact record: query_records() or ask for ID
3. get_record(table, record_id) → Get current values, show to user
4. CONFIRM with user: "You want to update [TableName] ID [X], correct?"
5. Ask user what fields to change
6. update_record(table, record_id, {ONLY changed fields})

Example - SINGLE RECORD:
User: "Change invoice INV-001 status to paid"
→ query_records(invoice, {invoice_id: "INV-001"}) → ID=5
→ get_record(invoice, 5) → Current: {status: "draft", amount: 5000}
→ Ask: "Update Invoice ID 5 (INV-001)? Current status is 'draft', change to 'paid'?"
→ User confirms
→ update_record(invoice, 5, {status: "paid"})

NEVER attempt to update multiple records even if user asks "update all invoices"
→ Response: "I can only update ONE record at a time for safety. Which specific invoice do you want to update?"

Example - BATCH REQUEST DENIED:
User: "Update all companies in USA to add tax_id 123"
→ RESPONSE: "I can only update ONE company at a time. Please specify which company you want to update."
"""


DELETE_OPERATION_GUIDE = """DELETE WORKFLOW:

⚠️ CRITICAL RESTRICTIONS:
- ONLY ONE RECORD AT A TIME - Never delete multiple records in batch
- ALWAYS check referential integrity BEFORE deletion
- BLOCK deletion if dependencies exist - show user what depends on it

Mandatory Steps:
1. get_<table>_schema_guide() → Learn table structure
2. Identify record: query_records() or get_record() → Get exact ID
3. CHECK INTEGRITY: check_referential_integrity_tool(table, record_id)
4. If has_dependencies=True:
   a. STOP - DO NOT proceed with deletion
   b. Show user the dependencies with counts and sample IDs
   c. Explain: "Cannot delete because X records in Y table depend on it"
   d. Ask user to delete/reassign dependencies first
   e. END workflow
5. If has_dependencies=False:
   a. Show record details to user
   b. ASK FOR CONFIRMATION (mandatory!)
   c. delete_record(table, record_id, confirm=True)

Example - DELETION BLOCKED:
User: "Delete company ABC Corp"
→ query_records(company, {name: "ABC Corp"}) → ID=22
→ check_referential_integrity_tool(company, 22)
→ Result: has_dependencies=True, dependencies=[{table: "account", count: 5, sample_ids: [95,96,97,98,99]}]
→ RESPONSE: "Cannot delete ABC Corp (ID: 22) because 5 Account records depend on it (IDs: 95, 96, 97, 98, 99). You must delete or reassign these accounts first."
→ STOP - Do not call delete_record

Example - DELETION ALLOWED:
User: "Delete journal entry JE-056"
→ query_records(journal_entry, {entry_number: "JE-056"}) → ID=140
→ check_referential_integrity_tool(journal_entry, 140)
→ Result: has_dependencies=False, can_delete=True
→ get_record(journal_entry, 140) → Show details
→ Ask: "Delete JE-056 (Office Supplies, $1000)? This cannot be undone. Confirm?"
→ User confirms
→ delete_record(journal_entry, 140, confirm=True)

NEVER attempt to delete multiple records even if user asks "delete all X"
→ Response: "I can only delete ONE record at a time for safety. Which specific record do you want to delete?"
"""


READ_OPERATION_GUIDE = """READ WORKFLOW:

Single record:
→ get_<table>_schema_guide()
→ get_record(table, record_id)

Multiple records:
→ get_<table>_schema_guide()
→ query_records(table, filters, text_search, page, page_size)

For date ranges use: date__gte, date__lte
For text search use: text_search parameter"""


OPERATION_GUIDES = {
    "create": CREATE_OPERATION_GUIDE,
    "update": UPDATE_OPERATION_GUIDE,
    "delete": DELETE_OPERATION_GUIDE,
    "read": READ_OPERATION_GUIDE,
    "get": READ_OPERATION_GUIDE,
    "query": READ_OPERATION_GUIDE,
}


def get_crud_operation_guide(operation: str) -> str:
    """Get concise guide for a CRUD operation"""
    operation_lower = operation.lower().strip()
    
    if operation_lower in OPERATION_GUIDES:
        return OPERATION_GUIDES[operation_lower]
    
    return f"""Invalid operation: {operation}
Available: create, update, delete, read (or get/query)
Usage: get_crud_operation_guide("create")"""


CRUD_WORKFLOW_SUMMARY = """CRUD WORKFLOW:
1. FIRST: get_<table>_schema_guide()
2. THEN: get_crud_operation_guide(operation)
3. FINALLY: Use appropriate tool (get_record/query_records/create_record/update_record/delete_record)"""
