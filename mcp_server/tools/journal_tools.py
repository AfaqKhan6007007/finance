"""
Journal Entry Tools for MCP Server
Micro-tools for querying Journal Entry data
"""
from typing import Dict, Any, Optional
from finance.models import JournalEntry
from mcp_server.utils import (
    format_success_response,
    format_error_response,
    serialize_queryset,
    serialize_model_instance,
    paginate_results,
    get_tool_metadata,
    apply_filters
)


def list_journal_entries(filters: Optional[Dict[str, Any]] = None, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
    """
    List all journal entries with optional dynamic filtering
    
    Args:
        filters: Optional dict of filters (e.g., {"date__year": 2025, "debit_amount__gte": 1000})
        page: Page number (1-indexed)
        page_size: Number of results per page
        
    Example filters:
        {"date__range": ["2025-01-01", "2025-12-31"]}
        {"debit_amount__gte": 1000}
        {"account__account_type": "Asset"}
        {"company__id": 5}
    """
    tool_name = "list_journal_entries"
    try:
        entries = JournalEntry.objects.select_related('account', 'company')
        entries = apply_filters(entries, filters)
        entries = entries.order_by('-date', '-created_at')
        result = paginate_results(entries, page, page_size)
        
        return format_success_response(data=result, tool_name=tool_name, metadata=get_tool_metadata(tool_name))
    except Exception as e:
        return format_error_response(e, tool_name)


def get_journal_entry(entry_id: int) -> Dict[str, Any]:
    """
    Get detailed information about a specific journal entry
    
    Args:
        entry_id: The ID of the journal entry
        
    Returns:
        Journal entry details with related information
    """
    tool_name = "get_journal_entry"
    try:
        entry = JournalEntry.objects.select_related('account', 'company').get(id=entry_id)
        data = serialize_model_instance(entry)
        
        # Add related info
        data['account_name'] = entry.account.name if entry.account else None
        data['account_number'] = entry.account.account_number if entry.account else None
        data['company_name'] = entry.company.name if entry.company else None
        
        return format_success_response(data=data, tool_name=tool_name, metadata=get_tool_metadata(tool_name))
    except JournalEntry.DoesNotExist:
        return format_error_response(Exception(f"Journal entry with ID {entry_id} not found"), tool_name)
    except Exception as e:
        return format_error_response(e, tool_name)


def search_journal_entries(query: str, filters: Optional[Dict[str, Any]] = None, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
    """
    Search journal entries by entry number or description with optional additional filters
    
    Args:
        query: Search query string
        filters: Optional dict of additional filters (e.g., {"date__year": 2025})
        page: Page number (1-indexed)
        page_size: Number of results per page
        
    Example:
        search_journal_entries("JE-2025", {"debit_amount__gte": 1000})
    """
    tool_name = "search_journal_entries"
    try:
        from django.db.models import Q
        
        entries = JournalEntry.objects.filter(
            Q(entry_number__icontains=query) |
            Q(description__icontains=query)
        ).select_related('account', 'company')
        entries = apply_filters(entries, filters)
        entries = entries.order_by('-date')
        
        result = paginate_results(entries, page, page_size)
        
        return format_success_response(
            data=result,
            tool_name=tool_name,
            metadata={**get_tool_metadata(tool_name), "search_query": query}
        )
    except Exception as e:
        return format_error_response(e, tool_name)


def get_journal_stats(filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Get journal entry statistics with optional filtering
    
    Args:
        filters: Optional dict of filters (e.g., {"date__year": 2025, "account__account_type": "Asset"})
        
    Returns:
        Statistics: total entries, total debits, total credits, balance
    """
    tool_name = "get_journal_stats"
    try:
        from django.db.models import Sum
        
        queryset = JournalEntry.objects.all()
        queryset = apply_filters(queryset, filters)
        
        total_count = queryset.count()
        total_debits = queryset.aggregate(total=Sum('debit_amount'))['total'] or 0
        total_credits = queryset.aggregate(total=Sum('credit_amount'))['total'] or 0
        
        data = {
            "total_entries": total_count,
            "total_debits": float(total_debits),
            "total_credits": float(total_credits),
            "balance": float(total_debits - total_credits),
            "is_balanced": abs(total_debits - total_credits) < 0.01,  # Account for rounding
            "filters_applied": filters or {}
        }
        
        return format_success_response(data=data, tool_name=tool_name, metadata=get_tool_metadata(tool_name))
    except Exception as e:
        return format_error_response(e, tool_name)
