"""
MCP Client Connector - Subprocess/Stdio Version
Connects to MCP server via subprocess stdio communication using JSON-RPC protocol.
"""
import json
import logging
import time
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class MCPClientConnector:
    """
    MCP client connector using stdio (subprocess) communication.
    Communicates with MCP server process via JSON-RPC over stdin/stdout.
    """
    
    def __init__(self, server_manager):
        """
        Initialize MCP client.
        
        Args:
            server_manager: MCPServerManager instance that manages the subprocess
        """
        self.server_manager = server_manager
        self.is_connected = False
        self._request_id_counter = 0
    
    def connect(self):
        """
        Connect to MCP server via stdio (subprocess communication).
        Sends initialize request and capabilities to establish connection.
        """
        try:
            if not self.server_manager or not self.server_manager.is_running():
                raise RuntimeError("MCP server is not running")
            
            # Send initialize request
            init_request = {
                "jsonrpc": "2.0",
                "id": self._generate_request_id(),
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "roots": {"listChanged": True},
                        "sampling": {}
                    },
                    "clientInfo": {
                        "name": "finance-chatbot",
                        "version": "1.0.0"
                    }
                }
            }
            
            response = self._send_request(init_request)
            
            if "result" in response:
                logger.info("Successfully connected to MCP server")
                self.is_connected = True
                
                # Send initialized notification
                self._send_notification({
                    "jsonrpc": "2.0",
                    "method": "notifications/initialized"
                })
            else:
                raise Exception(f"Initialize failed: {response.get('error', 'Unknown error')}")
                
        except Exception as e:
            logger.error(f"Failed to connect to MCP server: {e}")
            self.is_connected = False
            raise
    
    def discover_tools(self) -> list:
        """
        Get list of available tools from MCP server.
        Returns tool definitions compatible with OpenAI function calling.
        """
        if not self.is_connected:
            return []
        
        try:
            request = {
                "jsonrpc": "2.0",
                "id": self._generate_request_id(),
                "method": "tools/list"
            }
            
            response = self._send_request(request)
            
            if "result" in response and "tools" in response["result"]:
                # Convert MCP tool format to OpenAI function calling format
                mcp_tools = response["result"]["tools"]
                openai_tools = []
                
                for tool in mcp_tools:
                    openai_tool = {
                        "type": "function",
                        "function": {
                            "name": tool["name"],
                            "description": tool.get("description", ""),
                            "parameters": tool.get("inputSchema", {
                                "type": "object",
                                "properties": {},
                                "required": []
                            })
                        }
                    }
                    openai_tools.append(openai_tool)
                
                logger.info(f"Discovered {len(openai_tools)} tools from MCP server")
                return openai_tools
            else:
                logger.warning("No tools found in MCP server response")
                return []
                
        except Exception as e:
            logger.error(f"Failed to discover tools: {e}")
            return []
    
    def call_tool(self, name: str, arguments: dict) -> Any:
        """
        Call a tool via MCP server using JSON-RPC.
        
        Args:
            name: Tool name
            arguments: Tool arguments
            
        Returns:
            Tool execution result
        """
        if not self.is_connected:
            raise RuntimeError("Not connected to MCP server")
        
        try:
            request = {
                "jsonrpc": "2.0",
                "id": self._generate_request_id(),
                "method": "tools/call",
                "params": {
                    "name": name,
                    "arguments": arguments
                }
            }
            
            response = self._send_request(request)
            
            if "result" in response:
                return response["result"]
            else:
                error = response.get("error", {})
                raise Exception(f"Tool call failed: {error.get('message', 'Unknown error')}")
                
        except Exception as e:
            logger.error(f"Error calling tool {name}: {e}")
            raise
    
    def disconnect(self):
        """
        Disconnect from MCP server.
        """
        self.is_connected = False
        logger.info("Disconnected from MCP server")
    
    def _send_request(self, request: dict, timeout: int = 30) -> dict:
        """
        Send JSON-RPC request to MCP server via stdio.
        
        Args:
            request: JSON-RPC request dictionary
            timeout: Timeout in seconds (default 30)
            
        Returns:
            JSON-RPC response dictionary
        """
        if not self.server_manager or not self.server_manager.process:
            raise RuntimeError("Server process not available")
        
        try:
            # Check if process is still alive
            if self.server_manager.process.poll() is not None:
                raise RuntimeError(f"Server process died with code {self.server_manager.process.poll()}")
            
            # Serialize request to JSON
            request_json = json.dumps(request) + "\n"
            request_bytes = request_json.encode('utf-8')
            
            logger.debug(f"Sending request: {request.get('method', 'unknown')}")
            
            # Send to server stdin
            self.server_manager.process.stdin.write(request_bytes)
            self.server_manager.process.stdin.flush()
            
            # Read response from server stdout with timeout
            import select
            start_time = time.time()
            
            while True:
                # Check timeout
                if time.time() - start_time > timeout:
                    raise TimeoutError(f"No response from server after {timeout}s")
                
                # Try to read line (non-blocking check)
                response_line = self.server_manager.process.stdout.readline()
                
                if response_line:
                    logger.debug(f"Received response: {len(response_line)} bytes")
                    response = json.loads(response_line.decode('utf-8'))
                    return response
                
                # Check if process died
                if self.server_manager.process.poll() is not None:
                    # Read any error output
                    stderr_output = self.server_manager.process.stderr.read().decode('utf-8', errors='ignore')
                    raise RuntimeError(f"Server process died. stderr: {stderr_output[:500]}")
                
                # Small sleep to avoid busy waiting
                time.sleep(0.1)
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response from server: {e}")
            logger.error(f"Raw response: {response_line[:200] if response_line else 'None'}")
            raise
        except Exception as e:
            logger.error(f"Error sending request to MCP server: {e}")
            raise
    
    def _send_notification(self, notification: dict):
        """
        Send JSON-RPC notification to MCP server (no response expected).
        
        Args:
            notification: JSON-RPC notification dictionary
        """
        if not self.server_manager or not self.server_manager.process:
            raise RuntimeError("Server process not available")
        
        try:
            # Serialize notification to JSON
            notification_json = json.dumps(notification) + "\n"
            notification_bytes = notification_json.encode('utf-8')
            
            # Send to server stdin
            self.server_manager.process.stdin.write(notification_bytes)
            self.server_manager.process.stdin.flush()
            
        except Exception as e:
            logger.error(f"Error sending notification to MCP server: {e}")
            raise
    
    def _generate_request_id(self) -> int:
        """
        Generate unique request ID for JSON-RPC.
        """
        self._request_id_counter += 1
        return self._request_id_counter
