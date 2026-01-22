# MCP Server Utility Functions
from datetime import datetime
import hashlib
import json
from typing import Any, Dict, List, Optional
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Q
from decimal import Decimal


def get_tool_metadata(tool_name: str) -> Dict[str, str]:
    """
    Generate metadata for MCP tool (best practice)
    
    Args:
        tool_name: Name of the tool
        
    Returns:
        Dict with version, hash, timestamp
    """
    return {
        "version": "1.0.0",
        "tool_name": tool_name,
        "last_updated": datetime.utcnow().isoformat(),
        "code_hash": hashlib.sha256(tool_name.encode()).hexdigest()[:16]
    }


def serialize_queryset(queryset, fields: List[str] = None) -> List[Dict[str, Any]]:
    """
    Serialize Django QuerySet to JSON-serializable format
    
    Args:
        queryset: Django QuerySet
        fields: List of field names to include (None = all)
        
    Returns:
        List of dicts
    """
    result = []
    for obj in queryset:
        data = {}
        if fields:
            for field in fields:
                data[field] = getattr(obj, field, None)
        else:
            # Get all fields
            data = {
                field.name: getattr(obj, field.name)
                for field in obj._meta.fields
            }
        
        # Convert non-serializable types
        for key, value in data.items():
            if hasattr(value, 'isoformat'):  # Date/DateTime
                data[key] = value.isoformat()
            elif value is None:
                data[key] = None
            else:
                try:
                    json.dumps(value)
                except (TypeError, ValueError):
                    data[key] = str(value)
        
        result.append(data)
    
    return result


def serialize_model_instance(instance, fields: List[str] = None) -> Dict[str, Any]:
    """
    Serialize single Django model instance
    
    Args:
        instance: Django model instance
        fields: List of field names to include
        
    Returns:
        Dict representation
    """
    data = {}
    
    if fields:
        for field in fields:
            value = getattr(instance, field, None)
            if hasattr(value, 'isoformat'):
                data[field] = value.isoformat()
            else:
                data[field] = value
    else:
        for field in instance._meta.fields:
            value = getattr(instance, field.name)
            if hasattr(value, 'isoformat'):
                data[field.name] = value.isoformat()
            elif value is None:
                data[field.name] = None
            else:
                try:
                    json.dumps(value)
                    data[field.name] = value
                except (TypeError, ValueError):
                    data[field.name] = str(value)
    
    return data


def format_error_response(error: Exception, tool_name: str) -> Dict[str, Any]:
    """
    Format error response for MCP (consistent error handling)
    
    Args:
        error: Exception that occurred
        tool_name: Name of tool that errored
        
    Returns:
        Structured error dict
    """
    return {
        "success": False,
        "error": {
            "type": type(error).__name__,
            "message": str(error),
            "tool": tool_name,
            "timestamp": datetime.utcnow().isoformat()
        }
    }


def parse_filters(filters: Optional[Dict[str, Any]]) -> Q:
    """
    Parse filter dictionary into Django Q objects for dynamic filtering.
    LLM provides filters as parameters, this converts them to Django queries.
    
    Supported filter types:
    - Exact match: {"field": "value"}
    - Greater than: {"field__gt": value}
    - Less than: {"field__lt": value}
    - Greater/equal: {"field__gte": value}
    - Less/equal: {"field__lte": value}
    - Contains: {"field__icontains": "text"}
    - In list: {"field__in": [val1, val2]}
    - Date range: {"field__range": ["2024-01-01", "2024-12-31"]}
    - Is null: {"field__isnull": True}
    
    Args:
        filters: Dict of field filters from LLM
        
    Returns:
        Django Q object for queryset filtering
        
    Examples:
        >>> parse_filters({"balance__gte": 1000, "account_type": "Asset"})
        >>> parse_filters({"status__in": ["pending", "approved"], "amount__gt": 500})
    """
    if not filters:
        return Q()
    
    q_object = Q()
    
    for key, value in filters.items():
        # Convert string dates to datetime if needed
        if '__range' in key and isinstance(value, list):
            value = [datetime.fromisoformat(v) if isinstance(v, str) else v for v in value]
        
        # Convert string numbers to Decimal for monetary fields
        if any(field in key for field in ['balance', 'amount', 'total', 'price']):
            if isinstance(value, (str, int, float)):
                value = Decimal(str(value))
            elif isinstance(value, list):
                value = [Decimal(str(v)) if isinstance(v, (str, int, float)) else v for v in value]
        
        # Build Q object
        q_object &= Q(**{key: value})
    
    return q_object


def apply_filters(queryset, filters: Optional[Dict[str, Any]]):
    """
    Apply filters to Django QuerySet
    
    Args:
        queryset: Django QuerySet
        filters: Dictionary of filters
        
    Returns:
        Filtered QuerySet
    """
    if not filters:
        return queryset
    
    q_object = parse_filters(filters)
    return queryset.filter(q_object)


def format_success_response(data: Any, tool_name: str, metadata: Dict = None) -> Dict[str, Any]:
    """
    Format success response for MCP (consistent response structure)
    
    Args:
        data: The response data
        tool_name: Name of tool
        metadata: Optional metadata
        
    Returns:
        Structured response dict
    """
    response = {
        "success": True,
        "data": data,
        "meta": {
            "tool": tool_name,
            "timestamp": datetime.utcnow().isoformat(),
            **(metadata or {})
        }
    }
    return response


def paginate_results(queryset, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
    """
    Paginate QuerySet results
    
    Args:
        queryset: Django QuerySet
        page: Page number (1-indexed)
        page_size: Items per page
        
    Returns:
        Dict with paginated data and metadata
    """
    from django.core.paginator import Paginator, EmptyPage
    
    paginator = Paginator(queryset, page_size)
    
    try:
        page_obj = paginator.page(page)
    except EmptyPage:
        return {
            "results": [],
            "pagination": {
                "current_page": page,
                "total_pages": paginator.num_pages,
                "total_count": paginator.count,
                "page_size": page_size,
                "has_next": False,
                "has_previous": False
            }
        }
    
    return {
        "results": serialize_queryset(page_obj.object_list),
        "pagination": {
            "current_page": page,
            "total_pages": paginator.num_pages,
            "total_count": paginator.count,
            "page_size": page_size,
            "has_next": page_obj.has_next(),
            "has_previous": page_obj.has_previous()
        }
    }
