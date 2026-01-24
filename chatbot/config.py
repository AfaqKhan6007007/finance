"""
Chatbot Configuration
MCP and optimization settings for the chatbot
Local Django integration - tools are called directly via imports
"""
import os
from pathlib import Path

# MCP Tools Configuration
# For local Django integration, tools are imported directly (no subprocess)
MCP_TOOLS_PATH = Path(__file__).resolve().parent.parent / "mcp_server" / "tools"
MCP_SERVER_PATH = Path(__file__).resolve().parent.parent / "mcp_server" / "server.py"

# These are kept for backward compatibility but not used in local integration
MCP_SERVER_TIMEOUT = 30  # seconds
MCP_SERVER_MAX_RETRIES = 3
MCP_SERVER_RETRY_DELAY = 2  # seconds

# Tool Configuration
TOOL_CALL_TIMEOUT = 15  # seconds for individual tool calls
MAX_PARALLEL_TOOL_CALLS = 3  # maximum parallel tool executions
ENABLE_TOOL_CACHING = True
TOOL_CACHE_TTL = 300  # 5 minutes

# Token Optimization
MAX_CONVERSATION_HISTORY = 10  # reduced from 20 for token efficiency
MAX_TOOL_RESPONSE_LENGTH = 2000  # characters
ENABLE_RESPONSE_SUMMARIZATION = True
TOKEN_LIMIT_WARNING_THRESHOLD = 3000  # warn if approaching context limit

# Schema Tools Configuration
SCHEMA_CACHE_ENABLED = True
SCHEMA_CACHE_TTL = 600  # 10 minutes
MINIMAL_SCHEMA_MODE = True  # return only essential field information

# Model Configuration
CHATBOT_MODEL = os.getenv('CHATBOT_MODEL', 'gpt-4o-mini')  # gpt-4o-mini is cost-effective
CHATBOT_TEMPERATURE = 0.7
CHATBOT_MAX_TOKENS = 800  # reduced for cost optimization

# Logging Configuration
LOG_LEVEL = os.getenv('CHATBOT_LOG_LEVEL', 'INFO')
LOG_MCP_COMMUNICATIONS = False  # Set to True for debugging
LOG_TOKEN_USAGE = True

# Tool Filtering (for safety and cost control)
TOOL_BLACKLIST = []  # Tools that should never be called
TOOL_WHITELIST = []  # If set, only these tools can be called (empty = all allowed)

# Rate Limiting
MAX_TOOL_CALLS_PER_MESSAGE = 5  # prevent runaway tool calling
MAX_MESSAGES_PER_SESSION = 50

# Error Handling
RETRY_ON_MCP_ERROR = True
FALLBACK_TO_BASIC_MODE = True  # If MCP fails, continue without tools
SHOW_TOOL_ERRORS_TO_USER = False  # Hide technical errors from end users
