# MCP Server Dynamic Filtering Guide

This guide explains how the LLM can use dynamic filters in the Finance MCP Server tools.

## How It Works

Instead of creating separate tools for every possible query, the LLM provides filters as dictionary parameters:

```python
# OLD WAY (would need 100s of tools):
get_asset_accounts_with_balance_over_10000()
get_active_liability_accounts_for_company_5()
get_accounts_created_in_2025()

# NEW WAY (one tool, infinite queries):
list_accounts_tool(filters={"account_type": "Asset", "balance__gte": 10000})
list_accounts_tool(filters={"account_type": "Liability", "is_active": True, "company__id": 5})
list_accounts_tool(filters={"created_at__range": ["2025-01-01", "2025-12-31"]})
```

## Filter Operators

All Django ORM lookup operators are supported:

### Exact Match
```python
{"country": "USA"}
{"account_type": "Asset"}
{"is_active": True}
```

### Contains (Case-Insensitive)
```python
{"name__icontains": "tech"}  # Matches "TechCorp", "FinTech Solutions"
{"account_number__icontains": "1000"}  # Matches "1000", "10001", "21000"
```

### Comparison Operators
```python
{"balance__gt": 1000}      # Greater than
{"balance__gte": 1000}     # Greater than or equal
{"balance__lt": 50000}     # Less than
{"balance__lte": 50000}    # Less than or equal
```

### In List
```python
{"account_type__in": ["Asset", "Liability"]}
{"status__in": ["pending", "approved"]}
```

### Date Range
```python
{"created_at__range": ["2025-01-01", "2025-12-31"]}
{"invoice_date__range": ["2025-06-01", "2025-06-30"]}
```

### Null Check
```python
{"parent_account__isnull": True}   # Top-level accounts only
{"email__isnull": False}           # Must have email
```

### Related Field Lookups
```python
{"company__name": "ABC Corp"}           # Filter by related company name
{"company__country": "USA"}             # Filter by company's country
{"parent_account__id": 10}              # Filter by parent account
{"supplier__gst_category": "Regular"}   # Filter by supplier's GST category
```

### Multiple Filters (AND logic)
```python
{
    "account_type": "Asset",
    "balance__gte": 10000,
    "is_active": True,
    "company__id": 5
}
# All conditions must be true
```

## Real-World Examples

### Example 1: Find High-Value Asset Accounts
**User Query**: "Show me all asset accounts with a balance over $50,000"

**LLM Response**:
```python
list_accounts_tool(
    filters={
        "account_type": "Asset",
        "balance__gte": 50000
    }
)
```

### Example 2: Find Active Companies in USA
**User Query**: "List all active companies in the USA"

**LLM Response**:
```python
list_companies_tool(
    filters={
        "country": "USA",
        "is_active": True
    }
)
```

### Example 3: Search Tech Companies in USA
**User Query**: "Find technology companies in the United States"

**LLM Response**:
```python
search_companies_tool(
    query="tech",
    filters={
        "country": "USA"
    }
)
```

### Example 4: Find Expense Accounts for Specific Company
**User Query**: "Show expense accounts for company ID 3"

**LLM Response**:
```python
get_accounts_by_type_tool(
    account_type="expense",
    filters={
        "company__id": 3
    }
)
```

### Example 5: Find Accounts Without Parent
**User Query**: "List all top-level accounts (no parent)"

**LLM Response**:
```python
list_accounts_tool(
    filters={
        "parent_account__isnull": True
    }
)
```

### Example 6: Complex Multi-Criteria Query
**User Query**: "Find active asset accounts with balance between $10,000 and $100,000 for companies in USA"

**LLM Response**:
```python
list_accounts_tool(
    filters={
        "account_type": "Asset",
        "is_active": True,
        "balance__gte": 10000,
        "balance__lte": 100000,
        "company__country": "USA"
    }
)
```

### Example 7: Date-Based Filtering
**User Query**: "Show accounts created in Q1 2025"

**LLM Response**:
```python
list_accounts_tool(
    filters={
        "created_at__range": ["2025-01-01", "2025-03-31"]
    }
)
```

### Example 8: Search with Filters
**User Query**: "Find cash accounts that are active"

**LLM Response**:
```python
search_accounts_tool(
    query="cash",
    filters={
        "is_active": True
    }
)
```

## Field Names Reference

### Company Model Fields
- `id`, `name`, `abbreviation`, `country`
- `default_currency`, `fiscal_year_start`, `fiscal_year_end`
- `is_active`, `created_at`, `updated_at`

### Account Model Fields
- `id`, `name`, `account_number`, `account_type`
- `balance`, `is_group`, `is_active`
- `company`, `parent_account` (related fields)
- `created_at`, `updated_at`

### Invoice Model Fields (for future implementation)
- `id`, `invoice_number`, `invoice_date`, `due_date`
- `amount`, `status`, `currency`
- `supplier`, `customer`, `company` (related fields)
- `created_at`, `updated_at`

## Type Conversions

The filter parser automatically handles:

### Decimal Conversion
Fields like `balance`, `amount`, `total`, `price` are automatically converted to Decimal:
```python
{"balance__gte": 1000}  # String "1000" → Decimal(1000)
{"amount__lt": 5000.50}  # Float 5000.50 → Decimal("5000.50")
```

### Date Conversion
Date strings are converted to datetime objects:
```python
{"created_at__range": ["2025-01-01", "2025-12-31"]}
# Strings → datetime objects
```

### Boolean Values
```python
{"is_active": True}   # Boolean
{"is_group": False}   # Boolean
```

## Best Practices for LLMs

### 1. Use Specific Tools When Possible
```python
# Good - specific tool
get_company_tool(company_id=5)

# Avoid - using filters when ID is known
list_companies_tool(filters={"id": 5})
```

### 2. Combine Filters Instead of Sequential Calls
```python
# Good - one query
list_accounts_tool(filters={"account_type": "Asset", "balance__gte": 10000})

# Avoid - two queries
# 1. list_accounts_tool(filters={"account_type": "Asset"})
# 2. Then filter results manually
```

### 3. Use Pagination for Large Results
```python
list_accounts_tool(
    filters={"account_type": "Asset"},
    page=1,
    page_size=20
)
```

### 4. Use Related Field Lookups
```python
# Good - filter by related field
list_accounts_tool(filters={"company__name": "ABC Corp"})

# Avoid - two queries (get company ID, then query accounts)
```

### 5. Be Specific with Search Terms
```python
# Good - search + filters
search_accounts_tool(query="cash", filters={"account_type": "Asset"})

# Less efficient - broad search, no filters
search_accounts_tool(query="a")
```

## Error Handling

Invalid filters will return error responses:

```python
# Invalid account type
get_accounts_by_type_tool(account_type="InvalidType")
# Returns: {"success": False, "error": "Invalid account type..."}

# Invalid field name
list_accounts_tool(filters={"invalid_field": "value"})
# Returns: Django field error
```

## Performance Considerations

### Efficient Queries
```python
# Good - specific filters
{"company__id": 5, "account_type": "Asset"}

# Less efficient - broad filters
{"name__icontains": "a"}  # Matches too many results
```

### Use Pagination
Always use pagination for list operations:
```python
list_accounts_tool(page=1, page_size=20)  # Default
list_accounts_tool(page=1, page_size=100)  # Max
```

## Future Extensions

These filters will be available for all upcoming tools:
- Invoice tools (filter by status, date, amount, supplier/customer)
- Journal entry tools (filter by account, date, amount)
- Supplier tools (filter by GST category, country, active status)
- Customer tools (filter by country, credit limit, active status)
- Budget tools (filter by fiscal year, department, status)
- Cost center tools (filter by company, active status)
- Tax tools (filter by category, rate, jurisdiction)

## Implementation Details

The `parse_filters()` utility function in `helpers.py`:
1. Accepts dictionary of filters
2. Converts field names and values to Django ORM format
3. Handles type conversions (Decimal, datetime)
4. Builds Django Q objects for complex queries
5. Returns filtered QuerySet

This allows the LLM to construct sophisticated database queries through simple dictionary parameters, making the MCP server extremely flexible without needing hundreds of specialized tools.
