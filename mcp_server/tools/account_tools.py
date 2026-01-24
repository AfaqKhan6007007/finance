"""
Account Tools for MCP Server
Micro-tools for querying Chart of Accounts data
"""
from typing import Dict, Any, Optional
from finance.models import Account
from utils.helpers import (
    format_success_response,
    format_error_response,
    serialize_queryset,
    serialize_model_instance,
    paginate_results,
    get_tool_metadata,
    apply_filters
)


def list_accounts(filters: Optional[Dict[str, Any]] = None, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
    """
    List all accounts with optional dynamic filtering
    
    Args:
        filters: Optional dict of filters (e.g., {"account_type": "Asset", "is_active": True})
        page: Page number (1-indexed)
        page_size: Number of results per page
        
    Example filters:
        {"account_type": "Asset"}
        {"balance__gte": 1000}
        {"company__id": 5}
        {"is_group": False, "account_type": "Liability"}
    """
    tool_name = "list_accounts"
    try:
        accounts = Account.objects.select_related('company', 'parent_account')
        accounts = apply_filters(accounts, filters)
        accounts = accounts.order_by('company', 'account_number')
        result = paginate_results(accounts, page, page_size)
        
        return format_success_response(data=result, tool_name=tool_name, metadata=get_tool_metadata(tool_name))
    except Exception as e:
        return format_error_response(e, tool_name)


def get_account(account_id: int) -> Dict[str, Any]:
    """Get detailed information about a specific account"""
    tool_name = "get_account"
    try:
        account = Account.objects.select_related('company', 'parent_account').get(id=account_id)
        data = serialize_model_instance(account)
        
        # Add related info
        data['company_name'] = account.company.name if account.company else None
        data['parent_account_name'] = account.parent_account.name if account.parent_account else None
        data['sub_accounts_count'] = account.sub_accounts.count()
        data['journal_entries_count'] = account.journal_entries.count()
        
        return format_success_response(data=data, tool_name=tool_name, metadata=get_tool_metadata(tool_name))
    except Account.DoesNotExist:
        return format_error_response(Exception(f"Account with ID {account_id} not found"), tool_name)
    except Exception as e:
        return format_error_response(e, tool_name)


def search_accounts(query: str, filters: Optional[Dict[str, Any]] = None, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
    """
    Search accounts by name or account number with optional additional filters
    
    Args:
        query: Search query string
        filters: Optional dict of additional filters (e.g., {"account_type": "Asset"})
        page: Page number (1-indexed)
        page_size: Number of results per page
        
    Example:
        search_accounts("cash", {"account_type": "Asset", "is_active": True})
    """
    tool_name = "search_accounts"
    try:
        from django.db.models import Q
        
        accounts = Account.objects.filter(
            Q(name__icontains=query) |
            Q(account_number__icontains=query)
        ).select_related('company')
        accounts = apply_filters(accounts, filters)
        accounts = accounts.order_by('account_number')
        
        result = paginate_results(accounts, page, page_size)
        
        return format_success_response(
            data=result,
            tool_name=tool_name,
            metadata={**get_tool_metadata(tool_name), "search_query": query}
        )
    except Exception as e:
        return format_error_response(e, tool_name)


def get_account_balance(account_id: int) -> Dict[str, Any]:
    """Calculate account balance from journal entries"""
    tool_name = "get_account_balance"
    try:
        from django.db.models import Sum
        
        account = Account.objects.get(id=account_id)
        
        total_debits = account.journal_entries.aggregate(
            total=Sum('debit_amount')
        )['total'] or 0
        
        total_credits = account.journal_entries.aggregate(
            total=Sum('credit_amount')
        )['total'] or 0
        
        balance = total_debits - total_credits
        
        data = {
            "account_id": account_id,
            "account_name": account.name,
            "account_number": account.account_number,
            "account_type": account.account_type,
            "total_debits": float(total_debits),
            "total_credits": float(total_credits),
            "balance": float(balance),
            "balance_type": "debit" if balance >= 0 else "credit",
            "entry_count": account.journal_entries.count()
        }
        
        return format_success_response(data=data, tool_name=tool_name, metadata=get_tool_metadata(tool_name))
    except Account.DoesNotExist:
        return format_error_response(Exception(f"Account with ID {account_id} not found"), tool_name)
    except Exception as e:
        return format_error_response(e, tool_name)


def get_account_hierarchy(account_id: int) -> Dict[str, Any]:
    """Get account hierarchy (parent and children)"""
    tool_name = "get_account_hierarchy"
    try:
        account = Account.objects.select_related('parent_account').get(id=account_id)
        
        # Get parents (walk up the tree)
        parents = []
        current = account.parent_account
        while current:
            parents.insert(0, {
                "id": current.id,
                "name": current.name,
                "account_number": current.account_number
            })
            current = current.parent_account
        
        # Get children
        children = serialize_queryset(
            account.sub_accounts.all(),
            fields=['id', 'name', 'account_number', 'account_type']
        )
        
        data = {
            "account": {
                "id": account.id,
                "name": account.name,
                "account_number": account.account_number,
                "account_type": account.account_type,
                "is_group": account.is_group
            },
            "parents": parents,
            "children": children,
            "depth_level": len(parents)
        }
        
        return format_success_response(data=data, tool_name=tool_name, metadata=get_tool_metadata(tool_name))
    except Account.DoesNotExist:
        return format_error_response(Exception(f"Account with ID {account_id} not found"), tool_name)
    except Exception as e:
        return format_error_response(e, tool_name)
