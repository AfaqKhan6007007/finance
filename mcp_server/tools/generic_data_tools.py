"""
Generic Data Tools for MCP Server
5 core generic tools that work across ALL tables:
1. get_record - Get single record by ID
2. query_records - Query multiple records with filters/search
3. create_record - Create new record
4. update_record - Update existing record
5. delete_record - Delete record

This architecture reduces tool count from 98+ to just 5 core tools.
"""
from typing import Dict, Any, List, Optional
from django.db.models import Q
from django.core.exceptions import ValidationError
from utils.helpers import (
    format_success_response,
    format_error_response,
    serialize_queryset,
    serialize_model_instance,
    paginate_results,
    get_tool_metadata,
    apply_filters
)

# Import all Django models
from finance.models import (
    Company,
    Account,
    Invoice,
    JournalEntry,
    Supplier,
    Customer,
    Budget,
    CostCenter,
    CostCenterAllocation,
    AccountingDimension,
    TaxItemTemplate,
    TaxCategory,
    TaxRule,
    TaxWithholdingCategory,
    TaxWithholdingRate,
    TaxCategoryAccount,
    DeductionCertificate,
    BankAccountType,
    BankAccountSubtype,
    BankAccount,
    UserProfile,
)


# ============================================
# TABLE REGISTRY - Maps table names to models
# ============================================
TABLE_REGISTRY = {
    # Core Business Entities
    "company": Company,
    "companies": Company,  # Alias for convenience
    
    "account": Account,
    "accounts": Account,
    
    "invoice": Invoice,
    "invoices": Invoice,
    
    "journal_entry": JournalEntry,
    "journal_entries": JournalEntry,
    
    # Contacts
    "supplier": Supplier,
    "suppliers": Supplier,
    
    "customer": Customer,
    "customers": Customer,
    
    # Planning & Budgeting
    "budget": Budget,
    "budgets": Budget,
    
    "cost_center": CostCenter,
    "cost_centers": CostCenter,
    
    "cost_center_allocation": CostCenterAllocation,
    "cost_center_allocations": CostCenterAllocation,
    
    "accounting_dimension": AccountingDimension,
    "accounting_dimensions": AccountingDimension,
    
    # Tax Configuration
    "tax_item_template": TaxItemTemplate,
    "tax_item_templates": TaxItemTemplate,
    
    "tax_category": TaxCategory,
    "tax_categories": TaxCategory,
    
    "tax_rule": TaxRule,
    "tax_rules": TaxRule,
    
    "tax_withholding_category": TaxWithholdingCategory,
    "tax_withholding_categories": TaxWithholdingCategory,
    
    "tax_withholding_rate": TaxWithholdingRate,
    "tax_withholding_rates": TaxWithholdingRate,
    
    "tax_category_account": TaxCategoryAccount,
    "tax_category_accounts": TaxCategoryAccount,
    
    "deduction_certificate": DeductionCertificate,
    "deduction_certificates": DeductionCertificate,
    
    # Banking
    "bank_account_type": BankAccountType,
    "bank_account_types": BankAccountType,
    
    "bank_account_subtype": BankAccountSubtype,
    "bank_account_subtypes": BankAccountSubtype,
    
    "bank_account": BankAccount,
    "bank_accounts": BankAccount,
    
    # User Management
    "user_profile": UserProfile,
    "user_profiles": UserProfile,
}


# ============================================
# SEARCH FIELDS - Fields to search per table
# ============================================
SEARCH_FIELDS = {
    "company": ["name", "abbreviation", "country", "tax_id", "domain"],
    "account": ["name", "account_number"],
    "invoice": ["invoice_id", "invoice_number", "supplier_vat", "customer_vat"],
    "journal_entry": ["entry_number", "description"],
    "supplier": ["name", "gstin_uin", "contact_email", "city", "country"],
    "customer": ["name", "gstin_uin", "contact_email", "city", "country"],
    "budget": ["series"],
    "cost_center": ["name", "cost_center_number"],
    "cost_center_allocation": [],
    "accounting_dimension": ["name"],
    "tax_item_template": ["title"],
    "tax_category": ["title"],
    "tax_rule": ["item", "item_group", "billing_city", "shipping_city"],
    "tax_withholding_category": ["name", "category_name", "section"],
    "tax_withholding_rate": ["tax_withholding_group"],
    "tax_category_account": [],
    "deduction_certificate": ["certificate_number", "pan_number"],
    "bank_account_type": ["account_type"],
    "bank_account_subtype": ["account_subtype"],
    "bank_account": ["name", "bank", "iban", "bank_account_number"],
    "user_profile": ["phone_number"],
}


# ============================================
# RELATED COUNTS - Related data to include in GET
# ============================================
RELATED_COUNTS = {
    "company": [
        ("accounts", "total_accounts"),
        ("suppliers", "total_suppliers"),
        ("customers", "total_customers"),
        ("invoices", "total_invoices"),
        ("budgets", "total_budgets"),
        ("cost_centers", "total_cost_centers"),
        ("journal_entries", "total_journal_entries"),
    ],
    "account": [
        ("journal_entries", "total_journal_entries"),
        ("budgets", "total_budgets"),
        ("sub_accounts", "total_sub_accounts"),
    ],
    "supplier": [
        ("invoices", "total_invoices"),
        ("deduction_certificates", "total_certificates"),
    ],
    "customer": [
        ("invoices", "total_invoices"),
        ("tax_rules", "total_tax_rules"),
    ],
    "cost_center": [
        ("children", "total_children"),
        ("allocations", "total_allocations"),
    ],
    "tax_withholding_category": [
        ("rates", "total_rates"),
        ("accounts", "total_accounts"),
        ("deduction_certificates", "total_certificates"),
    ],
    "tax_category": [
        ("tax_rules", "total_rules"),
    ],
    "tax_item_template": [
        ("sales_tax_rules", "total_rules"),
    ],
    "bank_account_type": [
        ("bank_accounts", "total_accounts"),
    ],
    "bank_account_subtype": [
        ("bank_accounts", "total_accounts"),
    ],
}


def _normalize_table_name(table: str) -> str:
    """Normalize table name to singular lowercase form"""
    table = table.lower().strip()
    # Handle common variations
    if table.endswith("ies"):
        # Handle special cases like "companies" -> "company"
        return table[:-3] + "y"
    elif table.endswith("s") and not table.endswith("ss"):
        return table[:-1]
    return table


def _get_model(table: str):
    """Get Django model class from table name"""
    table_lower = table.lower().strip()
    
    # Try exact match first
    if table_lower in TABLE_REGISTRY:
        return TABLE_REGISTRY[table_lower]
    
    # Try normalized name
    normalized = _normalize_table_name(table_lower)
    if normalized in TABLE_REGISTRY:
        return TABLE_REGISTRY[normalized]
    
    return None


def _build_search_query(model_name: str, search_text: str) -> Q:
    """Build Q object for text search across searchable fields"""
    normalized_name = _normalize_table_name(model_name)
    search_fields = SEARCH_FIELDS.get(normalized_name, [])
    
    if not search_fields or not search_text:
        return Q()
    
    q_objects = Q()
    for field in search_fields:
        q_objects |= Q(**{f"{field}__icontains": search_text})
    
    return q_objects


def _add_related_counts(instance, data: dict, model_name: str) -> dict:
    """Add related object counts to the response data"""
    normalized_name = _normalize_table_name(model_name)
    related_configs = RELATED_COUNTS.get(normalized_name, [])
    
    for related_name, count_key in related_configs:
        try:
            related_manager = getattr(instance, related_name, None)
            if related_manager is not None:
                data[count_key] = related_manager.count()
        except Exception:
            data[count_key] = 0
    
    return data


# ============================================
# CORE GENERIC TOOLS
# ============================================

def get_record(
    table: str,
    record_id: int,
    include_related_counts: bool = True
) -> Dict[str, Any]:
    """
    Get a single record by ID from any table.
    
    WORKFLOW:
    1. First call get_<table>_schema_guide() to understand the schema
    2. Then call this tool with the table name and record ID
    
    Args:
        table: Name of the table (e.g., "company", "account", "invoice")
        record_id: The ID of the record to retrieve
        include_related_counts: Whether to include counts of related objects
        
    Returns:
        Record details with optional related counts
        
    Example:
        get_record(table="company", record_id=5)
        get_record(table="invoice", record_id=123, include_related_counts=True)
    """
    tool_name = "get_record"
    
    try:
        # Validate table name
        model = _get_model(table)
        if model is None:
            available_tables = list(set(_normalize_table_name(t) for t in TABLE_REGISTRY.keys()))
            return format_error_response(
                Exception(f"Invalid table '{table}'. Available tables: {sorted(available_tables)}"),
                tool_name
            )
        
        # Get the record
        try:
            instance = model.objects.get(id=record_id)
        except model.DoesNotExist:
            return format_error_response(
                Exception(f"Record with ID {record_id} not found in table '{table}'"),
                tool_name
            )
        
        # Serialize the record
        data = serialize_model_instance(instance)
        
        # Add related counts if requested
        if include_related_counts:
            data = _add_related_counts(instance, data, table)
        
        return format_success_response(
            data=data,
            tool_name=tool_name,
            metadata={
                **get_tool_metadata(tool_name),
                "table": table,
                "record_id": record_id
            }
        )
        
    except Exception as e:
        return format_error_response(e, tool_name)


def query_records(
    table: str,
    filters: Optional[Dict[str, Any]] = None,
    text_search: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    order_by: Optional[str] = None
) -> Dict[str, Any]:
    """
    Query multiple records from any table with optional filters and text search.
    
    WORKFLOW:
    1. First call get_<table>_schema_guide() to understand available fields
    2. Optionally call get_filter_syntax_guide() to understand filter syntax
    3. Then call this tool with appropriate filters/search
    
    Args:
        table: Name of the table (e.g., "company", "accounts", "invoices")
        filters: Optional dict of field filters (e.g., {"country": "USA", "is_active": True})
        text_search: Optional text to search across searchable fields
        page: Page number (1-indexed)
        page_size: Number of results per page (max 100)
        order_by: Field to order by (prefix with - for descending, e.g., "-created_at")
        
    Returns:
        Paginated list of records
        
    Filter Examples:
        {"country": "USA"}
        {"name__icontains": "tech"}
        {"balance__gte": 1000}
        {"status__in": ["pending", "approved"]}
        {"date__range": ["2024-01-01", "2024-12-31"]}
        
    Search Examples:
        text_search="technology" - searches across name, description, etc.
    """
    tool_name = "query_records"
    
    try:
        # Validate table name
        model = _get_model(table)
        if model is None:
            available_tables = list(set(_normalize_table_name(t) for t in TABLE_REGISTRY.keys()))
            return format_error_response(
                Exception(f"Invalid table '{table}'. Available tables: {sorted(available_tables)}"),
                tool_name
            )
        
        # Limit page size
        page_size = min(page_size, 100)
        
        # Start with all records
        queryset = model.objects.all()
        
        # Apply filters
        if filters:
            queryset = apply_filters(queryset, filters)
        
        # Apply text search
        if text_search:
            search_query = _build_search_query(table, text_search)
            if search_query:
                queryset = queryset.filter(search_query)
        
        # Apply ordering
        if order_by:
            queryset = queryset.order_by(order_by)
        elif hasattr(model, '_meta') and model._meta.ordering:
            pass  # Use model's default ordering
        else:
            # Default to most recent first if created_at exists
            if hasattr(model, 'created_at'):
                queryset = queryset.order_by('-created_at')
            else:
                queryset = queryset.order_by('-id')
        
        # Paginate results
        result = paginate_results(queryset, page, page_size)
        
        return format_success_response(
            data=result,
            tool_name=tool_name,
            metadata={
                **get_tool_metadata(tool_name),
                "table": table,
                "filters_applied": filters is not None,
                "search_applied": text_search is not None
            }
        )
        
    except Exception as e:
        return format_error_response(e, tool_name)


def create_record(
    table: str,
    data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Create a new record in any table.
    
    WORKFLOW:
    1. First call get_<table>_schema_guide() to understand required fields
    2. Call get_crud_operation_guide(operation="create") for few-shot examples
    3. Then call this tool with the data
    
    Args:
        table: Name of the table (e.g., "company", "account", "invoice")
        data: Dictionary of field values for the new record
        
    Returns:
        Created record with ID
        
    Example:
        create_record(
            table="company",
            data={
                "name": "Acme Corporation",
                "country": "USA",
                "default_currency": "USD"
            }
        )
    """
    tool_name = "create_record"
    
    try:
        # Validate table name
        model = _get_model(table)
        if model is None:
            available_tables = list(set(_normalize_table_name(t) for t in TABLE_REGISTRY.keys()))
            return format_error_response(
                Exception(f"Invalid table '{table}'. Available tables: {sorted(available_tables)}"),
                tool_name
            )
        
        # Validate data is provided
        if not data:
            return format_error_response(
                Exception("No data provided for creating record"),
                tool_name
            )
        
        # Handle foreign key fields - convert IDs to model instances
        processed_data = _process_foreign_keys(model, data)
        
        # Create the instance
        try:
            instance = model(**processed_data)
            instance.full_clean()  # Validate before saving
            instance.save()
        except ValidationError as ve:
            return format_error_response(
                Exception(f"Validation error: {ve.message_dict}"),
                tool_name
            )
        except TypeError as te:
            return format_error_response(
                Exception(f"Invalid field in data: {str(te)}"),
                tool_name
            )
        
        # Serialize and return created record
        response_data = serialize_model_instance(instance)
        
        return format_success_response(
            data={
                "created": True,
                "id": instance.id,
                "record": response_data
            },
            tool_name=tool_name,
            metadata={
                **get_tool_metadata(tool_name),
                "table": table,
                "created_id": instance.id
            }
        )
        
    except Exception as e:
        return format_error_response(e, tool_name)


def update_record(
    table: str,
    record_id: int,
    data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Update an existing record in any table.
    
    WORKFLOW:
    1. First call get_<table>_schema_guide() to understand available fields
    2. Call get_record() to verify the record exists and see current values
    3. Call get_crud_operation_guide(operation="update") for few-shot examples
    4. Then call this tool with updated data
    
    Args:
        table: Name of the table (e.g., "company", "account", "invoice")
        record_id: The ID of the record to update
        data: Dictionary of field values to update (only include fields to change)
        
    Returns:
        Updated record
        
    Example:
        update_record(
            table="company",
            record_id=5,
            data={
                "name": "New Company Name",
                "country": "Canada"
            }
        )
    """
    tool_name = "update_record"
    
    try:
        # Validate table name
        model = _get_model(table)
        if model is None:
            available_tables = list(set(_normalize_table_name(t) for t in TABLE_REGISTRY.keys()))
            return format_error_response(
                Exception(f"Invalid table '{table}'. Available tables: {sorted(available_tables)}"),
                tool_name
            )
        
        # Validate data is provided
        if not data:
            return format_error_response(
                Exception("No data provided for updating record"),
                tool_name
            )
        
        # Get the existing record
        try:
            instance = model.objects.get(id=record_id)
        except model.DoesNotExist:
            return format_error_response(
                Exception(f"Record with ID {record_id} not found in table '{table}'"),
                tool_name
            )
        
        # Store old values for change tracking
        old_values = {}
        for field in data.keys():
            if hasattr(instance, field):
                old_value = getattr(instance, field)
                if hasattr(old_value, 'id'):  # FK field
                    old_values[field] = old_value.id
                elif hasattr(old_value, 'isoformat'):  # Date/DateTime
                    old_values[field] = old_value.isoformat()
                else:
                    old_values[field] = old_value
        
        # Handle foreign key fields
        processed_data = _process_foreign_keys(model, data)
        
        # Update fields
        try:
            for field, value in processed_data.items():
                if hasattr(instance, field):
                    setattr(instance, field, value)
            
            instance.full_clean()  # Validate before saving
            instance.save()
        except ValidationError as ve:
            return format_error_response(
                Exception(f"Validation error: {ve.message_dict}"),
                tool_name
            )
        
        # Serialize and return updated record
        response_data = serialize_model_instance(instance)
        
        return format_success_response(
            data={
                "updated": True,
                "id": instance.id,
                "record": response_data,
                "changes": {
                    "old_values": old_values,
                    "new_values": {k: response_data.get(k) for k in data.keys()}
                }
            },
            tool_name=tool_name,
            metadata={
                **get_tool_metadata(tool_name),
                "table": table,
                "updated_id": instance.id
            }
        )
        
    except Exception as e:
        return format_error_response(e, tool_name)


def delete_record(
    table: str,
    record_id: int,
    confirm: bool = False
) -> Dict[str, Any]:
    """
    Delete a record from any table.
    
    WORKFLOW:
    1. First call get_<table>_schema_guide() to understand relationships
    2. Call get_record() to verify the record and check dependencies
    3. Call get_crud_operation_guide(operation="delete") for few-shot examples
    4. Then call this tool with confirm=True
    
    Args:
        table: Name of the table (e.g., "company", "account", "invoice")
        record_id: The ID of the record to delete
        confirm: Must be True to actually delete (safety check)
        
    Returns:
        Deletion confirmation
        
    Example:
        delete_record(table="invoice", record_id=123, confirm=True)
    """
    tool_name = "delete_record"
    
    try:
        # Validate table name
        model = _get_model(table)
        if model is None:
            available_tables = list(set(_normalize_table_name(t) for t in TABLE_REGISTRY.keys()))
            return format_error_response(
                Exception(f"Invalid table '{table}'. Available tables: {sorted(available_tables)}"),
                tool_name
            )
        
        # Safety check
        if not confirm:
            return format_error_response(
                Exception("Delete not confirmed. Set confirm=True to delete the record."),
                tool_name
            )
        
        # Get the existing record
        try:
            instance = model.objects.get(id=record_id)
        except model.DoesNotExist:
            return format_error_response(
                Exception(f"Record with ID {record_id} not found in table '{table}'"),
                tool_name
            )
        
        # Store record data before deletion
        deleted_data = serialize_model_instance(instance)
        
        # Check for protected relationships before deleting
        # This will raise ProtectedError if there are related objects
        try:
            instance.delete()
        except Exception as delete_error:
            if "ProtectedError" in str(type(delete_error)):
                return format_error_response(
                    Exception(f"Cannot delete: Record has protected related objects. {str(delete_error)}"),
                    tool_name
                )
            raise
        
        return format_success_response(
            data={
                "deleted": True,
                "id": record_id,
                "deleted_record": deleted_data
            },
            tool_name=tool_name,
            metadata={
                **get_tool_metadata(tool_name),
                "table": table,
                "deleted_id": record_id
            }
        )
        
    except Exception as e:
        return format_error_response(e, tool_name)


def _process_foreign_keys(model, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process foreign key fields - convert IDs to model instances
    
    Args:
        model: Django model class
        data: Dictionary of field values
        
    Returns:
        Processed data with FK instances
    """
    from django.db.models import ForeignKey
    
    processed = {}
    
    for field in model._meta.fields:
        if field.name in data:
            value = data[field.name]
            
            if isinstance(field, ForeignKey) and value is not None:
                # Convert ID to model instance
                if isinstance(value, int):
                    related_model = field.related_model
                    try:
                        processed[field.name] = related_model.objects.get(id=value)
                    except related_model.DoesNotExist:
                        raise ValueError(f"Related {related_model.__name__} with ID {value} not found")
                else:
                    processed[field.name] = value
            else:
                processed[field.name] = value
    
    # Include any remaining fields that might be valid
    for key, value in data.items():
        if key not in processed and hasattr(model, key):
            processed[key] = value
    
    return processed


def list_available_tables() -> Dict[str, Any]:
    """
    List all available tables that can be queried.
    
    Returns:
        List of available table names with descriptions
    """
    tool_name = "list_available_tables"
    
    # Get unique table names (singular form)
    tables = {}
    for name, model in TABLE_REGISTRY.items():
        normalized = _normalize_table_name(name)
        if normalized not in tables:
            tables[normalized] = {
                "model": model.__name__,
                "description": model.__doc__ or f"{model.__name__} table",
                "has_search": bool(SEARCH_FIELDS.get(normalized)),
                "search_fields": SEARCH_FIELDS.get(normalized, [])
            }
    
    return format_success_response(
        data={
            "total_tables": len(tables),
            "tables": dict(sorted(tables.items()))
        },
        tool_name=tool_name,
        metadata=get_tool_metadata(tool_name)
    )
