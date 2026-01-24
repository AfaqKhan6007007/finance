"""
Company Tools for MCP Server
Micro-tools for querying Company data following MCP best practices:
- Stateless, idempotent design
- Single responsibility per tool
- Proper error handling
- Consistent response format
"""
from typing import Dict, Any, List, Optional
from finance.models import Company
from utils.helpers import (
    format_success_response,
    format_error_response,
    serialize_queryset,
    serialize_model_instance,
    paginate_results,
    get_tool_metadata,
    apply_filters
)


def list_companies(filters: Optional[Dict[str, Any]] = None, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
    """
    List all companies with optional dynamic filtering
    
    Args:
        filters: Optional dict of filters (e.g., {"country": "USA", "is_active": True})
        page: Page number (1-indexed)
        page_size: Number of results per page
        
    Returns:
        Paginated list of companies
        
    Example filters:
        {"country": "USA"}
        {"name__icontains": "tech"}
        {"is_active": True}
    """
    tool_name = "list_companies"
    try:
        companies = Company.objects.all()
        companies = apply_filters(companies, filters)
        companies = companies.order_by('-created_at')
        result = paginate_results(companies, page, page_size)
        
        return format_success_response(
            data=result,
            tool_name=tool_name,
            metadata=get_tool_metadata(tool_name)
        )
    except Exception as e:
        return format_error_response(e, tool_name)


def get_company(company_id: int) -> Dict[str, Any]:
    """
    Get detailed information about a specific company
    
    Args:
        company_id: The ID of the company
        
    Returns:
        Company details
    """
    tool_name = "get_company"
    try:
        company = Company.objects.get(id=company_id)
        data = serialize_model_instance(company)
        
        # Add related counts
        data['total_accounts'] = company.accounts.count()
        data['total_suppliers'] = company.suppliers.count()
        data['total_customers'] = company.customers.count()
        data['total_invoices'] = company.invoices.count()
        
        return format_success_response(
            data=data,
            tool_name=tool_name,
            metadata=get_tool_metadata(tool_name)
        )
    except Company.DoesNotExist:
        return format_error_response(
            Exception(f"Company with ID {company_id} not found"),
            tool_name
        )
    except Exception as e:
        return format_error_response(e, tool_name)


def search_companies(query: str, filters: Optional[Dict[str, Any]] = None, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
    """
    Search companies by name, abbreviation, or country with optional additional filters
    
    Args:
        query: Search query string
        filters: Optional dict of additional filters (e.g., {"is_active": True})
        page: Page number (1-indexed)
        page_size: Number of results per page
        
    Returns:
        Matching companies
        
    Example:
        search_companies("tech", {"country": "USA", "is_active": True})
    """
    tool_name = "search_companies"
    try:
        from django.db.models import Q
        
        companies = Company.objects.filter(
            Q(name__icontains=query) |
            Q(abbreviation__icontains=query) |
            Q(country__icontains=query)
        )
        companies = apply_filters(companies, filters)
        companies = companies.order_by('-created_at')
        
        result = paginate_results(companies, page, page_size)
        
        return format_success_response(
            data=result,
            tool_name=tool_name,
            metadata={
                **get_tool_metadata(tool_name),
                "search_query": query
            }
        )
    except Exception as e:
        return format_error_response(e, tool_name)


def get_company_accounts(company_id: int, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
    """
    Get all accounts belonging to a specific company
    
    Args:
        company_id: The ID of the company
        page: Page number (1-indexed)
        page_size: Number of results per page
        
    Returns:
        Company's accounts
    """
    tool_name = "get_company_accounts"
    try:
        company = Company.objects.get(id=company_id)
        accounts = company.accounts.all().order_by('account_number')
        
        result = paginate_results(accounts, page, page_size)
        
        return format_success_response(
            data={
                "company_name": company.name,
                "company_id": company_id,
                **result
            },
            tool_name=tool_name,
            metadata=get_tool_metadata(tool_name)
        )
    except Company.DoesNotExist:
        return format_error_response(
            Exception(f"Company with ID {company_id} not found"),
            tool_name
        )
    except Exception as e:
        return format_error_response(e, tool_name)


def get_company_stats(company_id: int) -> Dict[str, Any]:
    """
    Get statistical summary for a company
    
    Args:
        company_id: The ID of the company
        
    Returns:
        Company statistics
    """
    tool_name = "get_company_stats"
    try:
        from django.db.models import Sum, Count
        
        company = Company.objects.get(id=company_id)
        
        stats = {
            "company_id": company_id,
            "company_name": company.name,
            "total_accounts": company.accounts.count(),
            "total_suppliers": company.suppliers.count(),
            "total_customers": company.customers.count(),
            "total_invoices": company.invoices.count(),
            "total_journal_entries": company.journal_entries.count(),
            "total_budgets": company.budgets.count(),
            "total_cost_centers": company.cost_centers.count(),
            
            # Invoice stats
            "invoice_stats": {
                "draft": company.invoices.filter(status='draft').count(),
                "sent": company.invoices.filter(status='sent').count(),
                "paid": company.invoices.filter(status='paid').count(),
                "cancelled": company.invoices.filter(status='cancelled').count(),
            },
            
            # Financial summary
            "total_invoice_amount": company.invoices.aggregate(
                total=Sum('total_amount')
            )['total'] or 0,
        }
        
        return format_success_response(
            data=stats,
            tool_name=tool_name,
            metadata=get_tool_metadata(tool_name)
        )
    except Company.DoesNotExist:
        return format_error_response(
            Exception(f"Company with ID {company_id} not found"),
            tool_name
        )
    except Exception as e:
        return format_error_response(e, tool_name)
