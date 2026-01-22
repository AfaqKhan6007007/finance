"""
Cost Center Tools for MCP Server
Micro-tools for querying Cost Center data
"""
from typing import Dict, Any, Optional
from finance.models import CostCenter
from mcp_server.utils import (
    format_success_response,
    format_error_response,
    serialize_queryset,
    serialize_model_instance,
    paginate_results,
    get_tool_metadata,
    apply_filters
)


def list_cost_centers(filters: Optional[Dict[str, Any]] = None, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
    """
    List all cost centers with optional dynamic filtering
    
    Args:
        filters: Optional dict of filters (e.g., {"is_group": False, "is_disabled": False})
        page: Page number (1-indexed)
        page_size: Number of results per page
        
    Example filters:
        {"is_group": False}
        {"is_disabled": False}
        {"company__id": 5}
        {"parent__isnull": True}  # Top-level cost centers
    """
    tool_name = "list_cost_centers"
    try:
        cost_centers = CostCenter.objects.select_related('company', 'parent')
        cost_centers = apply_filters(cost_centers, filters)
        cost_centers = cost_centers.order_by('name')
        result = paginate_results(cost_centers, page, page_size)
        
        return format_success_response(data=result, tool_name=tool_name, metadata=get_tool_metadata(tool_name))
    except Exception as e:
        return format_error_response(e, tool_name)


def get_cost_center(cost_center_id: int) -> Dict[str, Any]:
    """
    Get detailed information about a specific cost center
    
    Args:
        cost_center_id: The ID of the cost center
        
    Returns:
        Cost center details with related information
    """
    tool_name = "get_cost_center"
    try:
        cost_center = CostCenter.objects.select_related('company', 'parent').get(id=cost_center_id)
        data = serialize_model_instance(cost_center)
        
        # Add related info
        data['company_name'] = cost_center.company.name if cost_center.company else None
        data['parent_name'] = cost_center.parent.name if cost_center.parent else None
        data['children_count'] = cost_center.children.count()
        
        return format_success_response(data=data, tool_name=tool_name, metadata=get_tool_metadata(tool_name))
    except CostCenter.DoesNotExist:
        return format_error_response(Exception(f"Cost center with ID {cost_center_id} not found"), tool_name)
    except Exception as e:
        return format_error_response(e, tool_name)


def search_cost_centers(query: str, filters: Optional[Dict[str, Any]] = None, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
    """
    Search cost centers by name or number with optional additional filters
    
    Args:
        query: Search query string
        filters: Optional dict of additional filters
        page: Page number (1-indexed)
        page_size: Number of results per page
        
    Example:
        search_cost_centers("marketing", {"is_disabled": False})
    """
    tool_name = "search_cost_centers"
    try:
        from django.db.models import Q
        
        cost_centers = CostCenter.objects.filter(
            Q(name__icontains=query) |
            Q(cost_center_number__icontains=query)
        ).select_related('company', 'parent')
        cost_centers = apply_filters(cost_centers, filters)
        cost_centers = cost_centers.order_by('name')
        
        result = paginate_results(cost_centers, page, page_size)
        
        return format_success_response(
            data=result,
            tool_name=tool_name,
            metadata={**get_tool_metadata(tool_name), "search_query": query}
        )
    except Exception as e:
        return format_error_response(e, tool_name)
