# MCP-Enhanced Chatbot - Quick Start Guide

## Setup

### 1. Install Dependencies

```bash
cd "d:\Machine Learning\JFF JOB\finance"
source venv/Scripts/activate  # On Windows: venv\Scripts\activate
pip install tiktoken==0.8.0 psutil==6.1.1
```

### 2. Configure Environment

Add to `.env` file:
```env
USE_MCP_CHATBOT=true
CHATBOT_MODEL=gpt-4o-mini
OPENAI_API_KEY=your_api_key_here
```

### 3. Start Django Application

That's it! The chatbot will automatically load MCP tools when needed.

```bash
python manage.py runserver
```

The MCP tools are called directly via imports - **no separate server process needed** for local Django integration.

### 4. Test the Chatbot

**API Endpoint**: `POST /finance/chatbot/send/`

**Request**:
```json
{
  "message": "How many companies do we have?"
}
```

**Response**:
```json
{
  "success": true,
  "response": "You have 5 companies in the system.",
  "tool_calls_made": 1,
  "mcp_available": true
}
```

## Example Queries to Test

### Basic Queries
1. "List all companies"
2. "How many customers do we have?"
3. "Show me suppliers from India"

### Schema Discovery
4. "What fields are in the account table?"
5. "Tell me about the invoice schema"

### Filtered Queries
6. "Show me asset accounts with balance over $5000"
7. "List paid invoices from 2025"
8. "Find customers in USA"

### Statistics
9. "What are the invoice statistics?"
10. "Get financial summary for company ID 1"

## Troubleshooting

### Error: "Failed to connect to MCP tools"

**Check 1**: Verify MCP tools path
```python
# In chatbot/config.py, check:
MCP_TOOLS_PATH = Path(__file__).resolve().parent.parent / "mcp_server" / "tools"
# This path must exist and contain: company_tools.py, account_tools.py, etc.
```

**Check 2**: Ensure Django is properly configured
```python
# In Django shell:
python manage.py shell
>>> import sys
>>> sys.path
# MCP server parent should be in path
```

### Error: "Tool not found"

**Solution**: One of the tool imports failed. Check for import errors:
```bash
cd mcp_server
python -c "from tools.company_tools import list_companies; print('OK')"
```

### Error: "Module 'chatbot' not found"

**Solution**: Ensure project structure is correct
```bash
ls -la chatbot/
# Should show: __init__.py, config.py, mcp_client/, schema_tools/, etc.
```

### Error: Token limit exceeded

**Solution**: Reduce conversation history
```python
# In chatbot/config.py:
MAX_CONVERSATION_HISTORY = 5  # Reduce from 10
```

### High API costs

**Solution**: Use cheaper model
```env
# In .env:
CHATBOT_MODEL=gpt-4o-mini  # Cheapest option
# Or: CHATBOT_MODEL=gpt-3.5-turbo  # Even cheaper
```

## Disable MCP (Fallback to Basic Mode)

To revert to the original simple chatbot:

```env
# In .env:
USE_MCP_CHATBOT=false
```

This uses the original `ChatbotService` without MCP tools.

## Monitoring

### Check MCP Server Status

```python
from finance.services.chatbot_service_enhanced import EnhancedChatbotService
chatbot = EnhancedChatbotService()
status = chatbot.get_mcp_status()
print(status)
# Output: {'running': True, 'uptime': 123.45, 'pid': 12345, 'memory_mb': 45.2, 'cpu_percent': 0.5}
```

### View Token Usage

Enable in `chatbot/config.py`:
```python
LOG_TOKEN_USAGE = True
```

Check Django logs for:
```
INFO Conversation tokens: 523
INFO Token threshold reached, pruning conversation
```

## Configuration Options

Edit `chatbot/config.py` for fine-tuning:

```python
# Token limits
MAX_CONVERSATION_HISTORY = 10  # Messages to keep
CHATBOT_MAX_TOKENS = 800  # Max response length

# Performance
TOOL_CALL_TIMEOUT = 15  # Seconds per tool call
MAX_PARALLEL_TOOL_CALLS = 3  # Parallel executions

# Caching
ENABLE_TOOL_CACHING = True
SCHEMA_CACHE_TTL = 600  # 10 minutes

# Safety
MAX_TOOL_CALLS_PER_MESSAGE = 5  # Prevent runaway
FALLBACK_TO_BASIC_MODE = True  # Continue if MCP fails
```

## Performance Tips

1. **Use Minimal Schema Mode**: Returns only key fields
   ```python
   MINIMAL_SCHEMA_MODE = True
   ```

2. **Enable Caching**: Reduces repeated queries
   ```python
   ENABLE_TOOL_CACHING = True
   SCHEMA_CACHE_ENABLED = True
   ```

3. **Optimize Conversation History**: Keep only recent messages
   ```python
   MAX_CONVERSATION_HISTORY = 5
   ```

4. **Use gpt-4o-mini**: Best cost/performance ratio
   ```env
   CHATBOT_MODEL=gpt-4o-mini
   ```

## Next Steps

1. ✅ Test basic queries
2. ✅ Test schema discovery
3. ✅ Test filtering and pagination
4. ✅ Monitor token usage
5. ✅ Adjust configuration based on usage patterns

## Support

For issues or questions:
1. Check `MCP_CHATBOT_INTEGRATION.md` for detailed documentation
2. Review logs in Django console
3. Test MCP server independently with `npx @modelcontextprotocol/inspector`

## Success Checklist

- [ ] Dependencies installed
- [ ] Environment variables set
- [ ] MCP server starts without errors
- [ ] Django application runs
- [ ] Chatbot responds to test query
- [ ] Tool calls execute successfully
- [ ] Token usage is reasonable
- [ ] Configuration optimized for your use case

Congratulations! Your MCP-enhanced chatbot is ready to use! 🎉
