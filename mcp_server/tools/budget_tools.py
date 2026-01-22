"""
Budget Tools for MCP Server
Micro-tools for querying Budget data
"""
from typing import Dict, Any, Optional
from finance.models import Budget
from mcp_server.utils import (
    format_success_response,
    format_error_response,
    serialize_queryset,
    serialize_model_instance,
    paginate_results,
    get_tool_metadata,
    apply_filters
)


def list_budgets(filters: Optional[Dict[str, Any]] = None, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
    """
    List all budgets with optional dynamic filtering
    
    Args:
        filters: Optional dict of filters (e.g., {"fiscal_year_from": "2025-2026"})
        page: Page number (1-indexed)
        page_size: Number of results per page
        
    Example filters:
        {"fiscal_year_from": "2025-2026"}
        {"budget_against": "cost_center"}
        {"company__id": 5}
    """
    tool_name = "list_budgets"
    try:
        budgets = Budget.objects.select_related('company', 'cost_center')
        budgets = apply_filters(budgets, filters)
        budgets = budgets.order_by('-created_at')
        result = paginate_results(budgets, page, page_size)
        
        return format_success_response(data=result, tool_name=tool_name, metadata=get_tool_metadata(tool_name))
    except Exception as e:
        return format_error_response(e, tool_name)


def get_budget(budget_id: int) -> Dict[str, Any]:
    """
    Get detailed information about a specific budget
    
    Args:
        budget_id: The ID of the budget
        
    Returns:
        Budget details with related information
    """
    tool_name = "get_budget"
    try:
        budget = Budget.objects.select_related('company', 'cost_center').get(id=budget_id)
        data = serialize_model_instance(budget)
        
        # Add related info
        data['company_name'] = budget.company.name if budget.company else None
        data['cost_center_name'] = budget.cost_center.name if budget.cost_center else None
        
        return format_success_response(data=data, tool_name=tool_name, metadata=get_tool_metadata(tool_name))
    except Budget.DoesNotExist:
        return format_error_response(Exception(f"Budget with ID {budget_id} not found"), tool_name)
    except Exception as e:
        return format_error_response(e, tool_name)


def search_budgets(query: str, filters: Optional[Dict[str, Any]] = None, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
    """
    Search budgets by series with optional additional filters
    
    Args:
        query: Search query string
        filters: Optional dict of additional filters
        page: Page number (1-indexed)
        page_size: Number of results per page
        
    Example:
        search_budgets("2025", {"budget_against": "cost_center"})
    """
    tool_name = "search_budgets"
    try:
        from django.db.models import Q
        
        budgets = Budget.objects.filter(
            Q(series__icontains=query)
        ).select_related('company', 'cost_center')
        budgets = apply_filters(budgets, filters)
        budgets = budgets.order_by('-created_at')
        
        result = paginate_results(budgets, page, page_size)
        
        return format_success_response(
            data=result,
            tool_name=tool_name,
            metadata={**get_tool_metadata(tool_name), "search_query": query}
        )
    except Exception as e:
        return format_error_response(e, tool_name)
