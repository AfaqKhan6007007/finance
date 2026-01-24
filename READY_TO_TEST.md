# ✅ MCP Subprocess Integration - Ready to Test

## Current Status: READY

Your MCP chatbot integration is now using the **standard subprocess approach** with JSON-RPC communication over stdio.

## What Was Done

1. ✅ **Restored MCPServerManager** - Manages MCP server subprocess
2. ✅ **Updated MCPClientConnector** - JSON-RPC stdio communication
3. ✅ **Updated EnhancedChatbotService** - Uses subprocess architecture
4. ✅ **Updated test_mcp_setup.py** - Tests subprocess startup
5. ✅ **Created documentation** - Complete guides and comparisons

## Architecture Summary

```
Django Request
    ↓
EnhancedChatbotService
    ↓
MCPServerManager → Starts server.py as subprocess
    ↓
MCPClientConnector → Connects via JSON-RPC (stdin/stdout)
    ↓
OpenAI Function Calling → 36 tools (35 MCP + 1 schema)
    ↓
Tool Execution → JSON-RPC call to subprocess
    ↓
Response
```

## Quick Test (5 Minutes)

### Step 1: Install Dependencies
```bash
pip install tiktoken==0.8.0 psutil==6.1.1
```

### Step 2: Run Verification Script
```bash
python test_mcp_setup.py
```

**Expected Output:**
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
  server_uptime: 2.5
  tools_connected: True

✓ All tests passed! MCP server is running and tools are available.
```

### Step 3: Start Django
```bash
python manage.py runserver
```

### Step 4: Test Chatbot Endpoint
```bash
curl -X POST http://localhost:8000/finance/chatbot/send/ \
  -H "Content-Type: application/json" \
  -d '{"message": "How many companies do we have?"}'
```

## What Happens on First Request

1. **T=0s**: Request arrives
2. **T=0.5s**: MCPServerManager starts `server.py` as subprocess
3. **T=1.0s**: MCPClientConnector sends JSON-RPC initialize
4. **T=1.5s**: Connection established, tools discovered
5. **T=2.0s**: OpenAI API called with 36 tools
6. **T=4.0s**: Tool executed via JSON-RPC, result returned

**Total**: ~4-5 seconds for first message
**Subsequent**: ~2-3 seconds per message

## Verify Server is Running

### Check Process List
```bash
# Linux/Mac
ps aux | grep server.py

# Windows
tasklist | findstr python
```

### Check Django Logs
Look for:
```
INFO - Starting MCP server subprocess...
INFO - MCP server started successfully (PID: 12345)
INFO - Connected to MCP server successfully
INFO - Discovered 36 tools from MCP server
```

## Configuration

Create `.env` or set environment variables:

```env
# Required
OPENAI_API_KEY=your_api_key_here

# Optional (defaults shown)
USE_MCP_CHATBOT=true
CHATBOT_MODEL=gpt-4o-mini
MAX_TOOL_ITERATIONS=5
MAX_CONVERSATION_HISTORY=10
TOKEN_THRESHOLD_RATIO=0.7
```

## Test Queries to Try

Once Django is running, try these queries:

### 1. Company Queries
```json
{"message": "How many companies do we have?"}
{"message": "List all companies"}
{"message": "Search for companies with 'tech' in the name"}
```

### 2. Account Queries
```json
{"message": "Show me all asset accounts"}
{"message": "What's the balance of Cash account?"}
{"message": "List accounts under Expenses"}
```

### 3. Schema Queries
```json
{"message": "What fields are in the invoice table?"}
{"message": "Show me the company table schema"}
{"message": "What columns does the account table have?"}
```

### 4. Complex Queries
```json
{"message": "Find companies with invoices over $10,000"}
{"message": "Show me all unpaid invoices"}
{"message": "What's the total revenue this month?"}
```

## Troubleshooting

### Issue: "MCP server not running"
**Solution**: Check if `mcp_server/server.py` exists and is executable
```bash
ls -la mcp_server/server.py
python mcp_server/server.py  # Test manually
```

### Issue: "Failed to connect to MCP server"
**Solution**: Check subprocess communication
```bash
# Enable debug logging
export DJANGO_LOG_LEVEL=DEBUG
python manage.py runserver
```

### Issue: "Tool call failed"
**Solution**: Check tool is properly defined in server
```bash
cd mcp_server
npx @modelcontextprotocol/inspector python server.py
# Open http://localhost:3000 to test tools
```

### Issue: Server dies immediately
**Solution**: Check for import errors in tools
```bash
cd mcp_server
python server.py  # Run directly to see errors
```

## Monitoring Server Health

### Get Server Status
```python
from finance.services.chatbot_service_enhanced import EnhancedChatbotService
chatbot = EnhancedChatbotService()
status = chatbot.get_mcp_status()
print(status)
```

**Expected Output:**
```python
{
    'initialized': True,
    'server_running': True,
    'server_pid': 12345,
    'server_uptime': 120.5,  # seconds
    'connector_available': True,
    'tools_connected': True
}
```

### Server Lifecycle
- **Auto-start**: First chatbot message
- **Keep-alive**: Stays running between requests
- **Auto-shutdown**: When Django stops
- **Auto-restart**: On crash (if configured)

## Performance Tips

### 1. Keep Server Running
The server stays alive between requests for performance. First message is slower due to startup.

### 2. Monitor Memory
```python
status = chatbot.server_manager.get_health_status()
print(f"Memory: {status['memory_mb']} MB")
print(f"CPU: {status['cpu_percent']}%")
```

### 3. Optimize Token Usage
```python
# Set in config.py or .env
MAX_CONVERSATION_HISTORY=10  # Keep last 10 messages
TOKEN_THRESHOLD_RATIO=0.7     # Prune at 70% of limit
```

## Documentation Reference

| Document | Purpose |
|----------|---------|
| `MCP_SUBPROCESS_IMPLEMENTATION.md` | Complete implementation details |
| `MCP_SUBPROCESS_ARCHITECTURE.md` | Architecture and how it works |
| `MCP_APPROACHES_COMPARISON.md` | Subprocess vs Direct Import |
| `MCP_QUICKSTART.md` | Quick start guide |
| `MCP_CHATBOT_INTEGRATION.md` | Technical integration details |

## Success Checklist

- [ ] Dependencies installed (`tiktoken`, `psutil`)
- [ ] `test_mcp_setup.py` passes
- [ ] Django starts without errors
- [ ] Server subprocess starts on first message
- [ ] Tools discovered (36 total)
- [ ] Test query returns real data
- [ ] Server stays running between requests
- [ ] Cleanup works on Django shutdown

## Next Steps After Testing

1. **Monitor Performance**: Track response times and server health
2. **Add Error Handling**: Custom error messages for tool failures
3. **Implement Caching**: Cache frequent queries
4. **Add Logging**: Detailed logs for debugging
5. **Production Deploy**: Configure for production environment
6. **Load Testing**: Test with concurrent requests
7. **Optimize**: Tune configuration based on usage patterns

## Quick Commands Reference

```bash
# Install
pip install tiktoken psutil

# Test
python test_mcp_setup.py

# Run
python manage.py runserver

# Test endpoint
curl -X POST http://localhost:8000/finance/chatbot/send/ \
  -H "Content-Type: application/json" \
  -d '{"message": "How many companies?"}'

# Check process
ps aux | grep server.py

# View logs
tail -f logs/django.log  # if configured
```

---

## 🚀 You're Ready to Test!

Run `python test_mcp_setup.py` and see your MCP server come to life!

**The subprocess-based MCP integration is complete and ready for testing.**
