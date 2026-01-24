"""
Response Formatter
Formats MCP tool responses for optimal LLM consumption
Reduces token usage while maintaining clarity
"""
import json
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class ResponseFormatter:
    """
    Formats tool responses to be concise yet informative.
    Helps reduce token usage in conversation context.
    """
    
    @staticmethod
    def format_tool_response(tool_name: str, response: Dict[str, Any], max_length: int = 2000) -> str:
        """
        Format a tool response for inclusion in conversation.
        
        Args:
            tool_name: Name of the tool that was called
            response: The tool's response dict
            max_length: Maximum character length for response
            
        Returns:
            Formatted string suitable for LLM context
        """
        try:
            # Check if response indicates success
            if not response.get('success', False):
                error_msg = response.get('error', 'Unknown error')
                return f"[{tool_name}] Error: {error_msg}"
            
            data = response.get('data', {})
            
            # Handle different response types
            if 'results' in data:
                # Paginated list response
                return ResponseFormatter._format_list_response(tool_name, data, max_length)
            elif 'stats' in response or 'statistics' in response:
                # Statistics response
                return ResponseFormatter._format_stats_response(tool_name, response)
            elif isinstance(data, dict) and 'id' in data:
                # Single record response
                return ResponseFormatter._format_single_record(tool_name, data, max_length)
            else:
                # Generic response
                return ResponseFormatter._format_generic_response(tool_name, data, max_length)
        
        except Exception as e:
            logger.error(f"Error formatting response for {tool_name}: {e}")
            return f"[{tool_name}] Response received (formatting error)"
    
    @staticmethod
    def _format_list_response(tool_name: str, data: Dict, max_length: int) -> str:
        """Format a paginated list response"""
        results = data.get('results', [])
        pagination = data.get('pagination', {})
        
        total_count = pagination.get('total_count', len(results))
        current_page = pagination.get('current_page', 1)
        
        if not results:
            return f"[{tool_name}] No results found"
        
        # Format first few results
        formatted_results = []
        char_count = 0
        
        for item in results:
            item_str = ResponseFormatter._format_dict_compact(item)
            item_length = len(item_str)
            
            if char_count + item_length > max_length:
                formatted_results.append("... (truncated)")
                break
            
            formatted_results.append(item_str)
            char_count += item_length
        
        result_str = "\n".join(formatted_results)
        summary = f"[{tool_name}] Found {total_count} total results (page {current_page})"
        
        return f"{summary}\n{result_str}"
    
    @staticmethod
    def _format_stats_response(tool_name: str, response: Dict) -> str:
        """Format a statistics response"""
        stats = response.get('stats', response.get('statistics', {}))
        
        formatted_stats = []
        for key, value in stats.items():
            if isinstance(value, (int, float)):
                formatted_stats.append(f"  {key}: {value:,.2f}")
            else:
                formatted_stats.append(f"  {key}: {value}")
        
        stats_str = "\n".join(formatted_stats)
        return f"[{tool_name}] Statistics:\n{stats_str}"
    
    @staticmethod
    def _format_single_record(tool_name: str, data: Dict, max_length: int) -> str:
        """Format a single record response"""
        formatted = ResponseFormatter._format_dict_compact(data)
        
        if len(formatted) > max_length:
            # Truncate and add indicator
            formatted = formatted[:max_length] + "... (truncated)"
        
        return f"[{tool_name}] Record found:\n{formatted}"
    
    @staticmethod
    def _format_generic_response(tool_name: str, data: Any, max_length: int) -> str:
        """Format a generic response"""
        formatted = json.dumps(data, indent=2, default=str)
        
        if len(formatted) > max_length:
            formatted = formatted[:max_length] + "... (truncated)"
        
        return f"[{tool_name}] Response:\n{formatted}"
    
    @staticmethod
    def _format_dict_compact(item: Dict) -> str:
        """Format a dict in a compact, readable way"""
        # Extract key fields for different entity types
        key_fields = {
            'company': ['id', 'name', 'country'],
            'account': ['id', 'account_name', 'account_type', 'balance'],
            'invoice': ['id', 'invoice_number', 'date', 'total_amount', 'status'],
            'supplier': ['id', 'name', 'country', 'gst_category'],
            'customer': ['id', 'name', 'country', 'gst_category'],
            'journal_entry': ['id', 'entry_number', 'date', 'debit_amount', 'credit_amount'],
            'budget': ['id', 'series', 'fiscal_year_from', 'fiscal_year_to'],
            'cost_center': ['id', 'cost_center_name', 'is_group'],
            'tax_rule': ['id', 'item', 'tax_type', 'shipping_state']
        }
        
        # Try to detect entity type and use appropriate fields
        entity_type = None
        if 'account_name' in item:
            entity_type = 'account'
        elif 'invoice_number' in item:
            entity_type = 'invoice'
        elif 'gstin_uin' in item and 'customer_type' in item:
            entity_type = 'customer'
        elif 'gstin_uin' in item:
            entity_type = 'supplier'
        elif 'cost_center_name' in item:
            entity_type = 'cost_center'
        elif 'entry_number' in item:
            entity_type = 'journal_entry'
        elif 'fiscal_year_from' in item:
            entity_type = 'budget'
        elif 'abbreviation' in item:
            entity_type = 'company'
        elif 'tax_type' in item:
            entity_type = 'tax_rule'
        
        if entity_type and entity_type in key_fields:
            # Format with key fields only
            parts = []
            for field in key_fields[entity_type]:
                if field in item:
                    value = item[field]
                    if isinstance(value, float):
                        parts.append(f"{field}={value:,.2f}")
                    else:
                        parts.append(f"{field}={value}")
            return "{ " + ", ".join(parts) + " }"
        else:
            # Fallback: show all fields
            return json.dumps(item, default=str)
    
    @staticmethod
    def summarize_for_context(tool_name: str, response: Dict, ultra_compact: bool = False) -> str:
        """
        Create an ultra-compact summary for conversation context.
        Used when token limits are approaching.
        
        Args:
            tool_name: Name of tool
            response: Tool response
            ultra_compact: If True, extremely minimal summary
            
        Returns:
            Very brief summary string
        """
        if not response.get('success'):
            return f"[{tool_name}] Failed"
        
        data = response.get('data', {})
        
        if 'results' in data:
            count = len(data['results'])
            total = data.get('pagination', {}).get('total_count', count)
            return f"[{tool_name}] {count}/{total} results"
        elif isinstance(data, dict) and 'id' in data:
            return f"[{tool_name}] Record ID {data['id']}"
        else:
            return f"[{tool_name}] OK"
