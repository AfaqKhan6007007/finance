# MCP Subprocess Integration - Summary

## ✅ Architecture Restored: Subprocess-Based MCP Server

As requested, the integration now uses the **standard MCP subprocess approach** with JSON-RPC communication over stdio.

## What Changed

### Before (Direct Imports - Not Standard)
```python
# Tools were imported directly into Django process
from tools.company_tools import list_companies
result = list_companies(**args)
```

### After (Subprocess - Standard MCP)
```python
# Tools run in separate subprocess, called via JSON-RPC
request = {"method": "tools/call", "params": {"name": "list_companies", ...}}
response = send_to_subprocess(request)
```

## Architecture Components

### 1. MCPServerManager (`chatbot/mcp_client/server_manager.py`)
- **Purpose**: Manages MCP server subprocess lifecycle
- **Features**:
  - Starts `mcp_server/server.py` as subprocess
  - Monitors process health
  - Handles graceful shutdown
  - Provides health metrics (PID, uptime, memory, CPU)

### 2. MCPClientConnector (`chatbot/mcp_client/connector.py`)
- **Purpose**: JSON-RPC client for subprocess communication
- **Features**:
  - Connects via stdio (stdin/stdout)
  - Sends initialize handshake
  - Discovers tools via `tools/list`
  - Calls tools via `tools/call`
  - Handles JSON-RPC protocol

### 3. EnhancedChatbotService (`finance/services/chatbot_service_enhanced.py`)
- **Purpose**: Main chatbot service with MCP integration
- **Features**:
  - Initializes MCPServerManager
  - Ensures server is running
  - Manages tool calls
  - Integrates with OpenAI
  - Token optimization

## Communication Flow

```
Django Request
    ↓
EnhancedChatbotService
    ↓
[First Message?] → MCPServerManager.start()
    ↓                    ↓
    ↓            subprocess.Popen([python, server.py])
    ↓                    ↓
    ↓            MCP Server Running (separate process)
    ↓
MCPClientConnector.connect()
    ↓
JSON-RPC {"method": "initialize"} → stdin
    ↓                                   ↓
    ←  {"result": {...}}  ←  stdout  ← 
    ↓
MCPClientConnector.discover_tools()
    ↓
JSON-RPC {"method": "tools/list"} → stdin
    ↓                                   ↓
    ←  {"result": {"tools": [...]}}  ← stdout
    ↓
OpenAI Chat API (with tool definitions)
    ↓
[Tool Call Needed?]
    ↓
MCPClientConnector.call_tool()
    ↓
JSON-RPC {"method": "tools/call", "params": {...}} → stdin
    ↓                                                    ↓
    ←  {"result": <tool_result>}  ←  stdout  ← 
    ↓
Response to User
```

## File Structure

```
finance/
├── chatbot/
│   ├── mcp_client/
│   │   ├── connector.py              # ✅ Subprocess JSON-RPC client
│   │   ├── connector_direct_import.py # Backup: direct import version
│   │   ├── server_manager.py         # ✅ Subprocess manager
│   │   └── tool_handler.py           # Tool execution handler
│   └── ...
├── finance/services/
│   ├── chatbot_service_enhanced.py        # ✅ Subprocess version
│   └── chatbot_service_enhanced_direct.py # Backup: direct version
├── mcp_server/
│   ├── server.py                     # ✅ MCP server (runs as subprocess)
│   └── tools/                        # ✅ 35 MCP tools
└── test_mcp_setup.py                 # ✅ Updated for subprocess testing
```

## Key Benefits of Subprocess Approach

1. **Standard MCP Compliance**: Follows official MCP protocol
2. **Process Isolation**: Server crashes don't kill Django
3. **Error Isolation**: Tool errors contained in subprocess
4. **Independent Testing**: Can test MCP server separately
5. **Production Ready**: Standard deployment pattern
6. **Protocol Correct**: Uses JSON-RPC over stdio

## Testing

Run the verification script:

```bash
python test_mcp_setup.py
```

Expected output:
```
[1/5] Importing EnhancedChatbotService...
✓ Successfully imported EnhancedChatbotService

[2/5] Initializing chatbot service...
✓ Successfully initialized chatbot service

[3/5] Starting MCP server subprocess...
✓ MCP server started and connected successfully

[4/5] Discovering available tools from server...
✓ Successfully discovered 36 tools (35 MCP + 1 schema)

[5/5] Checking MCP status...
✓ MCP Status:
  server_running: True
  server_pid: 12345
  tools_connected: True
```

## Configuration

All settings in `chatbot/config.py`:

```python
# MCP Server Settings
MCP_SERVER_PATH = Path(__file__).parent.parent / "mcp_server"
MCP_SERVER_STARTUP_TIMEOUT = 10  # seconds
MCP_CONNECTION_TIMEOUT = 5        # seconds

# Django Integration
USE_MCP_CHATBOT = os.getenv("USE_MCP_CHATBOT", "true").lower() == "true"
```

## Usage

### Start Django
```bash
python manage.py runserver
```

### Make Request
```bash
curl -X POST http://localhost:8000/finance/chatbot/send/ \
  -H "Content-Type: application/json" \
  -d '{"message": "How many companies do we have?"}'
```

### What Happens
1. Django receives request
2. EnhancedChatbotService checks if MCP server is running
3. If not, starts `server.py` as subprocess
4. Connects via JSON-RPC
5. Discovers tools
6. Calls OpenAI with tools
7. Executes tool calls via JSON-RPC
8. Returns response

## Server Lifecycle

- **Startup**: Automatic on first chatbot message
- **Running**: Stays alive between requests
- **Monitoring**: Health checks via psutil
- **Shutdown**: Automatic when Django stops
- **Recovery**: Auto-restart on failure (configurable)

## Debugging

### Check Server Process
```bash
# Linux/Mac
ps aux | grep server.py

# Windows
tasklist | findstr python
```

### View Server Logs
```python
import logging
logging.getLogger('chatbot.mcp_client').setLevel(logging.DEBUG)
```

### Test Server Independently
```bash
cd mcp_server
npx @modelcontextprotocol/inspector python server.py
# Open http://localhost:3000
```

## Environment Variables

```env
# Required
OPENAI_API_KEY=your_key_here

# Optional
USE_MCP_CHATBOT=true
CHATBOT_MODEL=gpt-4o-mini
MAX_TOOL_ITERATIONS=5
MAX_CONVERSATION_HISTORY=10
TOKEN_THRESHOLD_RATIO=0.7
```

## Next Steps

1. ✅ Architecture restored to subprocess-based
2. ✅ JSON-RPC communication implemented
3. ✅ Server lifecycle management ready
4. ✅ Testing script updated
5. ⏳ Run `test_mcp_setup.py` to verify
6. ⏳ Test with real queries
7. ⏳ Monitor server health in production

## Documentation

- **`MCP_SUBPROCESS_ARCHITECTURE.md`** - Architecture overview
- **`MCP_QUICKSTART.md`** - Quick start guide
- **`MCP_CHATBOT_INTEGRATION.md`** - Technical details
- **`SETUP_CHECKLIST.md`** - Implementation checklist

---

**The subprocess-based MCP integration is now fully implemented and ready to use!** 🚀
