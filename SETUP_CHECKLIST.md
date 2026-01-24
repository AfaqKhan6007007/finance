# Setup Checklist - MCP-Enhanced Chatbot

## Pre-Setup (Django Already Running)

- [x] Django application is running
- [x] SQLite database with test data exists
- [x] OpenAI API key configured
- [x] MCP server code exists in `mcp_server/`

## Installation

- [ ] `pip install tiktoken==0.8.0 psutil==6.1.1`

## Configuration

- [ ] Add to `.env`:
  ```env
  USE_MCP_CHATBOT=true
  CHATBOT_MODEL=gpt-4o-mini
  OPENAI_API_KEY=<your_key>
  ```

## Verification

- [ ] Run: `python test_mcp_setup.py`
- [ ] Output shows: "✓ All tests passed!"
- [ ] 36 tools discovered

## Testing

- [ ] Start Django: `python manage.py runserver`
- [ ] POST to `/finance/chatbot/send/`
- [ ] Test query 1: `"How many companies do we have?"`
  - Expected: Real number from database
- [ ] Test query 2: `"List asset accounts"`
  - Expected: Actual accounts with balances
- [ ] Test query 3: `"What fields are in the invoice table?"`
  - Expected: Schema information

## Documentation Review

- [ ] Read `MCP_QUICKSTART.md` for usage examples
- [ ] Read `MCP_CHATBOT_INTEGRATION.md` for details
- [ ] Read `MCP_IMPLEMENTATION_SUMMARY.md` for architecture

## Customization (Optional)

- [ ] Edit `chatbot/config.py` for token limits
- [ ] Adjust `MAX_CONVERSATION_HISTORY` if needed
- [ ] Enable/disable logging as needed
- [ ] Configure `CHATBOT_MODEL` for cost/performance

## Production Checklist

- [ ] Test error handling (give invalid queries)
- [ ] Monitor token usage (set `LOG_TOKEN_USAGE=True`)
- [ ] Test conversation pruning (long conversations)
- [ ] Test fallback mode (set `USE_MCP_CHATBOT=false`)
- [ ] Review logs for warnings/errors
- [ ] Test on real user queries
- [ ] Monitor API costs

## Troubleshooting Quick Links

If you encounter issues:

1. **Tools not loading**: Check `test_mcp_setup.py` output
2. **High token usage**: Reduce `MAX_CONVERSATION_HISTORY`
3. **Slow responses**: Check tool call timeouts
4. **API errors**: Verify OpenAI API key
5. **Database errors**: Check Django models are correct

## Success Indicators

✅ Setup Complete When:
- [ ] `test_mcp_setup.py` passes all tests
- [ ] Chatbot responds with real database data
- [ ] No errors in Django console
- [ ] Token usage is reasonable
- [ ] Responses are fast (< 3 seconds)

## Support Files

- `MCP_QUICKSTART.md` - Quick start guide with examples
- `MCP_CHATBOT_INTEGRATION.md` - Comprehensive technical docs
- `MCP_IMPLEMENTATION_SUMMARY.md` - Architecture overview
- `test_mcp_setup.py` - Automated verification script

## Key Points to Remember

1. **No separate MCP server needed** - Tools are imported directly
2. **Django starts the chatbot** - Initialize on first request
3. **36 tools available** - All accessible to OpenAI function calling
4. **Token-optimized** - Schemas loaded on-demand
5. **Backward compatible** - Can disable with `USE_MCP_CHATBOT=false`

## Next Steps After Setup

1. Test with real queries
2. Monitor performance and costs
3. Adjust configuration based on usage
4. Consider enabling detailed logging for debugging
5. Train users on chatbot capabilities

---

**Timeline**: 
- Installation: 2-3 minutes
- Verification: 1-2 minutes
- Testing: 5-10 minutes
- **Total: ~15 minutes from start to working chatbot**

Good luck! 🚀
