"""
Supplier Tools for MCP Server
Micro-tools for querying Supplier data
"""
from typing import Dict, Any, Optional
from finance.models import Supplier
from mcp_server.utils import (
    format_success_response,
    format_error_response,
    serialize_queryset,
    serialize_model_instance,
    paginate_results,
    get_tool_metadata,
    apply_filters
)


def list_suppliers(filters: Optional[Dict[str, Any]] = None, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
    """
    List all suppliers with optional dynamic filtering
    
    Args:
        filters: Optional dict of filters (e.g., {"gst_category": "registered", "country": "India"})
        page: Page number (1-indexed)
        page_size: Number of results per page
        
    Example filters:
        {"country": "India"}
        {"gst_category": "registered"}
        {"supplier_type": "company"}
        {"company__id": 5}
    """
    tool_name = "list_suppliers"
    try:
        suppliers = Supplier.objects.select_related('company')
        suppliers = apply_filters(suppliers, filters)
        suppliers = suppliers.order_by('-created_at')
        result = paginate_results(suppliers, page, page_size)
        
        return format_success_response(data=result, tool_name=tool_name, metadata=get_tool_metadata(tool_name))
    except Exception as e:
        return format_error_response(e, tool_name)


def get_supplier(supplier_id: int) -> Dict[str, Any]:
    """
    Get detailed information about a specific supplier
    
    Args:
        supplier_id: The ID of the supplier
        
    Returns:
        Supplier details with related information
    """
    tool_name = "get_supplier"
    try:
        supplier = Supplier.objects.select_related('company').get(id=supplier_id)
        data = serialize_model_instance(supplier)
        
        # Add related info
        data['company_name'] = supplier.company.name if supplier.company else None
        data['total_invoices'] = supplier.invoices.count()
        
        return format_success_response(data=data, tool_name=tool_name, metadata=get_tool_metadata(tool_name))
    except Supplier.DoesNotExist:
        return format_error_response(Exception(f"Supplier with ID {supplier_id} not found"), tool_name)
    except Exception as e:
        return format_error_response(e, tool_name)


def search_suppliers(query: str, filters: Optional[Dict[str, Any]] = None, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
    """
    Search suppliers by name or GSTIN with optional additional filters
    
    Args:
        query: Search query string
        filters: Optional dict of additional filters (e.g., {"country": "India"})
        page: Page number (1-indexed)
        page_size: Number of results per page
        
    Example:
        search_suppliers("tech", {"gst_category": "registered", "country": "India"})
    """
    tool_name = "search_suppliers"
    try:
        from django.db.models import Q
        
        suppliers = Supplier.objects.filter(
            Q(name__icontains=query) |
            Q(gstin_uin__icontains=query)
        ).select_related('company')
        suppliers = apply_filters(suppliers, filters)
        suppliers = suppliers.order_by('-created_at')
        
        result = paginate_results(suppliers, page, page_size)
        
        return format_success_response(
            data=result,
            tool_name=tool_name,
            metadata={**get_tool_metadata(tool_name), "search_query": query}
        )
    except Exception as e:
        return format_error_response(e, tool_name)
