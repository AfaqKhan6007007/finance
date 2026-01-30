# TEST CASE FOR NEW OPTIONAL FIELDS WORKFLOW

## Test Scenario: Create Supplier (Non-Journal Entry Example)

This test uses **Supplier** instead of JournalEntry to validate the new optional fields workflow.

---

## User Prompt

```
"Create a new supplier named Tech Supplies Ltd, supplier type is company, 
and GST category is registered"
```

---

## Expected Chatbot Behavior

### Step 1: Call get_supplier_schema_guide()
Chatbot internally calls the schema guide to understand supplier fields.

### Step 2: Ask for ALL Fields (Required + Optional)

**Chatbot Response to User:**
```
To create a supplier, please provide the following information:

**REQUIRED Fields** (must provide):
- name: [already provided: Tech Supplies Ltd] ✓
- supplier_type: [already provided: company] ✓
- gst_category: [already provided: registered] ✓

**OPTIONAL Fields** (provide only if you have the information):
- gstin_uin: GST/UIN number (max 30 chars)
- contact_first_name: Contact person first name
- contact_last_name: Contact person last name
- contact_email: Email address
- contact_mobile: Mobile number
- address_line1: Street address line 1
- address_line2: Street address line 2
- city: City name
- state: State/province
- postal_code: Postal/ZIP code
- preferred_billing: Is this a preferred billing address?
- preferred_shipping: Is this a preferred shipping address?
- country: Country (defaults to Pakistan if not specified)

You can skip any optional fields you don't have. Just tell me if you'd like
to add any of the optional information.
```

### Step 3: User Decides on Optional Fields

**User Response:**
```
"No, I don't want to add any optional fields right now. Just create it 
with the required fields I provided."
```

### Step 4: Validate Required Fields

**Internally:**
```python
validate_required_fields_tool(
    table="supplier",
    provided_data={
        "name": "Tech Supplies Ltd",
        "supplier_type": "company",
        "gst_category": "registered"
    }
)

Response: {"is_valid": true}
```

### Step 5: Create with ONLY User-Provided Fields

**Internally:**
```python
create_record_tool(
    table="supplier",
    data={
        "name": "Tech Supplies Ltd",
        "supplier_type": "company",
        "gst_category": "registered"
    }
)

# ❌ DO NOT include these (user didn't provide):
# - gstin_uin: None
# - contact_first_name: None
# - contact_last_name: None
# - contact_email: None
# - contact_mobile: None
# - address_line1: None
# - address_line2: None
# - city: None
# - state: None
# - postal_code: None
# - preferred_billing: False/None
# - preferred_shipping: False/None
# - country: "Pakistan" (DON'T auto-fill default!)
```

### Step 6: Confirm to User

**Chatbot Response:**
```
Supplier "Tech Supplies Ltd" has been successfully created!

Here are the details:
- ID: [auto-generated]
- Name: Tech Supplies Ltd
- Supplier Type: company
- GST Category: registered
- Created By: [current user]
- Created At: [timestamp]

If you'd like to add more information (email, address, GST number, etc.) 
later, just let me know and I can update the supplier.
```

---

## What the Test Validates

✅ **Chatbot asks for ALL fields** (required + optional)
✅ **User can skip optional fields** without penalty
✅ **Validation passes** with only required fields
✅ **Create only includes** fields user explicitly provided
✅ **No auto-populated optional fields** in the database
✅ **No unwanted defaults** added for optional fields

---

## Contrast: What WOULD Be Wrong

### ❌ WRONG: Auto-populating optional fields
```python
create_record_tool(
    table="supplier",
    data={
        "name": "Tech Supplies Ltd",
        "supplier_type": "company",
        "gst_category": "registered",
        "country": "Pakistan",  # ← Auto-filled! (user didn't say this)
        "preferred_billing": False,  # ← Auto-filled! (user didn't say this)
        "preferred_shipping": False,  # ← Auto-filled! (user didn't say this)
    }
)
```
**Problem**: User didn't provide country, billing, or shipping preferences, but chatbot added them anyway!

### ❌ WRONG: Only asking for required fields
```
Chatbot: "Please provide gstin_uin, contact_first_name, contact_last_name"
User: "I don't have that information"
Chatbot: "OK, creating supplier without them"
```
**Problem**: Chatbot never even offered to ask for optional fields! What if user HAD the email or address?

### ✅ CORRECT: This Test Case
```
Chatbot: Shows BOTH required and optional sections
User: "I only have the required fields"
Chatbot: Creates with ONLY required fields, nothing more
```
**Benefit**: User has full control, nothing is assumed or auto-filled

---

## How to Run This Test

1. Open the chatbot
2. Type the user prompt above
3. Verify chatbot asks for ALL fields (required + optional)
4. Provide: name, supplier_type, gst_category (but skip optional fields)
5. Verify chatbot confirms creation
6. Check database: Supplier should have ONLY 3 fields, no auto-populated optional fields

---

## Variant Tests

### Variant 1: User Provides Some Optional Fields
```
User: "Create supplier Tech Supplies Ltd, company type, registered GST,
email is tech@supplies.com, city is New York"

Expected Chatbot Behavior:
- Ask for all fields (required + optional)
- User specifies: name, supplier_type, gst_category, contact_email, city
- Create with EXACTLY these 5 fields
- Do NOT add: address, phone, postal_code, state, country, etc.
```

### Variant 2: User Provides All Fields at Once
```
User: "Create supplier Tech Supplies Ltd, company type, registered GST,
email is tech@supplies.com, city New York, state NY, phone 555-1234,
address 123 Tech Lane, country USA"

Expected Chatbot Behavior:
- Still ask for all fields (let user confirm or add more)
- Validate all required fields present
- Create with ALL provided fields (11 fields total)
```

### Variant 3: User Changes Mind About Optional Fields Later
```
User 1: "Create supplier ABC"
Chatbot: [asks for required + optional]
User: "Just the required fields"
Chatbot: [creates with 3 fields]

User 2 (later): "Can you add email to that supplier?"
Chatbot: "Yes, I can update it. What's the email?"
User: "abc@company.com"
Chatbot: [updates supplier to include email]
```

---

## Success Criteria

The new optional fields workflow is **SUCCESSFUL** if:

1. ✅ Chatbot ALWAYS asks for optional fields upfront
2. ✅ User can skip optional fields without pushback
3. ✅ Chatbot creates with ONLY specified fields
4. ✅ No auto-populated defaults in database
5. ✅ No auto-inherited FK values from relationships
6. ✅ User has full control over what gets saved
7. ✅ Data integrity is maintained

---

## Notes for Tester

- **Don't test with JournalEntry yet** - use Supplier/Customer first
- **Check database directly** after creation to verify no unwanted fields
- **Test variant 1 and 2** to ensure workflow works with partial and complete data
- **Report any auto-populated fields** - those are bugs!

For detailed examples, see: `OPTIONAL_FIELDS_HANDLING_GUIDE.md`
