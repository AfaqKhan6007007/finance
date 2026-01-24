"""
Tax Tools for MCP Server
Micro-tools for querying Tax-related data
"""
from typing import Dict, Any, Optional
from finance.models import TaxRule, TaxCategory, TaxItemTemplate
from utils.helpers import (
    format_success_response,
    format_error_response,
    serialize_queryset,
    serialize_model_instance,
    paginate_results,
    get_tool_metadata,
    apply_filters
)


def list_tax_rules(filters: Optional[Dict[str, Any]] = None, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
    """
    List all tax rules with optional dynamic filtering
    
    Args:
        filters: Optional dict of filters (e.g., {"tax_type": "sales", "company__id": 5})
        page: Page number (1-indexed)
        page_size: Number of results per page
        
    Example filters:
        {"tax_type": "sales"}
        {"company__id": 5}
        {"from_date__gte": "2025-01-01"}
        {"billing_country": "USA"}
    """
    tool_name = "list_tax_rules"
    try:
        tax_rules = TaxRule.objects.select_related('company', 'customer', 'tax_category', 'sales_tax_template')
        tax_rules = apply_filters(tax_rules, filters)
        tax_rules = tax_rules.order_by('-priority', '-from_date')
        result = paginate_results(tax_rules, page, page_size)
        
        return format_success_response(data=result, tool_name=tool_name, metadata=get_tool_metadata(tool_name))
    except Exception as e:
        return format_error_response(e, tool_name)


def get_tax_rule(tax_rule_id: int) -> Dict[str, Any]:
    """
    Get detailed information about a specific tax rule
    
    Args:
        tax_rule_id: The ID of the tax rule
        
    Returns:
        Tax rule details with related information
    """
    tool_name = "get_tax_rule"
    try:
        tax_rule = TaxRule.objects.select_related('company', 'customer', 'tax_category', 'sales_tax_template').get(id=tax_rule_id)
        data = serialize_model_instance(tax_rule)
        
        # Add related info
        data['company_name'] = tax_rule.company.name if tax_rule.company else None
        data['customer_name'] = tax_rule.customer.name if tax_rule.customer else None
        data['tax_category_name'] = tax_rule.tax_category.name if tax_rule.tax_category else None
        
        return format_success_response(data=data, tool_name=tool_name, metadata=get_tool_metadata(tool_name))
    except TaxRule.DoesNotExist:
        return format_error_response(Exception(f"Tax rule with ID {tax_rule_id} not found"), tool_name)
    except Exception as e:
        return format_error_response(e, tool_name)


def search_tax_rules(query: str, filters: Optional[Dict[str, Any]] = None, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
    """
    Search tax rules by item, city, state, or country with optional additional filters
    
    Args:
        query: Search query string
        filters: Optional dict of additional filters
        page: Page number (1-indexed)
        page_size: Number of results per page
        
    Example:
        search_tax_rules("USA", {"tax_type": "sales"})
    """
    tool_name = "search_tax_rules"
    try:
        from django.db.models import Q
        
        tax_rules = TaxRule.objects.filter(
            Q(item__icontains=query) |
            Q(billing_city__icontains=query) |
            Q(billing_state__icontains=query) |
            Q(billing_country__icontains=query) |
            Q(shipping_city__icontains=query) |
            Q(shipping_state__icontains=query) |
            Q(shipping_country__icontains=query)
        ).select_related('company', 'customer', 'tax_category')
        tax_rules = apply_filters(tax_rules, filters)
        tax_rules = tax_rules.order_by('-priority')
        
        result = paginate_results(tax_rules, page, page_size)
        
        return format_success_response(
            data=result,
            tool_name=tool_name,
            metadata={**get_tool_metadata(tool_name), "search_query": query}
        )
    except Exception as e:
        return format_error_response(e, tool_name)


def list_tax_categories(filters: Optional[Dict[str, Any]] = None, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
    """
    List all tax categories with optional dynamic filtering
    
    Args:
        filters: Optional dict of filters
        page: Page number (1-indexed)
        page_size: Number of results per page
    """
    tool_name = "list_tax_categories"
    try:
        categories = TaxCategory.objects.all()
        categories = apply_filters(categories, filters)
        categories = categories.order_by('name')
        result = paginate_results(categories, page, page_size)
        
        return format_success_response(data=result, tool_name=tool_name, metadata=get_tool_metadata(tool_name))
    except Exception as e:
        return format_error_response(e, tool_name)


def list_tax_templates(filters: Optional[Dict[str, Any]] = None, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
    """
    List all tax item templates with optional dynamic filtering
    
    Args:
        filters: Optional dict of filters
        page: Page number (1-indexed)
        page_size: Number of results per page
    """
    tool_name = "list_tax_templates"
    try:
        templates = TaxItemTemplate.objects.all()
        templates = apply_filters(templates, filters)
        templates = templates.order_by('title')
        result = paginate_results(templates, page, page_size)
        
        return format_success_response(data=result, tool_name=tool_name, metadata=get_tool_metadata(tool_name))
    except Exception as e:
        return format_error_response(e, tool_name)
