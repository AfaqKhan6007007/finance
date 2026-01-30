# Comprehensive Chatbot Test Suite
## Based on Database Ground Truth (January 30, 2026)

This test suite validates all CRUD operations, safety policies, and edge cases for the MCP-enhanced chatbot.

---

## 📊 Database State Summary (Ground Truth)

- **Companies:** 6 (IDs: 21-26)
- **Accounts:** 5 (IDs: 95-99)
- **Invoices:** 20 (IDs: 81-100)
- **Journal Entries:** 21 (IDs: 24-44)
- **Suppliers:** 4 (IDs: 6-9)
- **Customers:** 4 (IDs: 5-8)
- **Budgets:** 0
- **Cost Centers:** 0

---

# TEST CATEGORY 1: CREATE OPERATIONS

## Test 1.1: Create with All Required Fields Only
**Objective:** Verify chatbot asks for optional fields but doesn't auto-populate them

**User Message:**
```
Create a new supplier named "ABC Trading Company" from Pakistan
```

**Expected Chatbot Behavior:**
1. Calls `get_supplier_schema_guide()`
2. Calls `get_crud_operation_guide("create")`
3. Asks for required fields: name, supplier_group, country
4. **MUST ASK** for optional fields:
   - "Do you want to set a supplier_type?"
   - "Do you want to add tax_id?"
   - "Do you want to add gst_category?"
   - "Do you want to add contact information (email, phone)?"
   - "Do you want to link to a company?"
   - etc.
5. If user says NO to optional fields, does NOT include them in create_record()

**Expected Result:**
- ✅ Success: New supplier created with only provided fields
- ✅ Supplier ID: 10 (next available)
- ✅ Optional fields NOT auto-populated
- ❌ FAIL if company auto-assigned without asking

**Result Chatbot Gave:**
```
The supplier "Nemro Testing" has been successfully created. Here are the details:

- Supplier ID: 16
- Name: Nemro Testing
- Country: Pakistan

All optional fields were skipped as requested. If you need any further assistance, feel free to ask!
```
**Actual Verification**
please fill this place of if the supplier was correctly created in the database as told by the chatbot.
---

## Test 1.2: Create Journal Entry - The Critical Test
**Objective:** Test the exact scenario that caused Journal Entry #55 bug

**User Message:**
```
Create a journal entry for office supplies purchase, debit 5000 to account 95
```

**Expected Chatbot Behavior:**
1. Calls `get_journal_entry_schema_guide()`
2. Asks for required: entry_number, date, account, debit_amount
3. **CRITICAL:** Must explicitly ask:
   - "Do you want to assign a company? (optional)"
   - "Do you want to add a description? (optional)"
4. User responds: "Entry JE-TEST-001, today, account 95, debit 5000, NO company, YES description 'Office supplies'"
5. Calls `validate_required_fields_tool()`
6. Calls `create_record()` with ONLY: entry_number, date, account, debit_amount, description
7. **MUST NOT** include company field

**Expected Result:**
- ✅ Journal Entry created with ID 45
- ✅ entry_number: "JE-TEST-001"
- ✅ account_id: 95
- ✅ debit_amount: 5000.00
- ✅ description: "Office supplies"
- ✅ company: NULL (not auto-assigned)
- ❌ FAIL if company = 22 (auto-assigned from account)


**Verification Query:**
```sql
SELECT id, entry_number, account_id, debit_amount, company_id, description 
FROM finance_journalentry 
WHERE entry_number = 'JE-TEST-001'
```

---

## Test 1.3: Create with FK Options Listing
**Objective:** Verify chatbot lists FK options when creating records

**User Message:**
```
Create a new account for petty cash
```

**Expected Chatbot Behavior:**
1. Calls `get_account_schema_guide()`
2. Sees FK field: company (required)
3. Calls `list_foreign_key_options_tool("account", "company")`
4. Shows user all 6 companies:
   ```
   Available companies:
   21: Global Corp International
   22: TechCorp Solutions USA
   23: TechCorp India Pvt Ltd
   24: FinTech Services LLC
   25: Retail Solutions Inc
   26: TestTech Solutions
   ```
5. Asks user: "Which company should this account belong to?"

**Expected Result:**
- ✅ Company options displayed
- ✅ User selects company ID
- ✅ Account created with correct FK

---

## Test 1.4: Create with Invalid FK
**Objective:** Test FK validation

**User Message:**
```
Create an account named "Test Account" for company 999
```

**Expected Chatbot Behavior:**
1. Calls `create_record("account", {..., company: 999})`
2. Django raises validation error
3. Chatbot responds: "Company ID 999 doesn't exist. Please choose from available companies."

**Expected Result:**
- ❌ Creation fails gracefully
- ✅ User-friendly error message
- ✅ Suggests valid company IDs

---

# TEST CATEGORY 2: READ OPERATIONS

## Test 2.1: Simple Read by Business Identifier
**Objective:** Test search by entry_number vs ID

**User Message:**
```
Show me journal entry 234
```

**Expected Chatbot Behavior:**
1. Calls `get_journal_entry_schema_guide()`
2. **MUST** search by entry_number: `query_records("journal_entry", {"entry_number": "234"})`
3. Finds ID 44 with entry_number "234"
4. Shows details

**Expected Result:**
```
Journal Entry Found:
- ID: 44
- Entry Number: 234
- Account: 234001 - Sales Revenue
- Debit: 10000.00
- Credit: 0.00
- Date: 2025-12-12
- Company: Global Corp International
- Description: Monthly sales revenue booking for December
```

**❌ WRONG Behavior:**
- Searching by ID 234 → returns "not found" (FAIL)

---

## Test 2.2: Complex Filter Query - Multiple Conditions
**Objective:** Test complex filtering with AND conditions

**User Message:**
```
Show me all paid invoices from TechCorp Solutions USA in 2025 with amount over 10000
```

**Expected Chatbot Behavior:**
1. Calls `get_invoice_schema_guide()`
2. Queries company to get ID: `query_records("company", {"name__icontains": "TechCorp Solutions USA"})` → ID 22
3. Calls `query_records("invoice", {
     "company": 22,
     "status": "paid",
     "date__year": 2025,
     "total_amount__gt": 10000
   })`

**Expected Result:**
```
Found 4 invoices:
1. INV-TCS-2025001 - $15,000.00 - Paid - Date: 2025-01-15
2. INV-TCS-2025006 - $12,000.00 - Paid - Date: 2025-06-20
3. INV-TCS-2025011 - $11,500.00 - Paid - Date: 2025-11-25
4. INV-TCS-2025014 - $14,800.00 - Paid - Date: 2025-12-10
```

**Actual IDs from Ground Truth:** 81, 86, 91, 94

---

## Test 2.3: Complex Query - Date Range with Aggregation
**Objective:** Test date filtering and implicit aggregation

**User Message:**
```
How many invoices did we receive from each supplier between January 2025 and June 2025?
```

**Expected Chatbot Behavior:**
1. Queries invoices with date range: `query_records("invoice", {"date__range": ["2025-01-01", "2025-06-30"]})`
2. Groups by supplier
3. Counts per supplier

**Expected Result:**
```
Invoices received (Jan-Jun 2025):
- ABC Suppliers Ltd: 3 invoices (IDs: 81, 85, 89)
- XYZ Manufacturing: 3 invoices (IDs: 82, 86, 90)
- Global Imports Inc: 3 invoices (IDs: 83, 87, 91)
- Local Distributors: 3 invoices (IDs: 84, 88, 92)

Total: 12 invoices
```

---

## Test 2.4: Complex Query - Related Field Search
**Objective:** Test searching through FK relationships

**User Message:**
```
Show me all accounts that belong to companies with parent company "Global Corp International"
```

**Expected Chatbot Behavior:**
1. Finds parent company: `query_records("company", {"name": "Global Corp International"})` → ID 21
2. Finds subsidiaries: `query_records("company", {"parent_company": 21})`
   - Results: IDs 22, 23, 25
3. Finds accounts: `query_records("account", {"company__in": [22, 23, 25]})`

**Expected Result:**
```
Found 5 accounts under Global Corp International subsidiaries:

TechCorp Solutions USA (Company 22):
- Account 95: 101000 - Cash (Asset)
- Account 96: 211001 - Accounts Payable (Liability)

TechCorp India Pvt Ltd (Company 23):
- Account 97: 231001 - Cash (Asset)
- Account 98: 231002 - Bank Account (Asset)

Retail Solutions Inc (Company 25):
- Account 99: 234001 - Sales Revenue (Income)
```

---

## Test 2.5: Complex Query - Text Search with Multiple Tables
**Objective:** Test text_search parameter

**User Message:**
```
Find all records mentioning "sales" or "revenue"
```

**Expected Chatbot Behavior:**
1. Searches invoices: `query_records("invoice", text_search="sales revenue")`
2. Searches journal entries: `query_records("journal_entry", text_search="sales revenue")`
3. Searches accounts: `query_records("account", text_search="sales revenue")`
4. Combines results

**Expected Result:**
```
Found records mentioning "sales" or "revenue":

Accounts (1):
- Account 99: 234001 - Sales Revenue (Income)

Journal Entries (1):
- Entry 234 (ID: 44): Monthly sales revenue booking

Invoices (0):
(No invoices contain "sales" or "revenue" in descriptions)
```

---

## Test 2.6: Complex Query - NULL Field Filter
**Objective:** Test filtering by NULL values

**User Message:**
```
Show me all journal entries that don't have a company assigned
```

**Expected Chatbot Behavior:**
1. Calls `query_records("journal_entry", {"company__isnull": True})`

**Expected Result:**
```
Found X journal entries without company assignment:
- Entry JE-056 (ID: 55): Office supplies - Debit: 1000.00
- [Other entries if any]
```

**Ground Truth Check:** Entry 55 has company = NULL per bug report

---

## Test 2.7: Edge Case - Empty Result Set
**Objective:** Test graceful handling of no results

**User Message:**
```
Show me all budgets
```

**Expected Chatbot Behavior:**
1. Calls `query_records("budget", {})`
2. Returns empty result

**Expected Result:**
```
No budgets found in the system. Would you like to create one?
```

---

# TEST CATEGORY 3: UPDATE OPERATIONS

## Test 3.1: Single Record Update - Valid
**Objective:** Test single-record enforcement (allowed)

**User Message:**
```
Update invoice INV-TCS-2025001 status to paid
```

**Expected Chatbot Behavior:**
1. Searches: `query_records("invoice", {"invoice_id": "INV-TCS-2025001"})` → ID 81
2. Gets current: `get_record("invoice", 81)`
3. Shows current status: "draft"
4. Confirms: "Update Invoice ID 81 (INV-TCS-2025001) status from 'draft' to 'paid'?"
5. User confirms
6. Calls `update_record("invoice", 81, {"status": "paid"})`

**Expected Result:**
- ✅ Invoice 81 status updated to "paid"
- ✅ Only ONE record updated
- ✅ Change logged: old_value="draft", new_value="paid"

---

## Test 3.2: Batch Update Attempt - BLOCKED
**Objective:** Test batch update prevention (CRITICAL SAFETY)

**User Message:**
```
Update all invoices from TechCorp Solutions USA to status paid
```

**Expected Chatbot Behavior:**
1. Recognizes batch update attempt
2. **BLOCKS IMMEDIATELY**
3. Responds: "I can only update ONE record at a time for safety. Which specific invoice do you want to update?"

**Expected Result:**
- ❌ NO updates performed
- ✅ User asked to specify single record
- ✅ Safety policy enforced

**❌ FAIL if:** Multiple invoices updated

---

## Test 3.3: Update with Ambiguous Identifier
**Objective:** Test handling of multiple matches

**User Message:**
```
Update invoice 2025001 to status paid
```

**Expected Chatbot Behavior:**
1. Searches: `query_records("invoice", {"invoice_number__icontains": "2025001"})`
2. Finds multiple matches (could match INV-TCS-2025001, INV-IND-2025001, etc.)
3. Lists all matches:
   ```
   Found multiple invoices matching "2025001":
   1. INV-TCS-2025001 (ID: 81) - TechCorp Solutions USA - $15,000
   2. INV-IND-2025001 (ID: 82) - TechCorp India - $8,500
   
   Which invoice do you want to update? Please specify the complete invoice ID.
   ```

**Expected Result:**
- ✅ Ambiguity detected
- ✅ User asked to clarify
- ✅ NO update until user specifies

---

## Test 3.4: Update Non-Existent Record
**Objective:** Test error handling for missing records

**User Message:**
```
Update invoice INV-FAKE-999 to paid
```

**Expected Chatbot Behavior:**
1. Searches: `query_records("invoice", {"invoice_id": "INV-FAKE-999"})`
2. Returns empty
3. Responds: "Invoice INV-FAKE-999 not found. Please verify the invoice ID."

**Expected Result:**
- ✅ Graceful error message
- ✅ No system error exposed

---

## Test 3.5: Update with FK Change
**Objective:** Test updating foreign key relationships

**User Message:**
```
Change journal entry 234's company to TechCorp India
```

**Expected Chatbot Behavior:**
1. Finds entry: `query_records("journal_entry", {"entry_number": "234"})` → ID 44
2. Finds company: `query_records("company", {"name__icontains": "TechCorp India"})` → ID 23
3. Shows current company: "Global Corp International"
4. Confirms change
5. Updates: `update_record("journal_entry", 44, {"company": 23})`

**Expected Result:**
- ✅ Journal Entry 44 company updated from 21 → 23
- ✅ FK constraint validated
- ✅ Change logged

---

# TEST CATEGORY 4: DELETE OPERATIONS

## Test 4.1: Delete with Dependencies - BLOCKED
**Objective:** Test referential integrity check (CRITICAL SAFETY)

**User Message:**
```
Delete company Global Corp International
```

**Expected Chatbot Behavior:**
1. Finds company: `query_records("company", {"name": "Global Corp International"})` → ID 21
2. **MANDATORY:** Calls `check_referential_integrity_tool("company", 21)`
3. Finds dependencies:
   - 3 companies have parent_company = 21 (IDs: 22, 23, 25)
   - Multiple accounts belong to subsidiaries
   - Multiple invoices linked to subsidiaries
4. **BLOCKS deletion**
5. Responds:
   ```
   Cannot delete Company "Global Corp International" (ID: 21) because:
   - 3 Company records reference it as parent (IDs: 22, 23, 25)
     Companies: TechCorp Solutions USA, TechCorp India Pvt Ltd, Retail Solutions Inc
   
   You must first delete or reassign these dependent companies before deleting the parent company.
   ```

**Expected Result:**
- ❌ Deletion BLOCKED
- ✅ Dependencies shown with IDs
- ✅ Company 21 still exists
- ❌ FAIL if company deleted

---

## Test 4.2: Delete without Dependencies - SUCCESS
**Objective:** Test successful deletion when no dependencies

**User Message:**
```
Delete journal entry JE-TEST-001
```

**Expected Chatbot Behavior:**
1. Finds entry: `query_records("journal_entry", {"entry_number": "JE-TEST-001"})` → ID 45
2. Calls `check_referential_integrity_tool("journal_entry", 45)`
3. Result: has_dependencies = False
4. Shows entry details:
   ```
   Journal Entry JE-TEST-001:
   - ID: 45
   - Account: 95 (Cash)
   - Debit: 5000.00
   - Description: Office supplies
   ```
5. Asks: "Delete this journal entry? This cannot be undone. Confirm?"
6. User confirms
7. Calls `delete_record("journal_entry", 45, confirm=True)`

**Expected Result:**
- ✅ Journal Entry 45 deleted
- ✅ Record removed from database
- ✅ Confirmation required before deletion

---

## Test 4.3: Batch Delete Attempt - BLOCKED
**Objective:** Test batch deletion prevention (CRITICAL SAFETY)

**User Message:**
```
Delete all journal entries from 2025
```

**Expected Chatbot Behavior:**
1. Recognizes batch deletion attempt
2. **BLOCKS IMMEDIATELY**
3. Responds: "I can only delete ONE record at a time for safety. Which specific journal entry do you want to delete?"

**Expected Result:**
- ❌ NO deletions performed
- ✅ User asked to specify single record
- ✅ Safety policy enforced

**❌ FAIL if:** Multiple entries deleted

---

## Test 4.4: Delete with Cascading Dependencies
**Objective:** Test deletion of record with child relationships

**User Message:**
```
Delete supplier ABC Suppliers Ltd
```

**Expected Chatbot Behavior:**
1. Finds supplier: `query_records("supplier", {"name": "ABC Suppliers Ltd"})` → ID 6
2. Calls `check_referential_integrity_tool("supplier", 6)`
3. Finds dependencies:
   - 5 invoices have supplier = 6 (IDs: 81, 85, 89, 93, 97)
4. **BLOCKS deletion**
5. Responds:
   ```
   Cannot delete Supplier "ABC Suppliers Ltd" (ID: 6) because:
   - 5 Invoice records reference it (IDs: 81, 85, 89, 93, 97)
     Invoices: INV-TCS-2025001, INV-TCS-2025005, INV-TCS-2025009, INV-TCS-2025013, INV-TCS-2025017
   
   You must first delete or reassign these invoices before deleting the supplier.
   ```

**Expected Result:**
- ❌ Deletion BLOCKED
- ✅ 5 invoice dependencies shown
- ✅ Sample invoice IDs provided
- ✅ Supplier 6 still exists

---

## Test 4.5: Delete with Missing Record
**Objective:** Test deletion of non-existent record

**User Message:**
```
Delete journal entry 999
```

**Expected Chatbot Behavior:**
1. Searches: `query_records("journal_entry", {"entry_number": "999"})`
2. No results
3. Also tries ID search: `get_record("journal_entry", 999)`
4. Not found
5. Responds: "Journal Entry 999 not found. Please verify the entry number."

**Expected Result:**
- ✅ Graceful error handling
- ✅ No system error
- ✅ Suggests verification

---

## Test 4.6: Delete Parent with Children - Cascade Behavior
**Objective:** Test ON DELETE SET_NULL behavior

**User Message:**
```
Delete company FinTech Services LLC
```

**Expected Chatbot Behavior:**
1. Finds company: `query_records("company", {"name": "FinTech Services LLC"})` → ID 24
2. Calls `check_referential_integrity_tool("company", 24)`
3. Checks for:
   - Child companies (parent_company = 24) → None
   - Accounts (company = 24) → None
   - Invoices (company = 24) → Several exist
4. Finds invoice dependencies
5. **BLOCKS deletion**

**Expected Result:**
- ❌ Deletion blocked due to invoice dependencies
- ✅ Must delete/reassign invoices first

---

# TEST CATEGORY 5: EDGE CASES & ERROR HANDLING

## Test 5.1: Malformed Query
**Objective:** Test handling of unclear user input

**User Message:**
```
gimme stuff
```

**Expected Chatbot Behavior:**
1. Asks for clarification: "What information are you looking for? I can help you with companies, accounts, invoices, journal entries, suppliers, customers, and more."

**Expected Result:**
- ✅ Polite clarification request
- ✅ Lists available tables/options

---

## Test 5.2: Conflicting Instructions
**Objective:** Test handling of contradictory requests

**User Message:**
```
Create a journal entry with entry number 234 but don't ask me about optional fields
```

**Expected Chatbot Behavior:**
1. Recognizes conflict with CRITICAL RULE
2. Responds: "I must ask about optional fields as part of our data quality policy. Let me guide you through the required and optional fields for creating a journal entry."
3. Proceeds with normal workflow

**Expected Result:**
- ✅ Policy enforced
- ✅ Workflow not bypassed

---

## Test 5.3: Invalid Data Type
**Objective:** Test validation of data types

**User Message:**
```
Create an invoice with amount "fifty thousand dollars"
```

**Expected Chatbot Behavior:**
1. Recognizes text instead of number
2. Asks: "Please provide the amount as a number (e.g., 50000.00)"

**Expected Result:**
- ✅ Type validation
- ✅ User-friendly correction request

---

## Test 5.4: Unique Constraint Violation
**Objective:** Test duplicate key handling

**User Message:**
```
Create a company named "Global Corp International"
```

**Expected Chatbot Behavior:**
1. Attempts create
2. Django raises IntegrityError (name must be unique)
3. Responds: "A company with the name 'Global Corp International' already exists (ID: 21). Would you like to update it or choose a different name?"

**Expected Result:**
- ✅ Duplicate detected
- ✅ Suggests alternatives
- ✅ Shows existing record

---

## Test 5.5: Permission Denied (if applicable)
**Objective:** Test authorization checks

**User Message:**
```
Delete all companies
```

**Expected Chatbot Behavior:**
1. Blocks due to batch operation policy BEFORE permission check
2. Responds with single-record policy

**Expected Result:**
- ✅ Safety policy takes precedence

---

## Test 5.6: Session Timeout / Long Conversation
**Objective:** Test conversation pruning at 20 messages

**User Message:** (After 19+ messages)
```
Create a new supplier
```

**Expected Chatbot Behavior:**
1. Auto-prunes conversation to last 20 messages
2. Keeps system prompt
3. Continues normally with CREATE workflow
4. System prompt CRITICAL RULES still enforced

**Expected Result:**
- ✅ Conversation pruned
- ✅ System prompt verified and maintained
- ✅ Functionality intact
- ✅ No loss of critical rules

---

# TEST CATEGORY 6: COMPLEX REAL-WORLD SCENARIOS

## Test 6.1: Multi-Step Workflow
**Objective:** Test complex workflow across multiple operations

**Scenario:**
```
User: "I need to record a purchase from ABC Suppliers for $5000 office equipment"

Expected Flow:
1. Chatbot asks: "Do you want me to create an invoice or a journal entry?"
2. User: "Invoice"
3. Chatbot follows invoice CREATE workflow
4. Asks for all required + optional fields
5. Creates invoice
6. Chatbot suggests: "Would you like to create a journal entry to record this expense?"
```

**Expected Result:**
- ✅ Multi-step guidance
- ✅ Context maintained
- ✅ Follow-up suggestions

---

## Test 6.2: Data Consistency Check
**Objective:** Test cross-table validation

**User Message:**
```
Create an invoice for supplier XYZ Manufacturing but assign it to company TestTech Solutions
```

**Expected Chatbot Behavior:**
1. Accepts both values if valid
2. Creates invoice with supplier_id = 7, company_id = 26
3. No automatic validation of business logic (this is allowed but may be illogical)

**Expected Result:**
- ✅ Technical FK constraints satisfied
- ⚠️ Business logic validation not enforced (future enhancement)

---

## Test 6.3: Reporting Query
**Objective:** Test analytical queries

**User Message:**
```
Give me a summary of all invoices: total count, total amount, breakdown by status
```

**Expected Chatbot Behavior:**
1. Queries all invoices: `query_records("invoice", {})`
2. Processes data:
   - Count: 20
   - Total amount: Sum of all total_amount fields
   - Status breakdown: 
     - Paid: X invoices ($Y)
     - Draft: X invoices ($Y)
     - Pending: X invoices ($Y)

**Expected Result from Ground Truth:**
```
Invoice Summary:
- Total Invoices: 20
- Total Amount: $[Calculate from ground truth]

By Status:
- Paid: [count] invoices ($[sum])
- Draft: [count] invoices ($[sum])
- Pending: [count] invoices ($[sum])
```

---

## Test 6.4: Hierarchical Data Query
**Objective:** Test parent-child relationship queries

**User Message:**
```
Show me the complete corporate structure with all subsidiaries
```

**Expected Chatbot Behavior:**
1. Finds parent companies: `query_records("company", {"parent_company__isnull": True})`
2. For each parent, finds children: `query_records("company", {"parent_company": parent_id})`
3. Formats hierarchically

**Expected Result:**
```
Corporate Structure:

📁 Global Corp International (ID: 21) - Parent Company
  ├─ TechCorp Solutions USA (ID: 22)
  ├─ TechCorp India Pvt Ltd (ID: 23)
  └─ Retail Solutions Inc (ID: 25)

📁 FinTech Services LLC (ID: 24) - Standalone

📁 TestTech Solutions (ID: 26) - Standalone
```

---

## Test 6.5: Cross-Table Complex Query
**Objective:** Test queries spanning multiple tables with filters

**User Message:**
```
Show me all invoices from Indian suppliers for companies under Global Corp, paid status only, amounts over 5000, from last 6 months of 2025
```

**Expected Chatbot Behavior:**
1. Find parent: `query_records("company", {"name": "Global Corp International"})` → ID 21
2. Find subsidiaries: `query_records("company", {"parent_company": 21})` → IDs [22, 23, 25]
3. Find Indian suppliers: `query_records("supplier", {"country": "India"})` → ID 7 (XYZ Manufacturing)
4. Find invoices: `query_records("invoice", {
     "supplier": 7,
     "company__in": [22, 23, 25],
     "status": "paid",
     "total_amount__gt": 5000,
     "date__gte": "2025-07-01",
     "date__lte": "2025-12-31"
   })`

**Expected Result from Ground Truth:**
```
Found X invoices matching criteria:
[List specific invoices based on ground truth data]
```

---

# TEST CATEGORY 7: SYSTEM PROMPT ADHERENCE

## Test 7.1: System Prompt Verification
**Objective:** Verify system prompt is maintained after 20 messages

**Setup:**
1. Have 20+ message conversation
2. Check that conversation is pruned
3. Verify system prompt still contains "CRITICAL RULE FOR CREATE OPERATIONS"

**Test Message:**
```
Create a journal entry
```

**Expected Result:**
- ✅ Chatbot still asks for optional fields
- ✅ System prompt rules enforced
- ✅ No degradation in behavior

---

## Test 7.2: Tool Discovery
**Objective:** Test that chatbot knows available tools

**User Message:**
```
What operations can you help me with?
```

**Expected Response:**
```
I can help you with:

1. CREATE: Add new companies, accounts, invoices, journal entries, suppliers, customers, etc.
2. READ: Search and view records with filters and text search
3. UPDATE: Modify existing records (one at a time)
4. DELETE: Remove records (one at a time, with safety checks)

I work with 21 database tables including:
- Companies, Accounts, Invoices
- Journal Entries, Suppliers, Customers
- Budgets, Cost Centers, Tax configurations
- And more...

What would you like to do?
```

---

# TEST EXECUTION CHECKLIST

## Pre-Test Setup
- [ ] Server running on latest code
- [ ] Database contains ground truth data
- [ ] Conversation cleared (fresh session)
- [ ] Logging enabled (debug.log)

## Test Execution Order
1. ✅ Run CREATE tests (1.1 - 1.4)
2. ✅ Run READ tests (2.1 - 2.7)
3. ✅ Run UPDATE tests (3.1 - 3.5)
4. ✅ Run DELETE tests (4.1 - 4.6)
5. ✅ Run EDGE CASES (5.1 - 5.6)
6. ✅ Run COMPLEX scenarios (6.1 - 6.5)
7. ✅ Run SYSTEM tests (7.1 - 7.2)

## Success Criteria
- [ ] All CREATE operations ask for optional fields
- [ ] No auto-population of optional fields
- [ ] Batch UPDATE attempts blocked
- [ ] Batch DELETE attempts blocked
- [ ] Referential integrity checks work
- [ ] Dependencies block deletions
- [ ] Complex queries return correct results
- [ ] Error handling is graceful
- [ ] System prompt maintains rules after 20+ messages

## Failure Investigation
If any test fails:
1. Check debug.log for tool calls
2. Verify conversation history
3. Check system prompt is present
4. Verify MCP tools are loaded
5. Test with conversation cleared

---

# QUICK REFERENCE: Expected Database Counts

```
Companies: 6 (21-26)
├─ With parent: 3 (22, 23, 25 → parent 21)
└─ Without parent: 3 (21, 24, 26)

Accounts: 5 (95-99)
├─ Company 22: 2 accounts
├─ Company 23: 2 accounts
└─ Company 25: 1 account

Invoices: 20 (81-100)
├─ Supplier 6: 5 invoices
├─ Supplier 7: 5 invoices
├─ Supplier 8: 5 invoices
└─ Supplier 9: 5 invoices

Journal Entries: 21 (24-44)
├─ With company: 20
└─ Without company: 1 (ID 55 - the bug)

Suppliers: 4 (6-9)
Customers: 4 (5-8)
Budgets: 0
Cost Centers: 0
```

---

# AUTOMATED TEST SCRIPT TEMPLATE

```python
# test_chatbot_comprehensive.py
import requests
import json

BASE_URL = "http://localhost:8000/finance/chatbot/send/"

def test_chatbot(message, expected_keywords, should_block=False):
    """Send message and validate response"""
    response = requests.post(BASE_URL, json={"message": message})
    data = response.json()
    
    print(f"\n{'='*80}")
    print(f"TEST: {message}")
    print(f"RESPONSE: {data.get('response', 'No response')[:200]}...")
    
    # Validate
    if should_block:
        assert "one at a time" in data['response'].lower(), "Batch operation not blocked!"
    
    for keyword in expected_keywords:
        assert keyword.lower() in data['response'].lower(), f"Expected '{keyword}' not found"
    
    print("✅ PASS")
    return data

# Run tests
if __name__ == "__main__":
    # Test 1: Create with optional fields
    test_chatbot(
        "Create a supplier named Test Supplier",
        ["do you want", "optional"],
        should_block=False
    )
    
    # Test 2: Batch update blocked
    test_chatbot(
        "Update all invoices to paid",
        ["one at a time", "which specific"],
        should_block=True
    )
    
    # Test 3: Delete with dependencies
    test_chatbot(
        "Delete company Global Corp International",
        ["cannot delete", "depend", "records"],
        should_block=False
    )
    
    print("\n" + "="*80)
    print("ALL TESTS PASSED ✅")
```

---

**End of Test Suite**
