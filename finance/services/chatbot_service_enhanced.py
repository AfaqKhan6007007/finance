"""
Enhanced Chatbot Service with MCP Integration
Integrates MCP server tools via subprocess stdio communication.
"""
from openai import OpenAI
from django.conf import settings
from typing import List, Dict, Optional
import logging
import json
from pathlib import Path

# Import MCP client components
from chatbot.mcp_client.connector import MCPClientConnector
from chatbot.mcp_client.server_manager import MCPServerManager
from chatbot.mcp_client.tool_handler import MCPToolHandler

# Import utilities
from chatbot.utils.response_formatter import ResponseFormatter
from chatbot.utils.token_counter import TokenCounter
from chatbot.schema_tools.schema_provider import SchemaProvider
from chatbot.prompt_templates.system_prompt import get_system_prompt
from chatbot import config as chatbot_config

logger = logging.getLogger(__name__)


class EnhancedChatbotService:
    """
    Enhanced chatbot service with MCP integration via subprocess.
    Communicates with MCP server process using JSON-RPC over stdio.
    """
    
    def __init__(self):
        """Initialize enhanced chatbot with MCP subprocess integration"""
        logger.info("="*80)
        logger.info("INITIALIZING EnhancedChatbotService")
        logger.info("="*80)
        
        # Initialize OpenAI client
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        
        # Initialize MCP server manager for subprocess
        try:
            # Get path to MCP server
            django_root = Path(__file__).resolve().parent.parent.parent
            mcp_server_path = django_root / "mcp_server" / "server.py"
            
            if not mcp_server_path.exists():
                raise FileNotFoundError(f"MCP server not found at {mcp_server_path}")
            
            # Get venv Python executable (where Django is installed)
            import sys
            python_executable = sys.executable  # Use the same Python as Django
            
            # Initialize server manager
            self.server_manager = MCPServerManager(
                server_path=mcp_server_path,
                python_executable=python_executable
            )
            
            # Initialize MCP connector with server manager
            self.mcp_connector = MCPClientConnector(self.server_manager)
            self.response_formatter = ResponseFormatter()
            self.tool_handler = MCPToolHandler(self.mcp_connector, self.response_formatter)
            
            logger.info("[OK] EnhancedChatbotService initialized with subprocess MCP integration")
            
        except Exception as e:
            logger.error(f"[ERROR] Error initializing MCP components: {e}")
            self.server_manager = None
            self.mcp_connector = None
            self.tool_handler = None
        
        # Initialize utilities
        self.token_counter = TokenCounter(model=chatbot_config.CHATBOT_MODEL)
        self.schema_provider = SchemaProvider()
        
        # System prompt will be added to first message
        self.system_prompt = get_system_prompt()
        logger.info(f"[OK] System prompt loaded (length: {len(self.system_prompt)} chars)")
        logger.info(f"System prompt preview: {self.system_prompt[:200]}...")
        logger.info("="*80)
    
    def ensure_mcp_connection(self):
        """
        Ensure MCP server is running and connected via subprocess.
        """
        if not self.server_manager:
            raise RuntimeError("Server manager not initialized")
        
        # Start server if not running
        if not self.server_manager.is_running():
            try:
                logger.info("Starting MCP server subprocess...")
                if not self.server_manager.start():
                    raise Exception("Failed to start MCP server")
                logger.info("MCP server started successfully")
            except Exception as e:
                logger.error(f"Failed to start MCP server: {e}")
                raise
        
        # Connect if not connected
        if not self.mcp_connector.is_connected:
            try:
                logger.info("Connecting to MCP server via stdio...")
                self.mcp_connector.connect()
                logger.info("Connected to MCP server successfully")
            except Exception as e:
                logger.error(f"Failed to connect to MCP server: {e}") 
                raise
    
    def get_mcp_status(self):
        """
        Get current MCP server and connection status.
        """
        if not self.server_manager:
            return {
                'initialized': False,
                'error': 'Server manager not initialized'
            }
        
        health = self.server_manager.get_health_status()
        
        return {
            'initialized': True,
            'server_running': health.get('running', False),
            'server_pid': health.get('pid'),
            'server_uptime': health.get('uptime', 0),
            'connector_available': self.mcp_connector is not None,
            'tools_connected': self.mcp_connector.is_connected if self.mcp_connector else False,
        }
    
    def clear_conversation(self, session: dict) -> None:
        """
        Clear conversation history from session.
        
        Args:
            session: Django session object
        """
        if 'conversation' in session:
            logger.info("[OK] Clearing conversation history from session")
            del session['conversation']
            session.modified = True
        else:
            logger.info("ℹ️ No conversation to clear")
    
    def get_conversation_history(self, session: dict, include_system: bool = False) -> list:
        """
        Get conversation history for display.
        
        Args:
            session: Django session object
            include_system: Whether to include system messages
            
        Returns:
            List of message dicts (without system messages by default)
        """
        conversation = session.get('conversation', [])
        
        if not include_system:
            # Filter out system messages for UI display
            conversation = [msg for msg in conversation if msg.get('role') != 'system']
        
        return conversation
    
    def send_message(self, user_message: str, session: dict) -> str:
        """
        Send a message to the chatbot with MCP tool integration.
        
        Args:
            user_message: User's message
            session: Session dict with 'conversation' key
            
        Returns:
            Chatbot response
        """
        try:
            # Ensure MCP connection
            self.ensure_mcp_connection()
            
            # CRITICAL: Conversation management with max history limit
            MAX_CONVERSATION_MESSAGES = 20  # Keep only last 20 messages (10 exchanges)
            
            # Get or initialize conversation history
            conversation = session.get('conversation', [])
            
            # CRITICAL: Prune old messages if conversation is too long
            if len(conversation) > MAX_CONVERSATION_MESSAGES:
                logger.warning(f"⚠️ Conversation too long ({len(conversation)} messages), pruning to {MAX_CONVERSATION_MESSAGES}")
                # Keep system prompt (first message) + last N messages
                system_msg = conversation[0] if conversation and conversation[0].get('role') == 'system' else None
                recent_messages = conversation[-(MAX_CONVERSATION_MESSAGES-1):] if system_msg else conversation[-MAX_CONVERSATION_MESSAGES:]
                
                if system_msg:
                    conversation = [system_msg] + recent_messages
                else:
                    conversation = recent_messages
                logger.info(f"[OK] Pruned conversation to {len(conversation)} messages")
            
            # Add system prompt if first message or if missing
            if not conversation:
                conversation.append({
                    "role": "system",
                    "content": self.system_prompt
                })
                logger.info(f"[OK] Added system prompt to new conversation")
            elif conversation[0].get('role') != 'system':
                # System prompt missing - add it at the beginning
                logger.warning(f"⚠️ System prompt missing, adding it now")
                conversation.insert(0, {
                    "role": "system",
                    "content": self.system_prompt
                })
            else:
                logger.info(f"[OK] Existing conversation loaded: {len(conversation)} messages")
                # Log the roles to see what's in there
                role_counts = {}
                for msg in conversation:
                    role = msg.get('role', 'unknown')
                    role_counts[role] = role_counts.get(role, 0) + 1
                logger.info(f"  Message breakdown: {role_counts}")
                
                # Verify system prompt
                system_content = conversation[0].get('content', '')
                if 'CRITICAL RULE FOR CREATE OPERATIONS' not in system_content:
                    logger.error(f"⚠️ WRONG SYSTEM PROMPT! Replacing with correct one")
                    conversation[0] = {
                        "role": "system",
                        "content": self.system_prompt
                    }
                else:
                    logger.info(f"  [OK] System prompt verified (has CRITICAL RULE)")
            
            # Add user message
            conversation.append({
                "role": "user",
                "content": user_message
            })
            
            # Get available tools from MCP server
            mcp_tools = self.mcp_connector.discover_tools()
            
            # Add schema tool
            schema_tool = self._get_schema_tool()
            all_tools = mcp_tools + [schema_tool]
            
            logger.info(f"[OK] Available tools: {len(all_tools)} total ({len(mcp_tools)} MCP + 1 schema)")
            logger.info(f"[OK] Tool names: {[tool.get('function', {}).get('name', 'unknown') for tool in all_tools[:5]]}...")
            
            # Call OpenAI with tools
            max_iterations = chatbot_config.MAX_TOOL_ITERATIONS
            iteration = 0
            
            logger.info(f"[OK] Starting LLM conversation loop (max iterations: {max_iterations})")
            
            while iteration < max_iterations:
                iteration += 1
                logger.info(f"\n--- ITERATION {iteration} ---")
                logger.info(f"Conversation messages: {len(conversation)}")
                logger.info(f"Last user message: {conversation[-1].get('content', '')[:100]}...")
                
                response = self.client.chat.completions.create(
                    model=chatbot_config.CHATBOT_MODEL,
                    messages=conversation,
                    tools=all_tools,
                    tool_choice="auto",
                    temperature=0.0
                )
                
                message = response.choices[0].message
                logger.info(f"[OK] LLM Response received")
                logger.info(f"  - Has content: {bool(message.content)}")
                logger.info(f"  - Has tool calls: {bool(message.tool_calls)}")
                if message.content:
                    logger.info(f"  - Content preview: {message.content[:200]}...")
                if message.tool_calls:
                    logger.info(f"  - Tool calls: {[tc.function.name for tc in message.tool_calls]}")
                
                # Add assistant message to conversation
                conversation.append({
                    "role": "assistant",
                    "content": message.content,
                    "tool_calls": [tc.model_dump() for tc in message.tool_calls] if message.tool_calls else None
                })
                
                # Check if tool calls are needed
                if not message.tool_calls:
                    # No more tool calls, return final response
                    logger.info(f"[OK] No tool calls - returning final response to user")
                    final_response = message.content or "I apologize, but I couldn't generate a response."
                    logger.info(f"Final response: {final_response[:200]}...")
                    logger.info("="*80)
                    
                    # Save conversation (already pruned at start)
                    session['conversation'] = conversation
                    return final_response
                
                # Execute tool calls
                logger.info(f"[OK] Executing {len(message.tool_calls)} tool calls...")
                for tool_call in message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)
                    
                    logger.info(f"  → Calling tool: {tool_name}")
                    logger.info(f"    Args: {json.dumps(tool_args, indent=2)[:200]}...")
                    
                    logger.info(f"Executing tool: {tool_name} with args: {tool_args}")
                    
                    try:
                        # Handle schema tool locally
                        if tool_name == "get_table_schema":
                            result = self._execute_schema_tool(tool_args)
                        else:
                            # Execute via MCP connector
                            result = self.mcp_connector.call_tool(tool_name, tool_args)
                        
                        logger.info(f"Tool {tool_name} returned: {str(result)[:200]}")
                        
                        # Format result
                        formatted_result = self.response_formatter.format_tool_response(
                            tool_name, result
                        )
                        
                        # Add tool result to conversation
                        conversation.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": json.dumps(formatted_result) if isinstance(formatted_result, dict) else formatted_result
                        })
                        
                    except Exception as e:
                        logger.error(f"Error executing tool {tool_name}: {e}", exc_info=True)
                        error_msg = f"[{tool_name}] Error: {str(e)}"
                        conversation.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": error_msg
                        })
            
            # Max iterations reached
            final_response = "I apologize, but I need to stop here. Please try rephrasing your question."
            session['conversation'] = conversation
            return final_response
            
        except Exception as e:
            logger.error(f"Error in send_message: {e}", exc_info=True)
            return f"I encountered an error: {str(e)}"
    
    def _get_schema_tool(self) -> dict:
        """
        Get schema tool definition for OpenAI function calling.
        """
        return {
            "type": "function",
            "function": {
                "name": "get_table_schema",
                "description": "Get the schema information for a database table",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "table_name": {
                            "type": "string",
                            "description": "Name of the table (e.g., 'company', 'invoice', 'account')"
                        },
                        "include_details": {
                            "type": "boolean",
                            "description": "Include detailed information like filters and relationships",
                            "default": False
                        }
                    },
                    "required": ["table_name"]
                }
            }
        }
    
    def _execute_schema_tool(self, args: dict) -> dict:
        """
        Execute schema tool locally.
        """
        table_name = args.get("table_name")
        include_details = args.get("include_details", False)
        
        mode = "full" if include_details else "minimal"
        return self.schema_provider.get_schema(table_name, mode=mode)
    
    def cleanup(self):
        """
        Cleanup resources (stop MCP server).
        """
        if self.server_manager:
            logger.info("Stopping MCP server...")
            self.server_manager.stop()
