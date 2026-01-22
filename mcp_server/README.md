# MCP Server for Finance Django Application

This MCP (Model Context Protocol) server provides AI-powered tools to query and analyze the Finance Management System database.

## Features

- **Micro-tools Design**: Each operation has a dedicated tool for precision
- **Stateless & Idempotent**: Safe for repeated calls with consistent results
- **Resource Access**: Database schema and query examples
- **Pagination**: Built-in result limiting for large datasets
- **Error Handling**: Graceful error responses with debugging info

## Architecture

```
mcp_server/
├── server.py           # Main FastMCP server
├── config.py           # Django integration & settings
├── requirements.txt    # Dependencies
├── FILTERING_GUIDE.md  # Dynamic filtering documentation
├── utils/
│   └── helpers.py     # Shared utilities (filtering, serialization, pagination)
└── tools/
    ├── company_tools.py    # Company operations (5 tools)
    ├── account_tools.py    # Account operations (5 tools)
    ├── invoice_tools.py    # Invoice operations (4 tools)
    ├── journal_tools.py    # Journal entry operations (4 tools)
    ├── supplier_tools.py   # Supplier operations (3 tools)
    ├── customer_tools.py   # Customer operations (3 tools)
    ├── budget_tools.py     # Budget operations (3 tools)
    ├── cost_center_tools.py # Cost center operations (3 tools)
    └── tax_tools.py        # Tax operations (5 tools)
```

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure Django:
- Ensure `DJANGO_SETTINGS_MODULE` is set in `config.py`
- Database migrations should be applied

## Usage

### Running the Server

```bash
cd mcp_server
python server.py
```

The server runs on stdio transport for MCP client integration.

### Available Tools (35 Total)

#### Company Tools (5)
- `list_companies_tool(filters, page, page_size)` - List with dynamic filtering
- `get_company_tool(company_id)` - Get specific company details
- `search_companies_tool(query, filters)` - Search companies by name
- `get_company_accounts_tool(company_id)` - Get all accounts for a company
- `get_company_stats_tool(company_id)` - Get company statistics

#### Account Tools (5)
- `list_accounts_tool(filters, page, page_size)` - List with dynamic filtering
- `get_account_tool(account_id)` - Get specific account details
- `search_accounts_tool(query, filters)` - Search accounts by name/code
- `get_account_balance_tool(account_id)` - Calculate current balance
- `get_account_hierarchy_tool(account_id)` - Get parent/child hierarchy

#### Invoice Tools (4)
- `list_invoices_tool(filters, page, page_size)` - List with dynamic filtering
- `get_invoice_tool(invoice_id)` - Get specific invoice details
- `search_invoices_tool(query, filters)` - Search by invoice number
- `get_invoice_stats_tool(filters)` - Get statistics (total, by status)

#### Journal Entry Tools (4)
- `list_journal_entries_tool(filters, page, page_size)` - List with dynamic filtering
- `get_journal_entry_tool(entry_id)` - Get specific entry details
- `search_journal_entries_tool(query, filters)` - Search by entry number
- `get_journal_stats_tool(filters)` - Get statistics (debits, credits, balance)

#### Supplier Tools (3)
- `list_suppliers_tool(filters, page, page_size)` - List with dynamic filtering
- `get_supplier_tool(supplier_id)` - Get specific supplier details
- `search_suppliers_tool(query, filters)` - Search by name or GSTIN

#### Customer Tools (3)
- `list_customers_tool(filters, page, page_size)` - List with dynamic filtering
- `get_customer_tool(customer_id)` - Get specific customer details
- `search_customers_tool(query, filters)` - Search by name or GSTIN

#### Budget Tools (3)
- `list_budgets_tool(filters, page, page_size)` - List with dynamic filtering
- `get_budget_tool(budget_id)` - Get specific budget details
- `search_budgets_tool(query, filters)` - Search by series

#### Cost Center Tools (3)
- `list_cost_centers_tool(filters, page, page_size)` - List with dynamic filtering
- `get_cost_center_tool(cost_center_id)` - Get specific cost center details
- `search_cost_centers_tool(query, filters)` - Search by name or number

#### Tax Tools (5)
- `list_tax_rules_tool(filters, page, page_size)` - List with dynamic filtering
- `get_tax_rule_tool(tax_rule_id)` - Get specific tax rule details
- `search_tax_rules_tool(query, filters)` - Search by location/item
- `list_tax_categories_tool(filters, page, page_size)` - List tax categories
- `list_tax_templates_tool(filters, page, page_size)` - List tax templates

### Available Resources

#### Database Schema
```python
# Access complete database schema documentation
resource = get_database_schema()
```

#### Prompt Templates
```python
# Get example queries for companies
examples = get_company_query_examples()

# Get example queries for accounts
examples = get_account_query_examples()
```

## Configuration

Edit `config.py` to customize:

```python
DJANGO_SETTINGS_MODULE = "core.settings"
MAX_RESULTS_PER_QUERY = 100
DEFAULT_PAGE_SIZE = 20
```

## Best Practices

1. **Use Specific Tools**: Don't use generic tools when specific ones exist
   - ✅ `get_company_tool(5)` 
   - ❌ `search_companies_tool("company 5")`

2. **Paginate Large Results**: Always use pagination for list operations
   ```python
   list_companies_tool(page=1, page_size=20)
   ```

3. **Check Error Responses**: All tools return structured errors
   ```json
   {
     "success": false,
     "error": "Company with ID 999 not found",
     "error_type": "NotFound"
   }
   ```

4. **Consult Schema**: Use `get_database_schema()` resource for field details

## Development Status

### Completed ✅
- [x] Project structure and architecture
- [x] Configuration and Django integration
- [x] Utility functions (filtering, serialization, pagination, error handling)
- [x] Dynamic filtering system (works across all models)
- [x] Company tools (5/5)
- [x] Account tools (5/5)
- [x] Invoice tools (4/4)
- [x] Journal entry tools (4/4)
- [x] Supplier tools (3/3)
- [x] Customer tools (3/3)
- [x] Budget tools (3/3)
- [x] Cost center tools (3/3)
- [x] Tax tools (5/5)
- [x] Main server setup with all tools registered (35 tools total)
- [x] Documentation (README, FILTERING_GUIDE)

### Ready for Testing 🧪
- [ ] Test with MCP Inspector
- [ ] Integration with chatbot
- [ ] Performance testing with large datasets

## Testing

Use MCP Inspector to test tools:

```bash
npx @modelcontextprotocol/inspector python server.py
```

## Tool Design Principles

Each tool follows these principles:

1. **Single Responsibility**: One operation per tool
2. **Stateless**: No server-side state between calls
3. **Idempotent**: Same input = same output
4. **Type-Safe**: Full type annotations
5. **Well-Documented**: Clear docstrings and examples
6. **Error Handling**: Graceful failures with context
7. **Dynamic Filtering**: Use filters parameter instead of creating specialized tools

## Key Features

### Dynamic Filtering System
Instead of creating hundreds of specialized tools, use the `filters` parameter:

```python
# One tool, infinite queries
list_accounts_tool(filters={"account_type": "Asset", "balance__gte": 10000})
list_accounts_tool(filters={"company__id": 5, "is_active": True})
list_invoices_tool(filters={"status": "paid", "date__year": 2025})
```

See `FILTERING_GUIDE.md` for complete documentation on filter operators and examples.

## Reference Documentation

- **DATABASE_SCHEMA.md**: Complete table definitions and relationships
- **CHATBOT_DOCUMENTATION.md**: Integration with chatbot service
- FastMCP Documentation: https://github.com/jlowin/fastmcp

## Contributing

When adding new tools:

1. Create tool file in `tools/` directory
2. Follow micro-tools pattern (one function per operation)
3. Add type annotations and docstrings
4. Register tools in `server.py`
5. Add prompt examples if needed
6. Update this README

## License

Part of the Finance Management System Django application.
