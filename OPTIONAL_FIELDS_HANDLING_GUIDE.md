# UPDATED CREATE WORKFLOW - Optional Fields Handling

## Summary of Changes

The chatbot CREATE workflow has been updated to:
1. **Ask for ALL fields** (required AND optional) upfront
2. **Only create with fields the user explicitly provided**
3. **Never auto-populate optional fields** without user consent
4. **Never inherit optional fields** from FK relationships

## The Problem We're Fixing

Previously, the chatbot could:
- Create records with unwanted optional fields
- Auto-populate company from linked account (causing data integrity issues)
- Add defaults for optional fields user never specified

Example of the bug:
```
User: "Create journal entry for account 95"
Account 95 belongs to Company 23
Chatbot WRONGLY created: {account: 95, company: 23}
Problem: User never said company=23!
```

## The Solution

### New Workflow

**Step 1**: Call `get_<table>_schema_guide()`

**Step 2**: Ask for ALL fields
- Show REQUIRED section
- Show OPTIONAL section
- For FK fields: Show available options

**Step 3**: Validate REQUIRED fields
- Call `validate_required_fields_tool(table, provided_data)`
- If missing: ask for missing REQUIRED fields only
- If valid: proceed to create

**Step 4**: Create with ONLY user-provided fields
```python
# User provided: name="ABC", company=22, email="abc@example.com"
# Chatbot creates:
create_record_tool(table="supplier", data={
    "name": "ABC",
    "company": 22,
    "email": "abc@example.com"
    # ❌ DON'T ADD: address, phone, city, state, gst_number, etc.
    # User didn't specify these, so DON'T include them!
})
```

## Example 1: Supplier Creation

### User Request
```
"Create supplier ABC Pvt Ltd from India"
```

### Chatbot Response - Step 1: Ask for ALL fields

```
To create a supplier, please provide the following information:

**REQUIRED Fields** (must provide):
- name: [already provided: ABC Pvt Ltd] ✓
- gst_category: Choose from registered/unregistered/SEZ/overseas
- supplier_type: Choose from company/individual/partnership

**OPTIONAL Fields** (provide only if you have):
- gstin_uin: GST/UIN number
- contact_first_name: Contact person first name
- contact_email: Email address
- contact_mobile: Mobile number
- address_line1: Street address
- city: City name
- state: State name
- country: Country (defaults to Pakistan if not specified)

You can skip optional fields you don't have. Just provide required fields
and any optional details you want to include.
```

### User Provides Missing Info
```
gst_category is registered, supplier_type is company, country is India, 
email is abc@example.com
```

### Chatbot Validates & Creates

```python
# Validation
validate_required_fields_tool(
    table="supplier",
    provided_data={
        "name": "ABC Pvt Ltd",
        "gst_category": "registered",
        "supplier_type": "company",
        "country": "India",
        "contact_email": "abc@example.com"
    }
)
# Response: {"is_valid": true}

# Create with ONLY user-provided fields
create_record_tool(
    table="supplier",
    data={
        "name": "ABC Pvt Ltd",
        "gst_category": "registered",
        "supplier_type": "company",
        "country": "India",
        "contact_email": "abc@example.com"
    }
)

# ❌ DO NOT INCLUDE (user didn't specify):
# - gstin_uin
# - contact_first_name, contact_last_name
# - contact_mobile
# - address_line1, city, state
# - preferred_billing, preferred_shipping
```

### Result
✅ Supplier created with 5 fields only

---

## Example 2: Customer with FK

### User Request
```
"Create customer John Smith"
```

### Chatbot Response - Ask for ALL

```
To create a customer, please provide:

**REQUIRED Fields**:
- name: [provided: John Smith] ✓
- company: Which company? Select from:
  1. TechCorp Solutions USA (ID: 22)
  2. Global Corp International (ID: 23)
  3. SmartTech Industries (ID: 24)

**OPTIONAL Fields** (provide if available):
- gst_number: Customer's GST number
- email: Email address
- phone: Phone number
- city: City name
- state: State name
- address: Street address

Please provide company (required) and any optional details.
```

### User Provides
```
Company is TechCorp Solutions USA, email is john@company.com
```

### Validation & Creation

```python
# Resolve FK: "TechCorp Solutions USA" → ID = 22

validate_required_fields_tool(
    table="customer",
    provided_data={
        "name": "John Smith",
        "company": 22,
        "email": "john@company.com"
    }
)
# Response: {"is_valid": true}

# Create with ONLY user-provided
create_record_tool(
    table="customer",
    data={
        "name": "John Smith",
        "company": 22,
        "email": "john@company.com"
    }
)

# ❌ DO NOT INCLUDE:
# - gst_number, phone, address, city, state (user didn't provide)
```

### Result
✅ Customer created with 3 fields only

---

## Example 3: Budget with Multiple FKs

### User Request
```
"Create budget for Marketing, fiscal year 2025"
```

### Chatbot asks for ALL:

```
**REQUIRED**:
- name: [provided: Marketing] ✓
- fiscal_year: [provided: 2025] ✓
- company: Which company?
  1. TechCorp Solutions USA (ID: 22)
  2. Global Corp International (ID: 23)
- cost_center: Which cost center?
  1. Marketing (ID: 5)
  2. Sales (ID: 6)
  3. Operations (ID: 7)

**OPTIONAL**:
- notes: Budget notes
- status: draft/active/archived
- total_amount: Total budget amount

Provide all required fields and any optional ones you want.
```

### User Provides
```
company is TechCorp Solutions USA, cost_center is Marketing, 
status is active, total_amount is 100000
```

### Create

```python
validate_required_fields_tool(
    table="budget",
    provided_data={
        "name": "Marketing",
        "fiscal_year": "2025",
        "company": 22,
        "cost_center": 5,
        "status": "active",
        "total_amount": 100000.00
    }
)
# {"is_valid": true}

create_record_tool(
    table="budget",
    data={
        "name": "Marketing",
        "fiscal_year": "2025",
        "company": 22,
        "cost_center": 5,
        "status": "active",
        "total_amount": 100000.00
    }
)

# ❌ DO NOT INCLUDE:
# - notes (user didn't provide)
```

### Result
✅ Budget created with 6 fields

---

## Critical Rules

### ✅ DO:
1. ALWAYS call `get_<table>_schema_guide()` first
2. Ask for BOTH required AND optional fields upfront
3. Clearly separate REQUIRED from OPTIONAL sections
4. For FK: Always show available options using `list_foreign_key_options_tool()`
5. Call `validate_required_fields_tool()` BEFORE `create_record_tool()`
6. CREATE with ONLY fields user explicitly specified
7. Let database handle defaults for unspecified fields

### ❌ DO NOT:
1. NEVER skip optional fields - always offer them
2. NEVER auto-populate optional fields without user consent
3. NEVER inherit optional FK values from relationships
4. NEVER add defaults for fields user didn't mention
5. NEVER create without validation
6. NEVER proceed if validation fails
7. NEVER assume optional fields should have default values

---

## The Journal Entry Issue (Fixed)

### The Problem
```
User: "Create journal entry for account 95"
Account 95 belongs to: TechCorp India Pvt Ltd (Company ID: 23)

Chatbot WRONGLY created:
{
    account: 95,
    company: 22  ← TechCorp Solutions USA (WRONG COMPANY!)
}
```

### Why It Happened
- Company field was OPTIONAL in JournalEntry model
- Chatbot auto-populated it from somewhere (user's default company?)
- Result: Data integrity violation

### The Fix
Now the workflow is:

1. Ask user for ALL journal entry fields
2. Show optional company field
3. Ask: "Should this journal entry be associated with a company?"
   - If YES: Show available options, user selects
   - If NO: Create without company field
4. Create with ONLY user-provided values

### Example of Corrected Flow
```
User: "Create journal entry for account 95"

Chatbot asks:
"To create a journal entry, please provide:

**REQUIRED**:
- entry_number: Unique entry ID
- date: Posting date
- account: [provided: account 95] ✓
- description: Transaction description

**OPTIONAL**:
- company: Should this entry be associated with a company?
  Available options:
  1. TechCorp Solutions USA (ID: 22)
  2. TechCorp India Pvt Ltd (ID: 23)
  3. Global Corp International (ID: 24)

Please provide all required fields and answer about company."

User: "entry_number is 55, date is today, description is 'Testing', 
NO company needed"

Chatbot creates:
{
    entry_number: "55",
    date: "2026-01-28",
    account: 95,
    description: "Testing"
    // ❌ NO company field - user didn't want it!
}
```

---

## Testing the Updated Workflow

Try these test cases:

1. **Supplier Creation** (Customer example)
   - Provide only required fields
   - Provide required + some optional
   - Verify only provided fields are saved

2. **Journal Entry Creation** (Fixed issue)
   - Don't specify company - verify it's not auto-populated
   - Specify company explicitly - verify it's saved
   - Verify account and journal entry belong to same company if user specifies

3. **Budget Creation** (Multiple FK)
   - Provide required + optional FK (company)
   - Verify no auto-inheritance
   - Verify only what user specified is saved

---

## Implementation Status

✅ CRUD prompt guide updated with examples
✅ New workflow documented
✅ Critical rules defined
✅ Ready for testing with non-JournalEntry examples

⏳ Next: Test with Supplier/Customer creation to validate new workflow
