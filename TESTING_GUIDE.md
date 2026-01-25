# How to Use database_ground_truth.md for Testing

## Overview
The `database_ground_truth.md` file contains **all 107 records** from your SQLite database, formatted in Markdown for easy reference.

## File Statistics
- **Total Records:** 107
- **Total Lines:** 1,933
- **File Size:** 68 KB
- **Last Generated:** Check the timestamp at the top of the file

## Structure

### Table of Contents
Jump to any section using the links in the Table of Contents at the top.

### Each Record Shows
- **All field names** (both verbose name and database column name)
- **All field values** (with special formatting):
  - Empty values: `_empty_`
  - Boolean: ✅ Yes / ❌ No
  - Dates: `YYYY-MM-DD HH:MM:SS`
  - Foreign Keys: `ID (Related Object Name)`

### Summary Statistics
At the bottom, see a table with record counts for all models.

## Testing Workflow

### 1. Test Simple Queries
**Query:** "List all companies"
**Ground Truth:** Check section "Companies" - should see 5 records (IDs: 22, 23, 24, 25, 26)

**Query:** "Show me company with ID 22"
**Ground Truth:** 
```
Record: TechCorp Solutions USA
- ID: 22
- Abbreviation: TCS-USA
- Country: USA
- Tax ID: TAX-USA-002
- Parent Company: Global Corp International
... (all 29 fields shown)
```

### 2. Test Filtered Queries
**Query:** "Find all invoices with status paid"
**Ground Truth:** Check "Invoices" section, count records where Status = "paid"

**Query:** "Show me all companies in USA"
**Ground Truth:** Check "Companies" section, filter by Country = "USA"

### 3. Test Date Range Queries
**Query:** "Find invoices from January 2024"
**Ground Truth:** Check "Invoices" section, filter by Date between 2024-01-01 and 2024-01-31

### 4. Test Relationship Queries
**Query:** "Show me all accounts for TechCorp Solutions USA"
**Ground Truth:** Check "Accounts" section, filter by Company field containing "22 (TechCorp Solutions USA)"

### 5. Test Aggregation Queries
**Query:** "How many suppliers do we have?"
**Ground Truth:** Check Summary Statistics table - Suppliers = 5

**Query:** "Count total journal entries"
**Ground Truth:** Check Summary Statistics table - Journal Entries = 20

## Sample Test Cases

### Test Case 1: Complete Record Details
```
Query: "Show me all data for TechCorp Solutions USA"
Expected: ALL 29 fields from Companies Record with ID 22
Verify: Every field listed in ground truth should appear in chatbot response
```

### Test Case 2: Multiple Filters
```
Query: "Find paid invoices for TechCorp Solutions USA in January 2024"
Expected: Filter Invoices where:
  - Status = "paid"
  - Company = "22 (TechCorp Solutions USA)"
  - Date between 2024-01-01 and 2024-01-31
Verify: Count and IDs match ground truth
```

### Test Case 3: Related Records
```
Query: "List all budgets for Marketing department"
Expected: Check "Budgets" section, filter by Cost Center containing "Marketing"
Verify: Budget names, amounts, and periods match ground truth
```

### Test Case 4: Empty Fields
```
Query: "Show companies without parent company"
Expected: Companies where Parent Company = "_empty_"
Verify: Company names match those with empty parent_company field
```

## Regenerating Ground Truth

When you add/modify database records:

```bash
cd /d/Machine\ Learning/JFF\ JOB/finance
source venv/Scripts/activate
python export_database_to_markdown.py
```

This will regenerate `database_ground_truth.md` with the latest data.

## Quick Reference: Record Counts

| Category | Model | Count |
|----------|-------|-------|
| Core Business | Companies | 5 |
| | Accounts | 24 |
| | Invoices | 10 |
| | Journal Entries | 20 |
| | Suppliers | 5 |
| | Customers | 4 |
| Planning | Budgets | 3 |
| | Cost Centers | 12 |
| | Cost Center Allocations | 3 |
| | Accounting Dimensions | 3 |
| Tax | Tax Item Templates | 4 |
| | Tax Categories | 4 |
| | Tax Rules | 3 |
| | Tax Withholding Categories | 4 |
| Users | User Profiles | 3 |

**Total:** 107 records

## Tips for Effective Testing

1. **Always check field count**: If ground truth shows 29 fields, chatbot should show 29 fields (when asked for "all data")
2. **Verify exact values**: Not just field names, but actual values should match
3. **Check empty fields**: Make sure chatbot handles empty/null values correctly
4. **Test foreign keys**: Verify chatbot shows both ID and related object name
5. **Date formatting**: Ensure dates are formatted consistently
6. **Boolean display**: Check if true/false are displayed clearly

## Common Ground Truth Lookups

### Companies
- **TechCorp Solutions USA** (ID: 22) - Has parent company, subsidiary type
- **Global Corp International** (ID: 23) - Parent company, has subsidiaries
- **SmartTech Industries** (ID: 26) - Regular company, no parent
- **FinTech Services LLC** (ID: 24) - Regular company
- **Retail Solutions Inc** (ID: 25) - Regular company

### Key Relationships
- TechCorp Solutions USA → Parent: Global Corp International
- TechCorp Solutions USA → 8 accounts, 1 budget, 4 cost centers, 6 journal entries

Use these as test anchors when verifying chatbot responses!
