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
    Update a SINGLE existing record in any table.
    
    ⚠️ CRITICAL RESTRICTION:
    - ONLY ONE RECORD AT A TIME - Never batch update
    - Must confirm record ID with user before updating
    
    WORKFLOW:
    1. Call get_<table>_schema_guide() to understand available fields
    2. Call get_record() to verify the record exists and show current values to user
    3. Confirm with user which SINGLE record to update
    4. Call get_crud_operation_guide(operation="update") for few-shot examples
    5. Then call this tool with updated data for ONE record only
    
    Args:
        table: Name of the table (e.g., "company", "account", "invoice")
        record_id: The ID of the SINGLE record to update (must be integer, NOT list)
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
        # CRITICAL: Validate single record only
        if isinstance(record_id, (list, tuple)):
            return format_error_response(
                Exception("CRITICAL ERROR: Cannot update multiple records at once. Only ONE record ID allowed. Never batch update."),
                tool_name
            )
        
        if not isinstance(record_id, int):
            return format_error_response(
                Exception(f"CRITICAL ERROR: record_id must be a single integer, got {type(record_id).__name__}"),
                tool_name
            )
        
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


def check_referential_integrity(
    table: str,
    record_id: int
) -> Dict[str, Any]:
    """
    Check if a record is referenced by other tables as a foreign key.
    This ensures referential integrity before deletion.
    
    Args:
        table: Name of the table (e.g., "company", "account")
        record_id: The ID of the record to check
        
    Returns:
        Dict with 'has_dependencies' boolean and 'dependencies' list
        
    Example:
        {
            "has_dependencies": True,
            "dependencies": [
                {"table": "account", "count": 5, "field": "company"},
                {"table": "invoice", "count": 12, "field": "company"}
            ]
        }
    """
    tool_name = "check_referential_integrity"
    
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
        
        # Check all related objects (reverse FK relationships)
        dependencies = []
        
        # Get all reverse FK relationships
        for related_object in instance._meta.related_objects:
            related_name = related_object.get_accessor_name()
            related_model_name = related_object.related_model._meta.model_name
            field_name = related_object.field.name
            
            # Count related objects
            related_manager = getattr(instance, related_name)
            count = related_manager.count()
            
            if count > 0:
                # Get sample IDs (first 5)
                sample_ids = list(related_manager.values_list('id', flat=True)[:5])
                
                dependencies.append({
                    "table": related_model_name,
                    "count": count,
                    "field": field_name,
                    "sample_ids": sample_ids,
                    "message": f"{count} {related_model_name} record(s) reference this {table}"
                })
        
        has_dependencies = len(dependencies) > 0
        
        return format_success_response(
            data={
                "has_dependencies": has_dependencies,
                "dependencies": dependencies,
                "record_id": record_id,
                "table": table,
                "can_delete": not has_dependencies
            },
            tool_name=tool_name,
            metadata=get_tool_metadata(tool_name)
        )
        
    except Exception as e:
        return format_error_response(e, tool_name)


def delete_record(
    table: str,
    record_id: int,
    confirm: bool = False
) -> Dict[str, Any]:
    """
    Delete a SINGLE record from any table.
    
    ⚠️ CRITICAL RESTRICTIONS:
    - ONLY ONE RECORD AT A TIME - Never batch delete
    - Must check referential integrity BEFORE deletion
    - If dependencies exist, deletion is BLOCKED
    
    WORKFLOW:
    1. Call get_<table>_schema_guide() to understand the table
    2. Call get_record() to verify the record exists
    3. Call check_referential_integrity() to check for dependencies
    4. If has_dependencies=True, STOP and show user the dependent records
    5. Only if has_dependencies=False, call this tool with confirm=True
    
    Args:
        table: Name of the table (e.g., "company", "account", "invoice")
        record_id: The ID of the SINGLE record to delete (must be integer, NOT list)
        confirm: Must be True to actually delete (safety check)
        
    Returns:
        Deletion confirmation or error if dependencies exist
        
    Example:
        delete_record(table="invoice", record_id=123, confirm=True)
    """
    tool_name = "delete_record"
    
    try:
        # CRITICAL: Validate single record only
        if isinstance(record_id, (list, tuple)):
            return format_error_response(
                Exception("CRITICAL ERROR: Cannot delete multiple records at once. Only ONE record ID allowed. Never batch delete."),
                tool_name
            )
        
        if not isinstance(record_id, int):
            return format_error_response(
                Exception(f"CRITICAL ERROR: record_id must be a single integer, got {type(record_id).__name__}"),
                tool_name
            )
        
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
        
        # CRITICAL: Check referential integrity BEFORE deletion
        integrity_check = check_referential_integrity(table, record_id)
        
        if integrity_check.get('success') and integrity_check['data'].get('has_dependencies'):
            dependencies = integrity_check['data']['dependencies']
            dep_summary = []
            for dep in dependencies:
                dep_summary.append(f"- {dep['count']} {dep['table']} record(s) via field '{dep['field']}' (IDs: {dep['sample_ids']})")
            
            error_msg = (
                f"DELETION BLOCKED: Cannot delete {table} ID {record_id} due to referential integrity constraints.\n"
                f"The following records depend on it:\n" + "\n".join(dep_summary) + "\n\n"
                f"You must first delete or update these dependent records before deleting this {table}."
            )
            
            return format_error_response(
                Exception(error_msg),
                tool_name
            )
        
        # Store record data before deletion
        deleted_data = serialize_model_instance(instance)
        
        # Perform deletion
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


def validate_required_fields(
    table: str,
    provided_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Validate if all required fields are provided for creating a record.
    
    CRITICAL: Call this BEFORE create_record to check if user provided all mandatory fields.
    If missing fields, display them to user and ask for the information.
    
    Args:
        table: Name of the table (e.g., "company", "account")
        provided_data: Dictionary of field values user wants to create
        
    Returns:
        Validation result with:
        - is_valid: True if all required fields provided
        - missing_required_fields: List of missing required fields
        - missing_foreign_keys: List of missing FK fields
        - provided_fields: List of fields user provided
        
    Example:
        validate_required_fields(
            table="account",
            provided_data={"name": "Cash"}
        )
        
        Returns:
        {
            "is_valid": False,
            "missing_required_fields": ["company", "account_type"],
            "missing_foreign_keys": ["company"],
            "provided_fields": ["name"],
            "required_fields_info": {
                "company": "Foreign key to Company table (required)",
                "account_type": "Choice field: asset/liability/equity/income/expense (required)"
            }
        }
    """
    tool_name = "validate_required_fields"
    
    try:
        # Get model
        model = _get_model(table)
        if model is None:
            return format_error_response(
                Exception(f"Invalid table '{table}'"),
                tool_name
            )
        
        # Get all required fields (excluding auto fields like id, created_at, updated_at)
        required_fields = []
        required_field_info = {}
        missing_fks = []
        
        for field in model._meta.fields:
            # Skip auto fields
            if field.auto_created or field.name in ['id', 'created_at', 'updated_at']:
                continue
            
            # Check if field is required (not nullable and no default)
            is_required = not field.null and not field.has_default()
            
            if is_required:
                required_fields.append(field.name)
                
                # Build description
                desc_parts = []
                if field.is_relation:
                    related_model = field.related_model.__name__
                    desc_parts.append(f"Foreign key to {related_model} table")
                    if field.name not in provided_data:
                        missing_fks.append(field.name)
                elif field.choices:
                    choices_str = "/".join([c[0] for c in field.choices])
                    desc_parts.append(f"Choice field: {choices_str}")
                else:
                    desc_parts.append(f"{field.get_internal_type()}")
                    if hasattr(field, 'max_length') and field.max_length:
                        desc_parts.append(f"max {field.max_length} chars")
                
                desc_parts.append("(required)")
                required_field_info[field.name] = " ".join(desc_parts)
        
        # Check which required fields are missing
        provided_fields = list(provided_data.keys())
        missing_fields = [f for f in required_fields if f not in provided_data]
        
        is_valid = len(missing_fields) == 0
        
        return format_success_response(
            data={
                "is_valid": is_valid,
                "table": table,
                "required_fields": required_fields,
                "provided_fields": provided_fields,
                "missing_required_fields": missing_fields,
                "missing_foreign_keys": missing_fks,
                "required_fields_info": required_field_info,
                "validation_message": "All required fields provided!" if is_valid else f"Missing {len(missing_fields)} required field(s)"
            },
            tool_name=tool_name,
            metadata={
                **get_tool_metadata(tool_name),
                "table": table
            }
        )
        
    except Exception as e:
        return format_error_response(e, tool_name)


def list_foreign_key_options(
    table: str,
    foreign_key_field: str,
    page: int = 1,
    page_size: int = 10
) -> Dict[str, Any]:
    """
    List available records from a foreign key related table for selection.
    
    CRITICAL: When creating a record that requires a FK, call this to show user the available options.
    User can then select from the list by name/ID.
    
    Args:
        table: Name of the table being created (e.g., "account")
        foreign_key_field: Name of the FK field (e.g., "company")
        page: Page number for pagination (default 1)
        page_size: Records per page (default 10, max 50)
        
    Returns:
        List of available records from the related table with ID and display name
        
    Example:
        list_foreign_key_options(
            table="account",
            foreign_key_field="company"
        )
        
        Returns:
        {
            "foreign_key_field": "company",
            "related_table": "Company",
            "options": [
                {"id": 1, "display": "Global Corp International"},
                {"id": 2, "display": "TechCorp Solutions USA"},
                {"id": 3, "display": "SmartTech Industries"}
            ],
            "total": 5,
            "page": 1,
            "instruction": "User should select one of these options by name or ID"
        }
    """
    tool_name = "list_foreign_key_options"
    
    try:
        # Get model
        model = _get_model(table)
        if model is None:
            return format_error_response(
                Exception(f"Invalid table '{table}'"),
                tool_name
            )
        
        # Find the FK field
        fk_field = None
        for field in model._meta.fields:
            if field.name == foreign_key_field and field.is_relation:
                fk_field = field
                break
        
        if not fk_field:
            return format_error_response(
                Exception(f"Field '{foreign_key_field}' is not a foreign key in table '{table}'"),
                tool_name
            )
        
        # Get the related model
        related_model = fk_field.related_model
        related_table_name = related_model.__name__
        
        # Query all records from related table
        queryset = related_model.objects.all()
        total = queryset.count()
        
        # Paginate
        page_size = min(page_size, 50)  # Max 50
        start = (page - 1) * page_size
        end = start + page_size
        
        records = queryset[start:end]
        
        # Build options list with ID and display name
        options = []
        for record in records:
            display_name = str(record)  # Uses __str__ method
            options.append({
                "id": record.pk,
                "display": display_name
            })
        
        return format_success_response(
            data={
                "foreign_key_field": foreign_key_field,
                "related_table": related_table_name,
                "related_table_normalized": _normalize_table_name(related_table_name),
                "options": options,
                "total": total,
                "page": page,
                "page_size": page_size,
                "has_more": end < total,
                "instruction": f"User should select one of these {related_table_name} records by name or ID. Use the ID value in the '{foreign_key_field}' field when creating the record."
            },
            tool_name=tool_name,
            metadata={
                **get_tool_metadata(tool_name),
                "table": table,
                "foreign_key_field": foreign_key_field
            }
        )
        
    except Exception as e:
        return format_error_response(e, tool_name)

