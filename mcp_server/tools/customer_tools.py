"""
Customer Tools for MCP Server
Micro-tools for querying Customer data
"""
from typing import Dict, Any, Optional
from finance.models import Customer
from utils.helpers import (
    format_success_response,
    format_error_response,
    serialize_queryset,
    serialize_model_instance,
    paginate_results,
    get_tool_metadata,
    apply_filters
)


def list_customers(filters: Optional[Dict[str, Any]] = None, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
    """
    List all customers with optional dynamic filtering
    
    Args:
        filters: Optional dict of filters (e.g., {"gst_category": "registered", "country": "USA"})
        page: Page number (1-indexed)
        page_size: Number of results per page
        
    Example filters:
        {"country": "USA"}
        {"gst_category": "registered"}
        {"customer_type": "company"}
        {"company__id": 5}
    """
    tool_name = "list_customers"
    try:
        customers = Customer.objects.select_related('company')
        customers = apply_filters(customers, filters)
        customers = customers.order_by('-created_at')
        result = paginate_results(customers, page, page_size)
        
        return format_success_response(data=result, tool_name=tool_name, metadata=get_tool_metadata(tool_name))
    except Exception as e:
        return format_error_response(e, tool_name)


def get_customer(customer_id: int) -> Dict[str, Any]:
    """
    Get detailed information about a specific customer
    
    Args:
        customer_id: The ID of the customer
        
    Returns:
        Customer details with related information
    """
    tool_name = "get_customer"
    try:
        customer = Customer.objects.select_related('company').get(id=customer_id)
        data = serialize_model_instance(customer)
        
        # Add related info
        data['company_name'] = customer.company.name if customer.company else None
        data['total_invoices'] = customer.invoices.count()
        
        return format_success_response(data=data, tool_name=tool_name, metadata=get_tool_metadata(tool_name))
    except Customer.DoesNotExist:
        return format_error_response(Exception(f"Customer with ID {customer_id} not found"), tool_name)
    except Exception as e:
        return format_error_response(e, tool_name)


def search_customers(query: str, filters: Optional[Dict[str, Any]] = None, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
    """
    Search customers by name or GSTIN with optional additional filters
    
    Args:
        query: Search query string
        filters: Optional dict of additional filters (e.g., {"country": "USA"})
        page: Page number (1-indexed)
        page_size: Number of results per page
        
    Example:
        search_customers("acme", {"gst_category": "registered", "country": "USA"})
    """
    tool_name = "search_customers"
    try:
        from django.db.models import Q
        
        customers = Customer.objects.filter(
            Q(name__icontains=query) |
            Q(gstin_uin__icontains=query)
        ).select_related('company')
        customers = apply_filters(customers, filters)
        customers = customers.order_by('-created_at')
        
        result = paginate_results(customers, page, page_size)
        
        return format_success_response(
            data=result,
            tool_name=tool_name,
            metadata={**get_tool_metadata(tool_name), "search_query": query}
        )
    except Exception as e:
        return format_error_response(e, tool_name)
