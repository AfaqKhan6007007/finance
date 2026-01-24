"""
Domain-Specific Prompt Tools for MCP Server
Provides targeted guidance when LLM needs context about specific domains
"""

from mcp import FastMCP


def register_prompt_tools(mcp: FastMCP):
    """Register all domain-specific prompt guide tools"""
    
    @mcp.tool()
    def get_invoice_query_guide() -> str:
        """
        Get guidance for querying and understanding invoices.
        Call this when user asks about invoices, bills, or payments.
        """
        return """## Invoice Query Guide

**Key Fields:**
- invoice_number: Unique identifier (e.g., "INV-2025-001")
- customer: Related customer object (use customer_id for filtering)
- supplier: Related supplier object (use supplier_id for filtering)  
- invoice_date: Date invoice was issued
- due_date: Payment due date
- total_amount: Total invoice value
- status: "draft", "sent", "paid", "overdue", "cancelled"
- invoice_type: "sales" (to customers) or "purchase" (from suppliers)
- currency: Invoice currency (default: INR)
- tax_amount: Total tax on invoice
- company: Related company object

**Common Filters:**
```python
{"status": "paid"}  # Paid invoices only
{"total_amount__gte": 5000}  # Amount >= 5000
{"invoice_date__range": ["2025-01-01", "2025-12-31"]}  # Date range
{"invoice_type": "sales"}  # Sales invoices only
{"customer_id": 3}  # Specific customer
{"status__in": ["sent", "overdue"]}  # Multiple statuses
```

**Available Tools:**
- list_invoices_tool(filters, page, page_size) - Paginated list
- get_invoice_tool(invoice_id) - Single invoice details
- search_invoices_tool(query) - Search by invoice_number/notes
- get_invoice_stats_tool(filters) - Aggregated statistics

**Query Examples:**
- "Show unpaid invoices" → filters={"status__in": ["sent", "overdue"]}
- "Invoices over 10000" → filters={"total_amount__gt": 10000}
- "Sales invoices from January" → filters={"invoice_type": "sales", "invoice_date__range": ["2025-01-01", "2025-01-31"]}

**Business Logic:**
- Sales invoices = Revenue (customer pays us)
- Purchase invoices = Expense (we pay supplier)
- Overdue = due_date passed and status != "paid"
- Use get_invoice_stats_tool for totals/averages"""

    @mcp.tool()
    def get_account_query_guide() -> str:
        """
        Get guidance for querying chart of accounts.
        Call this when user asks about accounts, ledgers, or account structure.
        """
        return """## Account Query Guide

**Key Fields:**
- account_code: Unique code (e.g., "1000", "2100")
- account_name: Descriptive name (e.g., "Cash", "Accounts Payable")
- account_type: "asset", "liability", "equity", "revenue", "expense"
- parent_account: Hierarchical parent (null for top-level)
- is_active: Whether account is currently in use
- opening_balance: Starting balance
- current_balance: Current balance (calculated)
- company: Related company object

**Account Type Rules:**
- **Asset**: Debit increases, Credit decreases (normal debit balance)
- **Liability**: Credit increases, Debit decreases (normal credit balance)
- **Equity**: Credit increases, Debit decreases (normal credit balance)
- **Revenue**: Credit increases, Debit decreases (normal credit balance)
- **Expense**: Debit increases, Credit decreases (normal debit balance)

**Common Filters:**
```python
{"account_type": "asset"}  # All asset accounts
{"is_active": True}  # Active accounts only
{"parent_account__isnull": True}  # Top-level accounts
{"current_balance__gt": 0}  # Accounts with positive balance
{"company_id": 5}  # Specific company
```

**Available Tools:**
- list_accounts_tool(filters, page, page_size) - Paginated list
- get_account_tool(account_id) - Single account details
- search_accounts_tool(query) - Search by code/name
- get_account_balance_tool(account_id, start_date, end_date) - Balance calc
- get_account_hierarchy_tool(company_id) - Tree structure

**Query Examples:**
- "Show all asset accounts" → filters={"account_type": "asset"}
- "Revenue accounts" → filters={"account_type": "revenue", "is_active": True}
- "Account hierarchy" → get_account_hierarchy_tool(company_id)

**Business Logic:**
- Chart of Accounts = Master list of all accounts
- Hierarchy supports sub-accounts (parent_account)
- Use get_account_hierarchy_tool for tree view"""

    @mcp.tool()
    def get_company_query_guide() -> str:
        """
        Get guidance for querying companies.
        Call this when user asks about companies, organizations, or entities.
        """
        return """## Company Query Guide

**Key Fields:**
- name: Company name
- company_code: Unique identifier code
- country: Operating country
- currency: Default currency (e.g., "INR", "USD")
- fiscal_year_start: Fiscal year start date
- fiscal_year_end: Fiscal year end date
- is_active: Whether company is active
- created_at: Registration date

**Common Filters:**
```python
{"country": "India"}  # Companies in India
{"is_active": True}  # Active companies
{"currency": "INR"}  # INR-based companies
{"name__icontains": "tech"}  # Name contains "tech"
```

**Available Tools:**
- list_companies_tool(filters, page, page_size) - Paginated list
- get_company_tool(company_id) - Single company details
- search_companies_tool(query) - Search by name/code
- get_company_accounts_tool(company_id) - Company's chart of accounts
- get_company_stats_tool(company_id) - Statistics

**Query Examples:**
- "List all companies" → list_companies_tool()
- "Company 5 details" → get_company_tool(5)
- "Companies in USA" → filters={"country": "USA"}

**Business Logic:**
- Multi-company support (each company has own accounts)
- Fiscal year defines reporting period
- Use get_company_accounts_tool to see company's accounts"""

    @mcp.tool()
    def get_supplier_query_guide() -> str:
        """
        Get guidance for querying suppliers/vendors.
        Call this when user asks about suppliers, vendors, or purchase sources.
        """
        return """## Supplier Query Guide

**Key Fields:**
- supplier_name: Business name
- supplier_code: Unique identifier
- contact_person: Primary contact name
- email: Contact email
- phone: Contact phone
- country: Supplier country
- gst_category: "registered", "unregistered", "overseas"
- gstin: GST identification number (India)
- pan: PAN number (India tax ID)
- outstanding_balance: Amount owed to supplier
- company: Related company object

**Common Filters:**
```python
{"country": "India"}  # Indian suppliers
{"gst_category": "registered"}  # GST-registered
{"outstanding_balance__gt": 0}  # Suppliers we owe money
{"supplier_name__icontains": "tech"}  # Name contains "tech"
```

**Available Tools:**
- list_suppliers_tool(filters, page, page_size) - Paginated list
- get_supplier_tool(supplier_id) - Single supplier details
- search_suppliers_tool(query) - Search by name/code/email

**Query Examples:**
- "List all suppliers" → list_suppliers_tool()
- "Suppliers in India" → filters={"country": "India"}
- "Suppliers with outstanding balance" → filters={"outstanding_balance__gt": 0}
- "Search for Tech suppliers" → search_suppliers_tool("tech")

**Business Logic:**
- Suppliers = Vendors we purchase from
- Outstanding balance = Amount we owe them
- GST category affects tax calculation (India)"""

    @mcp.tool()
    def get_customer_query_guide() -> str:
        """
        Get guidance for querying customers.
        Call this when user asks about customers, clients, or sales contacts.
        """
        return """## Customer Query Guide

**Key Fields:**
- customer_name: Business/individual name
- customer_code: Unique identifier
- contact_person: Primary contact name
- email: Contact email
- phone: Contact phone
- country: Customer country
- customer_type: "individual" or "business"
- credit_limit: Maximum credit allowed
- outstanding_balance: Amount customer owes us
- company: Related company object

**Common Filters:**
```python
{"country": "India"}  # Indian customers
{"customer_type": "business"}  # Business customers only
{"outstanding_balance__gt": 0}  # Customers owing money
{"credit_limit__gte": 50000}  # High credit limit customers
```

**Available Tools:**
- list_customers_tool(filters, page, page_size) - Paginated list
- get_customer_tool(customer_id) - Single customer details
- search_customers_tool(query) - Search by name/code/email

**Query Examples:**
- "List all customers" → list_customers_tool()
- "Business customers" → filters={"customer_type": "business"}
- "Customers with dues" → filters={"outstanding_balance__gt": 0}
- "Search Tech Innovations" → search_customers_tool("Tech Innovations")

**Business Logic:**
- Customers = Clients who buy from us
- Outstanding balance = Amount they owe us (receivables)
- Credit limit = Max allowed credit"""

    @mcp.tool()
    def get_journal_query_guide() -> str:
        """
        Get guidance for querying journal entries.
        Call this when user asks about journal entries, postings, or ledger entries.
        """
        return """## Journal Entry Query Guide

**Key Fields:**
- entry_number: Unique identifier (e.g., "JE-2025-001")
- entry_date: Date of entry
- entry_type: "manual", "automatic", "opening", "adjustment", "closing"
- description: Entry purpose/notes
- status: "draft", "posted", "cancelled"
- total_debit: Sum of debit amounts
- total_credit: Sum of credit amounts
- company: Related company object
- line_items: Array of account postings (account, debit, credit)

**Accounting Rules:**
- Debits must equal credits (balanced entry)
- Each line item has account_id, debit_amount, credit_amount
- Status "posted" = entry is finalized and affects balances

**Common Filters:**
```python
{"status": "posted"}  # Posted entries only
{"entry_type": "manual"}  # Manual entries
{"entry_date__range": ["2025-01-01", "2025-12-31"]}  # Date range
{"total_debit__gte": 10000}  # Large entries
```

**Available Tools:**
- list_journal_entries_tool(filters, page, page_size) - Paginated list
- get_journal_entry_tool(entry_id) - Single entry with line items
- search_journal_entries_tool(query) - Search by number/description
- get_journal_stats_tool(filters) - Aggregated statistics

**Query Examples:**
- "Posted journal entries" → filters={"status": "posted"}
- "Manual adjustments" → filters={"entry_type": "manual"}
- "January entries" → filters={"entry_date__range": ["2025-01-01", "2025-01-31"]}

**Business Logic:**
- Journal Entry = Basic unit of double-entry bookkeeping
- Every transaction affects at least 2 accounts
- Debits = Credits (accounting equation balance)"""

    @mcp.tool()
    def get_budget_query_guide() -> str:
        """
        Get guidance for querying budgets.
        Call this when user asks about budgets, planned spending, or financial planning.
        """
        return """## Budget Query Guide

**Key Fields:**
- account: Related account object (account_id for filtering)
- fiscal_year: Budget year (e.g., "2025-2026")
- period: "monthly", "quarterly", "annual"
- budgeted_amount: Planned amount
- actual_amount: Actual spending (calculated)
- variance: Budget vs Actual difference
- variance_percentage: Variance as percentage
- cost_center: Optional cost center allocation
- company: Related company object

**Common Filters:**
```python
{"fiscal_year": "2025-2026"}  # Specific fiscal year
{"period": "annual"}  # Annual budgets
{"variance__gt": 0}  # Over-budget items
{"account__account_type": "expense"}  # Expense budgets
```

**Available Tools:**
- list_budgets_tool(filters, page, page_size) - Paginated list
- get_budget_tool(budget_id) - Single budget details
- search_budgets_tool(query) - Search by fiscal_year/notes

**Query Examples:**
- "Annual budgets for 2025" → filters={"fiscal_year": "2025-2026", "period": "annual"}
- "Over-budget accounts" → filters={"variance__gt": 0}
- "Expense budgets" → filters={"account__account_type": "expense"}

**Business Logic:**
- Budget = Financial plan for account
- Variance = Actual - Budgeted (positive = over-budget)
- Typically set for expense accounts
- Can be allocated to cost centers"""

    @mcp.tool()
    def get_tax_query_guide() -> str:
        """
        Get guidance for querying tax rules and categories.
        Call this when user asks about taxes, GST, TDS, or tax calculations.
        """
        return """## Tax Query Guide

**Tax Categories (India):**
- CGST: Central GST
- SGST: State GST  
- IGST: Integrated GST (interstate)
- CESS: Additional cess
- TDS: Tax Deducted at Source
- TCS: Tax Collected at Source

**Tax Rules:**
- Rule defines tax calculation logic
- Links tax category to accounts
- Specifies rate, applicability, exemptions

**Common Filters:**
```python
{"is_active": True}  # Active tax rules
{"tax_category__category_code": "CGST"}  # CGST rules
{"rate__gte": 18}  # High tax rates
```

**Available Tools:**
- list_tax_rules_tool(filters, page, page_size) - Paginated list
- get_tax_rule_tool(rule_id) - Single rule details
- search_tax_rules_tool(query) - Search by name/description
- list_tax_categories_tool() - All tax categories
- list_tax_templates_tool() - Tax item templates

**Query Examples:**
- "Active tax rules" → filters={"is_active": True}
- "GST rules" → filters={"tax_category__category_code__icontains": "GST"}
- "All tax categories" → list_tax_categories_tool()

**Business Logic:**
- Tax rules define how taxes are calculated
- Categories = Types of taxes (CGST, SGST, etc)
- Templates = Reusable tax configurations
- India GST: CGST + SGST = Total GST (intrastate)
- India GST: IGST = Total GST (interstate)"""

    @mcp.tool()
    def get_cost_center_query_guide() -> str:
        """
        Get guidance for querying cost centers.
        Call this when user asks about cost centers, departments, or cost allocation.
        """
        return """## Cost Center Query Guide

**Key Fields:**
- cost_center_name: Department/division name
- cost_center_code: Unique identifier
- is_active: Whether currently in use
- parent_cost_center: Hierarchical parent (null for top-level)
- company: Related company object

**Common Filters:**
```python
{"is_active": True}  # Active cost centers
{"parent_cost_center__isnull": True}  # Top-level centers
{"company_id": 5}  # Specific company
```

**Available Tools:**
- list_cost_centers_tool(filters, page, page_size) - Paginated list
- get_cost_center_tool(cost_center_id) - Single cost center details
- search_cost_centers_tool(query) - Search by name/code

**Query Examples:**
- "All cost centers" → list_cost_centers_tool()
- "Active cost centers" → filters={"is_active": True}
- "Top-level departments" → filters={"parent_cost_center__isnull": True}

**Business Logic:**
- Cost Center = Department/division for expense tracking
- Hierarchical structure (parent/child)
- Used in budgets and journal entries for allocation
- Helps analyze spending by department"""

    @mcp.tool()
    def get_general_query_patterns() -> str:
        """
        Get general query patterns and filter syntax.
        Call this when you need help constructing filters or understanding query patterns.
        """
        return """## General Query Patterns

**Filter Operators:**
```python
# Exact match
{"field": "value"}

# Comparison
{"field__gt": 100}      # Greater than
{"field__gte": 100}     # Greater than or equal
{"field__lt": 100}      # Less than
{"field__lte": 100}     # Less than or equal

# Contains (case-insensitive)
{"field__icontains": "text"}

# In list
{"field__in": ["value1", "value2"]}

# Date range
{"date_field__range": ["2025-01-01", "2025-12-31"]}

# Null checks
{"field__isnull": True}   # IS NULL
{"field__isnull": False}  # IS NOT NULL

# Related field (foreign key)
{"related_model__field": "value"}
{"customer__country": "India"}
```

**Pagination:**
- page: Page number (default: 1)
- page_size: Items per page (default: 20, max: 100)

**Tool Naming Pattern:**
- list_* → Get paginated list with filters
- get_* → Get single item by ID
- search_* → Full-text search by query string
- get_*_stats → Get aggregated statistics

**Best Practices:**
1. Use specific filters to reduce result set
2. Start with stats tools for overview
3. Use search for fuzzy matching
4. Use list with filters for exact matching
5. Get schema when you need field details

**Error Handling:**
- Empty results = No matching records (not an error)
- Invalid filter = Check field name and operator
- Invalid ID = Record doesn't exist"""
