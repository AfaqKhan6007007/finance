"""
Finance Management System MCP Server
Main server file - registers all tools and resources
"""
from fastmcp import FastMCP
from pathlib import Path

# Import config first to initialize Django
from mcp_server import config

# Import all tools
from mcp_server.tools.company_tools import (
    list_companies,
    get_company,
    search_companies,
    get_company_accounts,
    get_company_stats
)
from mcp_server.tools.account_tools import (
    list_accounts,
    get_account,
    search_accounts,
    get_account_balance,
    get_account_hierarchy
)
from mcp_server.tools.invoice_tools import (
    list_invoices,
    get_invoice,
    search_invoices,
    get_invoice_stats
)
from mcp_server.tools.journal_tools import (
    list_journal_entries,
    get_journal_entry,
    search_journal_entries,
    get_journal_stats
)
from mcp_server.tools.supplier_tools import (
    list_suppliers,
    get_supplier,
    search_suppliers
)
from mcp_server.tools.customer_tools import (
    list_customers,
    get_customer,
    search_customers
)
from mcp_server.tools.budget_tools import (
    list_budgets,
    get_budget,
    search_budgets
)
from mcp_server.tools.cost_center_tools import (
    list_cost_centers,
    get_cost_center,
    search_cost_centers
)
from mcp_server.tools.tax_tools import (
    list_tax_rules,
    get_tax_rule,
    search_tax_rules,
    list_tax_categories,
    list_tax_templates
)

# Create FastMCP instance
mcp = FastMCP(
    name=config.SERVER_NAME,
    version=config.SERVER_VERSION
)


# ============================================
# RESOURCES - Schema Documentation
# ============================================

@mcp.resource("finance://schema/database")
def get_database_schema() -> str:
    """
    Returns the complete database schema documentation
    This helps LLMs understand the database structure
    """
    schema_path = config.SCHEMA_DOC_PATH
    if schema_path.exists():
        return schema_path.read_text(encoding='utf-8')
    return "Schema documentation not found"


@mcp.prompt()
def company_query_examples() -> str:
    """Examples of how to query company data"""
    return """
# Company Query Examples

## List all companies (paginated):
- Tool: list_companies_tool(page=1, page_size=20)

## List companies with filters:
- Tool: list_companies_tool(filters={"country": "USA"}, page=1, page_size=20)
- Tool: list_companies_tool(filters={"is_active": True}, page=1, page_size=20)
- Tool: list_companies_tool(filters={"name__icontains": "tech"}, page=1, page_size=20)

## Get specific company details:
- Tool: get_company_tool(company_id=1)

## Search companies by name/country:
- Tool: search_companies_tool(query="ABC", page=1, page_size=20)

## Search with additional filters:
- Tool: search_companies_tool(query="tech", filters={"country": "USA", "is_active": True})

## Get company's chart of accounts:
- Tool: get_company_accounts_tool(company_id=1, page=1, page_size=20)

## Get company statistics:
- Tool: get_company_stats_tool(company_id=1)
  Returns: account count, supplier count, customer count, invoice stats, financial summary

## Filter Operators Available:
- Exact match: {"field": "value"}
- Contains: {"field__icontains": "text"}
- Greater than: {"field__gt": value}
- Greater/equal: {"field__gte": value}
- Less than: {"field__lt": value}
- Less/equal: {"field__lte": value}
- In list: {"field__in": [val1, val2]}
- Date range: {"field__range": ["2024-01-01", "2024-12-31"]}
- Is null: {"field__isnull": True}
- Related field: {"company__name": "ABC Corp"}
"""


@mcp.prompt()
def account_query_examples() -> str:
    """Examples of how to query account data"""
    return """
# Account Query Examples

## List all accounts:
- Tool: list_accounts_tool(page=1, page_size=20)

## List accounts with filters:
- Tool: list_accounts_tool(filters={"account_type": "Asset"})
- Tool: list_accounts_tool(filters={"balance__gte": 10000})
- Tool: list_accounts_tool(filters={"company__id": 5})
- Tool: list_accounts_tool(filters={"is_group": False, "is_active": True})

## Get specific account:
- Tool: get_account_tool(account_id=1)

## Search accounts:
- Tool: search_accounts_tool(query="Cash", page=1, page_size=20)

## Search with filters:
- Tool: search_accounts_tool(query="cash", filters={"account_type": "Asset", "balance__gte": 5000})

## Calculate account balance:
- Tool: get_account_balance_tool(account_id=1)
  Returns: total debits, total credits, balance, entry count

## Get account hierarchy (parent/children):
- Tool: get_account_hierarchy_tool(account_id=1)

## Complex Filter Examples:
- Asset accounts with balance over $10,000: 
  list_accounts_tool(filters={"account_type": "Asset", "balance__gte": 10000})
  
- Active liability accounts for specific company:
  list_accounts_tool(filters={"account_type": "Liability", "is_active": True, "company__id": 5})
  
- Accounts created in 2025:
  list_accounts_tool(filters={"created_at__range": ["2025-01-01", "2025-12-31"]})
  
- Accounts with names containing "bank":
  search_accounts_tool(query="bank", filters={"is_active": True})

## Available Filter Operators:
- Exact: {"field": "value"}
- Contains (case-insensitive): {"field__icontains": "text"}
- Greater than: {"field__gt": 100}
- Greater/equal: {"field__gte": 100}
- Less than: {"field__lt": 1000}
- Less/equal: {"field__lte": 1000}
- In list: {"field__in": ["value1", "value2"]}
- Date range: {"field__range": ["2024-01-01", "2024-12-31"]}
- Is null: {"field__isnull": True}
- Related field: {"company__name": "ABC Corp", "parent_account__id": 10}
"""


# ============================================
# TOOLS - Company Operations
# ============================================

@mcp.tool()
def list_companies_tool(filters: dict = None, page: int = 1, page_size: int = 20) -> dict:
    """
    List all companies with optional filtering and pagination
    
    Args:
        filters: Optional dict for filtering (e.g., {"country": "USA", "is_active": True})
        page: Page number (default: 1)
        page_size: Results per page (default: 20, max: 100)
    
    Returns:
        Paginated list of companies with metadata
        
    Example filters:
        {"country": "USA"}
        {"name__icontains": "tech"}
        {"is_active": True}
    """
    if page_size > config.MAX_RESULTS_PER_QUERY:
        page_size = config.MAX_RESULTS_PER_QUERY
    return list_companies(filters, page, page_size)


@mcp.tool()
def get_company_tool(company_id: int) -> dict:
    """
    Get detailed information about a specific company
    
    Args:
        company_id: The unique ID of the company
    
    Returns:
        Company details including related counts
    """
    return get_company(company_id)


@mcp.tool()
def search_companies_tool(query: str, filters: dict = None, page: int = 1, page_size: int = 20) -> dict:
    """
    Search companies by name, abbreviation, or country with optional additional filters
    
    Args:
        query: Search string
        filters: Optional dict for additional filtering (e.g., {"is_active": True})
        page: Page number (default: 1)
        page_size: Results per page (default: 20)
    
    Returns:
        Matching companies
        
    Example:
        search_companies_tool("tech", {"country": "USA", "is_active": True})
    """
    if page_size > config.MAX_RESULTS_PER_QUERY:
        page_size = config.MAX_RESULTS_PER_QUERY
    return search_companies(query, filters, page, page_size)


@mcp.tool()
def get_company_accounts_tool(company_id: int, page: int = 1, page_size: int = 20) -> dict:
    """
    Get all accounts belonging to a specific company
    
    Args:
        company_id: The unique ID of the company
        page: Page number (default: 1)
        page_size: Results per page (default: 20)
    
    Returns:
        Company's chart of accounts
    """
    if page_size > config.MAX_RESULTS_PER_QUERY:
        page_size = config.MAX_RESULTS_PER_QUERY
    return get_company_accounts(company_id, page, page_size)


@mcp.tool()
def get_company_stats_tool(company_id: int) -> dict:
    """
    Get statistical summary for a company
    
    Args:
        company_id: The unique ID of the company
    
    Returns:
        Statistics: account count, suppliers, customers, invoices, budgets, financial summary
    """
    return get_company_stats(company_id)


# ============================================
# TOOLS - Account Operations
# ============================================

@mcp.tool()
def list_accounts_tool(filters: dict = None, page: int = 1, page_size: int = 20) -> dict:
    """
    List all accounts in the chart of accounts with optional filtering
    
    Args:
        filters: Optional dict for filtering (e.g., {"account_type": "Asset", "balance__gte": 1000})
        page: Page number (default: 1)
        page_size: Results per page (default: 20)
    
    Example filters:
        {"account_type": "Asset"}
        {"balance__gte": 10000}
        {"company__id": 5}
        {"is_group": False, "is_active": True}
    
    Returns:
        Paginated list of accounts
    """
    if page_size > config.MAX_RESULTS_PER_QUERY:
        page_size = config.MAX_RESULTS_PER_QUERY
    return list_accounts(filters, page, page_size)


@mcp.tool()
def get_account_tool(account_id: int) -> dict:
    """
    Get detailed information about a specific account
    
    Args:
        account_id: The unique ID of the account
    
    Returns:
        Account details with related counts
    """
    return get_account(account_id)


@mcp.tool()
def search_accounts_tool(query: str, filters: dict = None, page: int = 1, page_size: int = 20) -> dict:
    """
    Search accounts by name or account number with optional additional filters
    
    Args:
        query: Search string
        filters: Optional dict for additional filtering (e.g., {"account_type": "Asset"})
        page: Page number (default: 1)
        page_size: Results per page (default: 20)
    
    Returns:
        Matching accounts
        
    Example:
        search_accounts_tool("cash", {"account_type": "Asset", "balance__gte": 5000})
    """
    if page_size > config.MAX_RESULTS_PER_QUERY:
        page_size = config.MAX_RESULTS_PER_QUERY
    return search_accounts(query, filters, page, page_size)


@mcp.tool()
def get_account_balance_tool(account_id: int) -> dict:
    """
    Calculate account balance from journal entries
    
    Args:
        account_id: The unique ID of the account
    
    Returns:
        Balance calculation: total debits, credits, net balance, entry count
    """
    return get_account_balance(account_id)


@mcp.tool()
def get_account_hierarchy_tool(account_id: int) -> dict:
    """
    Get account hierarchy showing parent accounts and sub-accounts
    
    Args:
        account_id: The unique ID of the account
    
    Returns:
        Hierarchical structure with parents and children
    """
    return get_account_hierarchy(account_id)


# ============================================
# TOOLS - Invoice Operations
# ============================================

@mcp.tool()
def list_invoices_tool(filters: dict = None, page: int = 1, page_size: int = 20) -> dict:
    """
    List all invoices with optional filtering
    
    Args:
        filters: Optional dict for filtering (e.g., {"status": "paid", "total_amount__gte": 5000})
        page: Page number (default: 1)
        page_size: Results per page (default: 20)
    
    Example filters:
        {"status": "paid"}
        {"date__range": ["2025-01-01", "2025-12-31"]}
        {"supplier__country": "USA"}
    """
    if page_size > config.MAX_RESULTS_PER_QUERY:
        page_size = config.MAX_RESULTS_PER_QUERY
    return list_invoices(filters, page, page_size)


@mcp.tool()
def get_invoice_tool(invoice_id: int) -> dict:
    """Get detailed information about a specific invoice"""
    return get_invoice(invoice_id)


@mcp.tool()
def search_invoices_tool(query: str, filters: dict = None, page: int = 1, page_size: int = 20) -> dict:
    """Search invoices by invoice number or ID"""
    if page_size > config.MAX_RESULTS_PER_QUERY:
        page_size = config.MAX_RESULTS_PER_QUERY
    return search_invoices(query, filters, page, page_size)


@mcp.tool()
def get_invoice_stats_tool(filters: dict = None) -> dict:
    """Get invoice statistics (total count, amount, by status)"""
    return get_invoice_stats(filters)


# ============================================
# TOOLS - Journal Entry Operations
# ============================================

@mcp.tool()
def list_journal_entries_tool(filters: dict = None, page: int = 1, page_size: int = 20) -> dict:
    """
    List all journal entries with optional filtering
    
    Args:
        filters: Optional dict for filtering (e.g., {"date__year": 2025, "debit_amount__gte": 1000})
    """
    if page_size > config.MAX_RESULTS_PER_QUERY:
        page_size = config.MAX_RESULTS_PER_QUERY
    return list_journal_entries(filters, page, page_size)


@mcp.tool()
def get_journal_entry_tool(entry_id: int) -> dict:
    """Get detailed information about a specific journal entry"""
    return get_journal_entry(entry_id)


@mcp.tool()
def search_journal_entries_tool(query: str, filters: dict = None, page: int = 1, page_size: int = 20) -> dict:
    """Search journal entries by entry number or description"""
    if page_size > config.MAX_RESULTS_PER_QUERY:
        page_size = config.MAX_RESULTS_PER_QUERY
    return search_journal_entries(query, filters, page, page_size)


@mcp.tool()
def get_journal_stats_tool(filters: dict = None) -> dict:
    """Get journal entry statistics (debits, credits, balance)"""
    return get_journal_stats(filters)


# ============================================
# TOOLS - Supplier Operations
# ============================================

@mcp.tool()
def list_suppliers_tool(filters: dict = None, page: int = 1, page_size: int = 20) -> dict:
    """
    List all suppliers with optional filtering
    
    Args:
        filters: Optional dict for filtering (e.g., {"gst_category": "registered", "country": "India"})
    """
    if page_size > config.MAX_RESULTS_PER_QUERY:
        page_size = config.MAX_RESULTS_PER_QUERY
    return list_suppliers(filters, page, page_size)


@mcp.tool()
def get_supplier_tool(supplier_id: int) -> dict:
    """Get detailed information about a specific supplier"""
    return get_supplier(supplier_id)


@mcp.tool()
def search_suppliers_tool(query: str, filters: dict = None, page: int = 1, page_size: int = 20) -> dict:
    """Search suppliers by name or GSTIN"""
    if page_size > config.MAX_RESULTS_PER_QUERY:
        page_size = config.MAX_RESULTS_PER_QUERY
    return search_suppliers(query, filters, page, page_size)


# ============================================
# TOOLS - Customer Operations
# ============================================

@mcp.tool()
def list_customers_tool(filters: dict = None, page: int = 1, page_size: int = 20) -> dict:
    """
    List all customers with optional filtering
    
    Args:
        filters: Optional dict for filtering (e.g., {"gst_category": "registered", "country": "USA"})
    """
    if page_size > config.MAX_RESULTS_PER_QUERY:
        page_size = config.MAX_RESULTS_PER_QUERY
    return list_customers(filters, page, page_size)


@mcp.tool()
def get_customer_tool(customer_id: int) -> dict:
    """Get detailed information about a specific customer"""
    return get_customer(customer_id)


@mcp.tool()
def search_customers_tool(query: str, filters: dict = None, page: int = 1, page_size: int = 20) -> dict:
    """Search customers by name or GSTIN"""
    if page_size > config.MAX_RESULTS_PER_QUERY:
        page_size = config.MAX_RESULTS_PER_QUERY
    return search_customers(query, filters, page, page_size)


# ============================================
# TOOLS - Budget Operations
# ============================================

@mcp.tool()
def list_budgets_tool(filters: dict = None, page: int = 1, page_size: int = 20) -> dict:
    """
    List all budgets with optional filtering
    
    Args:
        filters: Optional dict for filtering (e.g., {"fiscal_year_from": "2025-2026"})
    """
    if page_size > config.MAX_RESULTS_PER_QUERY:
        page_size = config.MAX_RESULTS_PER_QUERY
    return list_budgets(filters, page, page_size)


@mcp.tool()
def get_budget_tool(budget_id: int) -> dict:
    """Get detailed information about a specific budget"""
    return get_budget(budget_id)


@mcp.tool()
def search_budgets_tool(query: str, filters: dict = None, page: int = 1, page_size: int = 20) -> dict:
    """Search budgets by series"""
    if page_size > config.MAX_RESULTS_PER_QUERY:
        page_size = config.MAX_RESULTS_PER_QUERY
    return search_budgets(query, filters, page, page_size)


# ============================================
# TOOLS - Cost Center Operations
# ============================================

@mcp.tool()
def list_cost_centers_tool(filters: dict = None, page: int = 1, page_size: int = 20) -> dict:
    """
    List all cost centers with optional filtering
    
    Args:
        filters: Optional dict for filtering (e.g., {"is_group": False, "is_disabled": False})
    """
    if page_size > config.MAX_RESULTS_PER_QUERY:
        page_size = config.MAX_RESULTS_PER_QUERY
    return list_cost_centers(filters, page, page_size)


@mcp.tool()
def get_cost_center_tool(cost_center_id: int) -> dict:
    """Get detailed information about a specific cost center"""
    return get_cost_center(cost_center_id)


@mcp.tool()
def search_cost_centers_tool(query: str, filters: dict = None, page: int = 1, page_size: int = 20) -> dict:
    """Search cost centers by name or number"""
    if page_size > config.MAX_RESULTS_PER_QUERY:
        page_size = config.MAX_RESULTS_PER_QUERY
    return search_cost_centers(query, filters, page, page_size)


# ============================================
# TOOLS - Tax Operations
# ============================================

@mcp.tool()
def list_tax_rules_tool(filters: dict = None, page: int = 1, page_size: int = 20) -> dict:
    """
    List all tax rules with optional filtering
    
    Args:
        filters: Optional dict for filtering (e.g., {"tax_type": "sales", "company__id": 5})
    """
    if page_size > config.MAX_RESULTS_PER_QUERY:
        page_size = config.MAX_RESULTS_PER_QUERY
    return list_tax_rules(filters, page, page_size)


@mcp.tool()
def get_tax_rule_tool(tax_rule_id: int) -> dict:
    """Get detailed information about a specific tax rule"""
    return get_tax_rule(tax_rule_id)


@mcp.tool()
def search_tax_rules_tool(query: str, filters: dict = None, page: int = 1, page_size: int = 20) -> dict:
    """Search tax rules by item, city, state, or country"""
    if page_size > config.MAX_RESULTS_PER_QUERY:
        page_size = config.MAX_RESULTS_PER_QUERY
    return search_tax_rules(query, filters, page, page_size)


@mcp.tool()
def list_tax_categories_tool(filters: dict = None, page: int = 1, page_size: int = 20) -> dict:
    """List all tax categories"""
    if page_size > config.MAX_RESULTS_PER_QUERY:
        page_size = config.MAX_RESULTS_PER_QUERY
    return list_tax_categories(filters, page, page_size)


@mcp.tool()
def list_tax_templates_tool(filters: dict = None, page: int = 1, page_size: int = 20) -> dict:
    """List all tax item templates"""
    if page_size > config.MAX_RESULTS_PER_QUERY:
        page_size = config.MAX_RESULTS_PER_QUERY
    return list_tax_templates(filters, page, page_size)


# ============================================
# RUN SERVER
# ============================================

if __name__ == "__main__":
    print(f"Starting {config.SERVER_NAME} v{config.SERVER_VERSION}")
    print(f"Description: {config.SERVER_DESCRIPTION}")
    print("=" * 60)
    mcp.run(transport="stdio")
