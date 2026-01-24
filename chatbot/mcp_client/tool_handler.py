"""
MCP Tool Handler
Converts between OpenAI function calling and MCP tool execution
"""
import json
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class MCPToolHandler:
    """
    Handles conversion between OpenAI function calls and MCP tool executions.
    Manages tool call workflow and response formatting.
    """
    
    def __init__(self, mcp_connector, response_formatter):
        """
        Initialize tool handler.
        
        Args:
            mcp_connector: MCPClientConnector instance
            response_formatter: ResponseFormatter instance
        """
        self.mcp_connector = mcp_connector
        self.response_formatter = response_formatter
    
    def execute_tool_calls(
        self,
        tool_calls: List[Dict],
        max_parallel: int = 3
    ) -> List[Dict]:
        """
        Execute multiple tool calls from OpenAI response.
        
        Args:
            tool_calls: List of tool call dicts from OpenAI
            max_parallel: Maximum parallel executions (currently sequential)
            
        Returns:
            List of tool call results
        """
        results = []
        
        for tool_call in tool_calls:
            result = self.execute_single_tool_call(tool_call)
            results.append(result)
        
        return results
    
    def execute_single_tool_call(self, tool_call: Dict) -> Dict:
        """
        Execute a single tool call.
        
        Args:
            tool_call: Tool call dict from OpenAI
            
        Returns:
            Dict with tool call ID and result
        """
        tool_call_id = tool_call.get('id')
        function = tool_call.get('function', {})
        function_name = function.get('name')
        
        try:
            # Parse arguments
            arguments_str = function.get('arguments', '{}')
            arguments = json.loads(arguments_str)
            
            logger.info(f"Executing tool: {function_name}")
            
            # Call the MCP tool
            result = self.mcp_connector.call_tool(function_name, arguments)
            
            # Format the response
            formatted_result = self.response_formatter.format_tool_response(
                function_name,
                result
            )
            
            return {
                'tool_call_id': tool_call_id,
                'role': 'tool',
                'name': function_name,
                'content': formatted_result
            }
        
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse tool arguments: {e}")
            return {
                'tool_call_id': tool_call_id,
                'role': 'tool',
                'name': function_name,
                'content': f"Error: Invalid arguments format - {str(e)}"
            }
        
        except Exception as e:
            logger.error(f"Error executing tool {function_name}: {e}")
            return {
                'tool_call_id': tool_call_id,
                'role': 'tool',
                'name': function_name,
                'content': f"Error: Tool execution failed - {str(e)}"
            }
    
    def get_tool_definitions_for_openai(self) -> List[Dict]:
        """
        Get tool definitions formatted for OpenAI function calling.
        
        Returns:
            List of tool definitions
        """
        return self.mcp_connector.discover_tools()
    
    def validate_tool_call(self, tool_call: Dict) -> bool:
        """
        Validate a tool call before execution.
        
        Args:
            tool_call: Tool call dict
            
        Returns:
            True if valid
        """
        if not tool_call.get('function'):
            return False
        
        function = tool_call['function']
        if not function.get('name'):
            return False
        
        # Check if tool exists
        available_tools = self.mcp_connector.discover_tools()
        tool_names = [t['function']['name'] for t in available_tools]
        
        return function['name'] in tool_names
