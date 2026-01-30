"""
Finance Management System MCP Server
New Architecture: 5 Generic Data Tools + Schema Guides + CRUD Prompt Templates

Tool Count Reduction:
- OLD: 35+ table-specific tools
- NEW: 5 generic data tools + 24 schema/helper tools = 29 total

This architecture:
1. Uses 5 core generic tools for ALL tables
2. Schema guides provide table-specific context
3. CRUD prompt templates provide few-shot examples
4. Easy to add new tables without new tools
"""
from fastmcp import FastMCP
from pathlib import Path
import sys
import os
from typing import Optional, Dict, Any
from asgiref.sync import sync_to_async

# Add parent directory to Python path for Django imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import config first to initialize Django
import config

# Import generic data tools (6 core tools - added referential integrity check)
from tools.generic_data_tools import (
    get_record,
    query_records,
    create_record,
    update_record,
    delete_record,
    check_referential_integrity,
    list_available_tables
)

# Import prompt tools (schema guides and CRUD guides)
from tools.prompt_tools import register_prompt_tools

# Create FastMCP instance
mcp = FastMCP(
    name=config.SERVER_NAME,
    version=config.SERVER_VERSION
)

# Register all schema guide tools (21 tables + filter syntax + CRUD operation guide)
register_prompt_tools(mcp)


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


# ============================================
# PROMPTS - Example Queries for New Architecture
# ============================================

@mcp.prompt()
def generic_tool_examples() -> str:
    """Examples of how to use the generic data tools"""
    return """
# Generic Data Tools Examples

## WORKFLOW: Always follow this order
1. Call get_<table>_schema_guide() to understand the table
2. Call get_crud_operation_guide(operation) for few-shot examples (if CRUD)
3. Use generic tool with table name

## Reading Data

### Get single record by ID:
get_record_tool(table="company", record_id=5)
get_record_tool(table="invoice", record_id=123)
get_record_tool(table="supplier", record_id=10)

### Query multiple records with filters:
query_records_tool(table="company", filters={"country": "USA"})
query_records_tool(table="invoice", filters={"status": "paid", "date__gte": "2024-01-01"})
query_records_tool(table="account", filters={"account_type": "asset", "is_disabled": False})

### Query with text search:
query_records_tool(table="company", text_search="tech")
query_records_tool(table="supplier", text_search="ABC Corp")
query_records_tool(table="invoice", text_search="INV-2024")

### Combined filters and search:
query_records_tool(table="supplier", text_search="import", filters={"country": "Pakistan"})

### Pagination and ordering:
query_records_tool(table="account", page=2, page_size=50, order_by="-created_at")

## Creating Data

### Create a company:
create_record_tool(table="company", data={"name": "Tech Corp", "country": "USA", "default_currency": "USD"})

### Create an account (with FK):
create_record_tool(table="account", data={"name": "Cash", "company": 5, "account_type": "asset"})

### Create an invoice:
create_record_tool(table="invoice", data={
    "invoice_id": "INV-2024-001",
    "invoice_number": "2024-001",
    "date": "2024-01-15",
    "supplier": 10,
    "company": 1,
    "amount_before_vat": 5000.00,
    "total_vat": 0.00,
    "total_amount": 5000.00,
    "status": "draft"
})

## Updating Data

### Update company name:
update_record_tool(table="company", record_id=5, data={"name": "New Name Inc"})

### Update invoice status:
update_record_tool(table="invoice", record_id=123, data={"status": "paid"})

### Update multiple fields:
update_record_tool(table="supplier", record_id=10, data={"contact_email": "new@email.com", "city": "New York"})

## Deleting Data (always confirm first!)

### Delete a record:
delete_record_tool(table="accounting_dimension", record_id=7, confirm=True)

## Filter Syntax Reference:
- Exact: {"field": "value"}
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


# ============================================
# GENERIC DATA TOOLS (5 Core Tools)
# ============================================

@mcp.tool()
async def get_record_tool(
    table: str,
    record_id: int,
    include_related_counts: bool = True
) -> dict:
    """
    Get a single record by ID from any table.
    
    WORKFLOW:
    1. First call get_<table>_schema_guide() to understand the schema
    2. Then call this tool with the table name and record ID
    
    Args:
        table: Name of the table (e.g., "company", "account", "invoice", "supplier")
        record_id: The ID of the record to retrieve
        include_related_counts: Whether to include counts of related objects (default: True)
        
    Returns:
        Record details with optional related counts
        
    Available tables:
        company, account, invoice, journal_entry, supplier, customer,
        budget, cost_center, cost_center_allocation, accounting_dimension,
        tax_item_template, tax_category, tax_rule, tax_withholding_category,
        tax_withholding_rate, tax_category_account, deduction_certificate,
        bank_account_type, bank_account_subtype, bank_account, user_profile
    """
    return await sync_to_async(get_record)(table, record_id, include_related_counts)


@mcp.tool()
async def query_records_tool(
    table: str,
    filters: Optional[Dict[str, Any]] = None,
    text_search: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    order_by: Optional[str] = None
) -> dict:
    """
    Query multiple records from any table with optional filters and text search.
    
    WORKFLOW:
    1. First call get_<table>_schema_guide() to understand available fields
    2. Optionally call get_filter_syntax_guide() for complex filters
    3. Then call this tool with appropriate filters/search
    
    Args:
        table: Name of the table (e.g., "company", "accounts", "invoices")
        filters: Optional dict of field filters
        text_search: Optional text to search across searchable fields
        page: Page number (1-indexed, default: 1)
        page_size: Number of results per page (default: 20, max: 100)
        order_by: Field to order by (prefix with - for descending)
        
    Filter examples:
        {"country": "USA"}
        {"name__icontains": "tech"}
        {"balance__gte": 1000}
        {"status__in": ["pending", "approved"]}
        {"date__range": ["2024-01-01", "2024-12-31"]}
        {"company__id": 5}
    """
    if page_size > config.MAX_RESULTS_PER_QUERY:
        page_size = config.MAX_RESULTS_PER_QUERY
    return await sync_to_async(query_records)(table, filters, text_search, page, page_size, order_by)


@mcp.tool()
async def create_record_tool(
    table: str,
    data: Dict[str, Any]
) -> dict:
    """
    Create a new record in any table.
    
    WORKFLOW:
    1. First call get_<table>_schema_guide() to understand required fields
    2. Call get_crud_operation_guide("create") for few-shot examples
    3. Then call this tool with the validated data
    
    Args:
        table: Name of the table (e.g., "company", "account", "invoice")
        data: Dictionary of field values for the new record
              For foreign keys, pass integer IDs (not names)
        
    Returns:
        Created record with ID
        
    Important:
        - Check schema guide for required vs optional fields
        - Foreign keys must be integer IDs
        - Date fields use format "YYYY-MM-DD"
        - Decimal fields should be numbers, not strings
    """
    return await sync_to_async(create_record)(table, data)


@mcp.tool()
async def update_record_tool(
    table: str,
    record_id: int,
    data: Dict[str, Any]
) -> dict:
    """
    Update an existing record in any table.
    
    WORKFLOW:
    1. First call get_<table>_schema_guide() to understand available fields
    2. Call get_record_tool() to verify the record exists and see current values
    3. Call get_crud_operation_guide("update") for few-shot examples
    4. Then call this tool with only the changed fields
    
    Args:
        table: Name of the table (e.g., "company", "account", "invoice")
        record_id: The ID of the record to update
        data: Dictionary of field values to update (only include fields to change)
        
    Returns:
        Updated record with change tracking (old_values and new_values)
        
    Important:
        - Only include fields that are changing
        - Never try to update id, created_at, or auto-generated fields
        - Check unique constraints in schema guide
    """
    return await sync_to_async(update_record)(table, record_id, data)


@mcp.tool()
async def delete_record_tool(
    table: str,
    record_id: int,
    confirm: bool = False
) -> dict:
    """
    Delete a record from any table.
    
    ⚠️ DESTRUCTIVE OPERATION - ALWAYS CONFIRM WITH USER FIRST!
    
    WORKFLOW:
    1. First call get_<table>_schema_guide() to understand relationships
    2. Call get_record_tool() to verify the record and check for related data
    3. Call get_crud_operation_guide("delete") for few-shot examples
    4. ASK USER FOR CONFIRMATION before proceeding
    5. Then call this tool with confirm=True
    
    Args:
        table: Name of the table (e.g., "company", "account", "invoice")
        record_id: The ID of the record to delete
        confirm: Must be True to actually delete (safety check)
        
    Returns:
        Deletion confirmation with deleted record data
        
    Important:
        - NEVER delete without user confirmation
        - Check for related records that might be affected
        - Protected relationships will prevent deletion
    """
    return await sync_to_async(delete_record)(table, record_id, confirm)


@mcp.tool()
async def check_referential_integrity_tool(
    table: str,
    record_id: int
) -> dict:
    """
    Check if a record has dependencies before deletion.
    
    ⚠️ CRITICAL: ALWAYS call this BEFORE delete_record_tool!
    
    This tool checks all reverse foreign key relationships to determine if other
    records depend on this record. Prevents data integrity violations by blocking
    deletions of records that are referenced by other tables.
    
    WORKFLOW FOR DELETION:
    1. Get record: get_record_tool(table, record_id)
    2. CHECK INTEGRITY: Call this tool to check for dependencies
    3. If has_dependencies=True:
       a. Display the dependencies list to user with counts and sample IDs
       b. Explain which tables/records depend on this
       c. STOP - DO NOT proceed with deletion
       d. Ask user to handle dependencies first (delete or reassign)
    4. If has_dependencies=False: Proceed to delete_record_tool(confirm=True)
    
    Args:
        table: Name of the table (e.g., "company", "account", "supplier")
        record_id: The ID of the record to check for dependencies
        
    Returns:
        {
            "success": true,
            "data": {
                "table": "company",
                "record_id": 22,
                "has_dependencies": true/false,
                "can_delete": true/false,
                "dependencies": [
                    {
                        "table": "account",
                        "count": 5,
                        "field": "company",
                        "sample_ids": [95, 96, 97, 98, 99]
                    },
                    {
                        "table": "invoice", 
                        "count": 12,
                        "field": "company",
                        "sample_ids": [101, 102, 103, 104, 105]
                    }
                ],
                "summary": "Cannot delete: 5 account + 12 invoice records depend on this"
            }
        }
        
    Example User Message When Dependencies Found:
    "Cannot delete Company 'ABC Corp' (ID: 22) because:
    - 5 Account records reference it (IDs: 95, 96, 97, 98, 99)
    - 12 Invoice records reference it (IDs: 101, 102, 103, 104, 105)
    
    You must first delete or reassign these dependent records before deleting the company."
    
    Important:
        - ALWAYS call this before attempting deletion
        - NEVER delete if has_dependencies=True
        - Show user the full dependencies list with counts
        - Explain which specific records are blocking the deletion
    """
    return await sync_to_async(check_referential_integrity)(table, record_id)


@mcp.tool()
async def validate_required_fields_tool(
    table: str,
    provided_data: dict
) -> dict:
    """
    Validate if all required fields are provided before creating a record.
    
    ⚠️ CRITICAL: ALWAYS call this BEFORE create_record_tool!
    
    WORKFLOW FOR CREATION:
    1. Get schema guide: get_<table>_schema_guide()
    2. VALIDATE FIELDS: Call this tool with user-provided data
    3. If is_valid=False:
       a. Display missing_required_fields to user
       b. For each missing FK, call list_foreign_key_options_tool
       c. Ask user to provide missing information
       d. DO NOT call create_record_tool yet!
    4. If is_valid=True: Proceed to create_record_tool
    
    Args:
        table: Name of the table (e.g., "account", "invoice")
        provided_data: Dictionary of fields user wants to create
        
    Returns:
        Validation result with:
        - is_valid: True if all required fields provided
        - missing_required_fields: List of fields user needs to provide
        - missing_foreign_keys: FK fields that need values
        - required_fields_info: Description of each required field
        
    Example Response (invalid):
        {
            "is_valid": false,
            "missing_required_fields": ["company", "account_type"],
            "missing_foreign_keys": ["company"],
            "required_fields_info": {
                "company": "Foreign key to Company table (required)",
                "account_type": "Choice field: asset/liability/equity/income/expense (required)"
            }
        }
    """
    from tools.generic_data_tools import validate_required_fields
    return await sync_to_async(validate_required_fields)(table, provided_data)


@mcp.tool()
async def list_foreign_key_options_tool(
    table: str,
    foreign_key_field: str,
    page: int = 1,
    page_size: int = 10
) -> dict:
    """
    List available records from a foreign key related table for user selection.
    
    ⚠️ CRITICAL: When creating a record with FK fields, call this to show options to user!
    
    WORKFLOW:
    1. validate_required_fields_tool identifies missing FKs
    2. For each missing FK, call this tool
    3. Display options to user in a friendly format
    4. User selects by name or ID
    5. Use the ID in create_record_tool
    
    Args:
        table: Name of the table being created (e.g., "account")
        foreign_key_field: Name of the FK field (e.g., "company")
        page: Page number (default 1)
        page_size: Records per page (default 10, max 50)
        
    Returns:
        List of available records with ID and display name
        
    Example Response:
        {
            "foreign_key_field": "company",
            "related_table": "Company",
            "options": [
                {"id": 22, "display": "TechCorp Solutions USA"},
                {"id": 23, "display": "Global Corp International"},
                {"id": 24, "display": "SmartTech Industries"}
            ],
            "total": 5,
            "instruction": "User should select one by name or ID"
        }
        
    Display to user:
        "Please select a company from the list:
        - TechCorp Solutions USA (ID: 22)
        - Global Corp International (ID: 23)
        - SmartTech Industries (ID: 24)"
    """
    from tools.generic_data_tools import list_foreign_key_options
    return await sync_to_async(list_foreign_key_options)(table, foreign_key_field, page, page_size)


# ============================================
# RUN SERVER
# ============================================

if __name__ == "__main__":
    import sys
    
    # Only print startup messages to stderr (not stdout, which is used for JSON-RPC)
    print(f"Starting {config.SERVER_NAME} v{config.SERVER_VERSION}", file=sys.stderr)
    print(f"Description: {config.SERVER_DESCRIPTION}", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    print("New Architecture: 5 Generic Data Tools + Schema Guides", file=sys.stderr)
    print("Total Tools: ~29 (5 data + 24 schema/helper)", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    
    # Run MCP server with stdio transport
    mcp.run(transport="stdio")
