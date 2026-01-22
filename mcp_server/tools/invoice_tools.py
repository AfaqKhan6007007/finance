"""
Invoice Tools for MCP Server
Micro-tools for querying Invoice data
"""
from typing import Dict, Any, Optional
from finance.models import Invoice
from mcp_server.utils import (
    format_success_response,
    format_error_response,
    serialize_queryset,
    serialize_model_instance,
    paginate_results,
    get_tool_metadata,
    apply_filters
)


def list_invoices(filters: Optional[Dict[str, Any]] = None, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
    """
    List all invoices with optional dynamic filtering
    
    Args:
        filters: Optional dict of filters (e.g., {"status": "paid", "total_amount__gte": 1000})
        page: Page number (1-indexed)
        page_size: Number of results per page
        
    Example filters:
        {"status": "paid"}
        {"total_amount__gte": 5000}
        {"date__range": ["2025-01-01", "2025-12-31"]}
        {"supplier__country": "USA"}
    """
    tool_name = "list_invoices"
    try:
        invoices = Invoice.objects.select_related('supplier', 'customer', 'company')
        invoices = apply_filters(invoices, filters)
        invoices = invoices.order_by('-date')
        result = paginate_results(invoices, page, page_size)
        
        return format_success_response(data=result, tool_name=tool_name, metadata=get_tool_metadata(tool_name))
    except Exception as e:
        return format_error_response(e, tool_name)


def get_invoice(invoice_id: int) -> Dict[str, Any]:
    """
    Get detailed information about a specific invoice
    
    Args:
        invoice_id: The ID of the invoice
        
    Returns:
        Invoice details with related information
    """
    tool_name = "get_invoice"
    try:
        invoice = Invoice.objects.select_related('supplier', 'customer', 'company').get(id=invoice_id)
        data = serialize_model_instance(invoice)
        
        # Add related info
        data['supplier_name'] = invoice.supplier.name if invoice.supplier else None
        data['customer_name'] = invoice.customer.name if invoice.customer else None
        data['company_name'] = invoice.company.name if invoice.company else None
        
        return format_success_response(data=data, tool_name=tool_name, metadata=get_tool_metadata(tool_name))
    except Invoice.DoesNotExist:
        return format_error_response(Exception(f"Invoice with ID {invoice_id} not found"), tool_name)
    except Exception as e:
        return format_error_response(e, tool_name)


def search_invoices(query: str, filters: Optional[Dict[str, Any]] = None, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
    """
    Search invoices by invoice number or ID with optional additional filters
    
    Args:
        query: Search query string
        filters: Optional dict of additional filters (e.g., {"status": "paid"})
        page: Page number (1-indexed)
        page_size: Number of results per page
        
    Example:
        search_invoices("INV-2025", {"status": "paid", "total_amount__gte": 1000})
    """
    tool_name = "search_invoices"
    try:
        from django.db.models import Q
        
        invoices = Invoice.objects.filter(
            Q(invoice_number__icontains=query) |
            Q(invoice_id__icontains=query)
        ).select_related('supplier', 'customer', 'company')
        invoices = apply_filters(invoices, filters)
        invoices = invoices.order_by('-date')
        
        result = paginate_results(invoices, page, page_size)
        
        return format_success_response(
            data=result,
            tool_name=tool_name,
            metadata={**get_tool_metadata(tool_name), "search_query": query}
        )
    except Exception as e:
        return format_error_response(e, tool_name)


def get_invoice_stats(filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Get invoice statistics with optional filtering
    
    Args:
        filters: Optional dict of filters (e.g., {"status": "paid", "date__year": 2025})
        
    Returns:
        Statistics: total count, total amount, by status breakdown
    """
    tool_name = "get_invoice_stats"
    try:
        from django.db.models import Sum, Count
        
        queryset = Invoice.objects.all()
        queryset = apply_filters(queryset, filters)
        
        total_count = queryset.count()
        total_amount = queryset.aggregate(total=Sum('total_amount'))['total'] or 0
        total_vat = queryset.aggregate(total=Sum('total_vat'))['total'] or 0
        
        # Breakdown by status
        by_status = {}
        for status_code, status_name in Invoice.STATUS_CHOICES:
            status_queryset = queryset.filter(status=status_code)
            by_status[status_name] = {
                "count": status_queryset.count(),
                "total_amount": float(status_queryset.aggregate(total=Sum('total_amount'))['total'] or 0)
            }
        
        data = {
            "total_invoices": total_count,
            "total_amount": float(total_amount),
            "total_vat": float(total_vat),
            "by_status": by_status,
            "filters_applied": filters or {}
        }
        
        return format_success_response(data=data, tool_name=tool_name, metadata=get_tool_metadata(tool_name))
    except Exception as e:
        return format_error_response(e, tool_name)
