# Chatbot Implementation Documentation

## Overview
A floating chatbot widget integrated into the Finance Management System with OpenAI-powered responses and session-based short-term memory.

---

## Architecture

### 1. **Service Layer (Decoupled Logic)**
**File:** `finance/services/chatbot_service.py`

**Purpose:** Handles all business logic and OpenAI API interactions independently from views.

**Key Features:**
- OpenAI GPT-3.5-turbo integration
- Session-based conversation management (no database)
- Automatic conversation history limiting (max 20 messages)
- Error handling and logging

**Methods:**
```python
ChatbotService.send_message(user_message, session)
    - Sends message to OpenAI
    - Maintains conversation context
    - Returns response dict

ChatbotService.get_conversation_history(session)
    - Retrieves conversation from session
    - Filters out system messages for UI

ChatbotService.clear_conversation(session)
    - Clears session data
```

**Configuration:**
- `MAX_CONVERSATION_HISTORY = 20` - Memory limit
- `MODEL = "gpt-3.5-turbo"` - AI model
- `SYSTEM_PROMPT` - Bot personality/role definition

---

### 2. **View Layer (API Endpoints)**
**File:** `finance/views.py`

**Endpoints:**

#### POST `/finance/chatbot/send/`
- Receives user message
- Calls ChatbotService
- Returns JSON response
- Requires login

#### GET `/finance/chatbot/history/`
- Retrieves conversation history
- Returns array of messages
- Requires login

#### POST `/finance/chatbot/clear/`
- Clears conversation
- Returns success status
- Requires login

**Request/Response Format:**
```javascript
// Send Message
Request: { "message": "Hello" }
Response: { "success": true, "response": "Hi! How can I help?" }

// Get History
Response: { "success": true, "conversation": [
    { "role": "user", "content": "Hello" },
    { "role": "assistant", "content": "Hi!" }
]}

// Clear
Response: { "success": true, "message": "Conversation cleared" }
```

---

### 3. **URL Configuration**
**File:** `finance/urls.py`

```python
path('chatbot/send/', chatbot_send_message, name='finance-chatbot-send')
path('chatbot/history/', chatbot_get_history, name='finance-chatbot-history')
path('chatbot/clear/', chatbot_clear_conversation, name='finance-chatbot-clear')
```

---

### 4. **Frontend Components**

#### HTML Template
**File:** `finance/templates/finance/chatbot_widget.html`

**Structure:**
```
chatbot-widget (container)
├── chatbot-toggle-btn (floating button)
└── chatbot-window (popup)
    ├── chatbot-header (title, actions)
    ├── chatbot-messages (conversation)
    ├── chatbot-typing (indicator)
    └── chatbot-input-area (input + send)
```

**Features:**
- Floating button (bottom-right corner)
- Expandable chat window
- Welcome message
- Message history display
- Typing indicator
- Clear conversation button

#### CSS Styles
**File:** `finance/static/finance/css/chatbot.css`

**Features:**
- Gradient purple theme
- Smooth animations (slideUp, fadeIn, typingDot)
- Responsive design (mobile-friendly)
- Dark mode support
- Custom scrollbar
- Message bubbles (user vs assistant)

#### JavaScript
**File:** `finance/static/finance/js/chatbot.js`

**Features:**
- AJAX API calls with fetch()
- CSRF token handling
- Real-time UI updates
- Auto-scroll to bottom
- Typing indicator control
- Error handling
- Form submission
- Conversation history loading

**Key Functions:**
```javascript
toggleChat() - Open/close widget
sendMessage(message) - Send to API
addMessage(content, role) - Add to UI
loadConversationHistory() - Load from session
clearConversation() - Clear session
```

---

### 5. **Integration**
**File:** `finance/templates/finance/header.html`

**Includes:**
```html
<!-- CSS -->
<link rel="stylesheet" href="{% static 'finance/css/chatbot.css' %}">

<!-- Widget HTML -->
{% include 'finance/chatbot_widget.html' %}

<!-- JavaScript -->
<script src="{% static 'finance/js/chatbot.js' %}"></script>
```

**Result:** Widget appears on **all pages** that include header.html

---

## Data Flow

### Sending a Message
```
1. User types message → clicks send
2. JavaScript catches form submit
3. AJAX POST to /finance/chatbot/send/
4. View calls ChatbotService.send_message()
5. Service:
   - Gets conversation from session
   - Adds user message
   - Calls OpenAI API with full context
   - Gets assistant response
   - Adds to conversation
   - Saves to session
6. Returns JSON response
7. JavaScript adds messages to UI
8. Scrolls to bottom
```

### Memory Management
```
Session Storage:
session['chatbot_conversation'] = [
    { "role": "system", "content": "You are a helpful..." },
    { "role": "user", "content": "Hello" },
    { "role": "assistant", "content": "Hi!" },
    ...
]

Limits:
- Keep only last 20 messages
- Always preserve system prompt
- Auto-trim older messages
- Cleared on logout or manual clear
```

---

## Configuration

### Environment Variables
**Required in `.env`:**
```
OPENAI_API_KEY=sk-...
```

### Django Settings
**File:** `core/settings.py`
```python
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
```

### OpenAI Model
Change in `chatbot_service.py`:
```python
MODEL = "gpt-3.5-turbo"  # or "gpt-4" for better responses
```

### System Prompt
Customize bot behavior in `chatbot_service.py`:
```python
SYSTEM_PROMPT = """You are a helpful assistant for..."""
```

---

## Testing Guide

### 1. **Visual Test**
- ✅ Widget button appears bottom-right on all pages
- ✅ Click opens chat window
- ✅ Chat window has header, messages, input
- ✅ Close button works

### 2. **Functionality Test**
- ✅ Type message → sends successfully
- ✅ Receives OpenAI response
- ✅ Messages display correctly (user right, assistant left)
- ✅ Typing indicator shows during processing
- ✅ Auto-scrolls to bottom

### 3. **Memory Test**
- ✅ Send multiple messages
- ✅ Ask follow-up question referencing previous message
- ✅ Bot remembers context
- ✅ Refresh page → history persists
- ✅ Clear conversation → history gone

### 4. **Error Handling Test**
- ✅ Empty message → validation error
- ✅ Network error → shows error message
- ✅ OpenAI API error → graceful fallback

---

## Scalability Considerations

### Current Architecture Benefits
1. **Decoupled Service Layer**
   - Easy to swap OpenAI for other LLMs
   - Can add preprocessing/postprocessing
   - Testable independently

2. **Session-based Storage**
   - No database overhead
   - Fast read/write
   - Auto-expires with session

3. **Frontend Modularity**
   - Separate HTML, CSS, JS files
   - Easy to modify styling
   - Reusable widget pattern

### Future Enhancements (Easy to Add)

#### 1. **Database Persistence**
Replace session storage with ChatConversation/ChatMessage models:
```python
# In chatbot_service.py
def save_to_database(user, conversation):
    chat = ChatConversation.objects.create(user=user)
    for msg in conversation:
        ChatMessage.objects.create(
            conversation=chat,
            role=msg['role'],
            content=msg['content']
        )
```

#### 2. **Context-Aware Responses**
Add finance data to prompts:
```python
# In chatbot_service.py
def add_finance_context(user):
    recent_invoices = Invoice.objects.filter(
        created_by=user
    )[:5]
    context = f"User has {recent_invoices.count()} recent invoices..."
    return context
```

#### 3. **Multi-Language Support**
Detect language and respond accordingly:
```python
SYSTEM_PROMPT = """You can respond in English, Arabic, or Urdu..."""
```

#### 4. **Voice Input**
Add Web Speech API:
```javascript
// In chatbot.js
const recognition = new webkitSpeechRecognition();
recognition.onresult = (e) => {
    const transcript = e.results[0][0].transcript;
    sendMessage(transcript);
};
```

#### 5. **Analytics**
Track usage:
```python
# In views.py
def chatbot_send_message(request):
    # Log analytics
    logger.info(f"User {request.user} sent message at {timezone.now()}")
    ...
```

#### 6. **Function Calling**
Let bot query database:
```python
# In chatbot_service.py
functions = [
    {
        "name": "get_invoices",
        "description": "Get user's recent invoices",
        "parameters": {...}
    }
]
response = client.chat.completions.create(
    model=MODEL,
    messages=conversation,
    functions=functions,
    function_call="auto"
)
```

---

## File Structure
```
finance/
├── services/
│   ├── __init__.py
│   └── chatbot_service.py          # Business logic (decoupled)
│
├── static/finance/
│   ├── css/
│   │   └── chatbot.css             # Styles
│   └── js/
│       └── chatbot.js              # Frontend logic
│
├── templates/finance/
│   ├── chatbot_widget.html         # Widget HTML
│   └── header.html                 # Includes widget
│
├── views.py                         # API endpoints
└── urls.py                          # URL routing
```

---

## API Reference

### Send Message
```bash
curl -X POST http://localhost:8000/finance/chatbot/send/ \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: <token>" \
  -d '{"message": "What is an invoice?"}'
```

Response:
```json
{
  "success": true,
  "response": "An invoice is a document...",
  "conversation_length": 4
}
```

### Get History
```bash
curl http://localhost:8000/finance/chatbot/history/ \
  -H "X-CSRFToken: <token>"
```

Response:
```json
{
  "success": true,
  "conversation": [
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "Hi!"}
  ]
}
```

### Clear Conversation
```bash
curl -X POST http://localhost:8000/finance/chatbot/clear/ \
  -H "X-CSRFToken: <token>"
```

Response:
```json
{
  "success": true,
  "message": "Conversation cleared successfully"
}
```

---

## Troubleshooting

### Widget Not Appearing
- Check if header.html includes chatbot_widget.html
- Verify static files loaded: `python manage.py collectstatic`
- Check browser console for errors

### OpenAI API Errors
- Verify OPENAI_API_KEY in .env file
- Check API key validity
- Review OpenAI account billing/limits

### Session Not Persisting
- Ensure Django session middleware enabled
- Check SESSION_ENGINE in settings.py
- Verify session cookie not blocked

### Messages Not Sending
- Check browser Network tab for failed requests
- Verify CSRF token present
- Check Django logs for errors

---

## Performance Considerations

### Current Performance
- **Response Time:** 1-3 seconds (OpenAI API call)
- **Memory Usage:** Minimal (session storage only)
- **Database Impact:** Zero (no DB queries)

### Optimization Tips
1. **Reduce Token Usage:** Limit conversation history
2. **Cache Responses:** For common questions
3. **Stream Responses:** Use OpenAI streaming API
4. **Rate Limiting:** Prevent abuse
5. **Queue System:** For high traffic

---

## Security

### Current Security Measures
- ✅ Login required (`@login_required`)
- ✅ CSRF protection
- ✅ Input validation (max 500 chars)
- ✅ Session isolation (user-specific)

### Additional Security (Future)
- Rate limiting per user
- Content filtering
- API key rotation
- Audit logging

---

## Maintenance

### Regular Tasks
1. Monitor OpenAI API usage/costs
2. Review conversation logs for issues
3. Update system prompt for better responses
4. Check error logs

### Updates
- OpenAI library: `pip install --upgrade openai`
- Monitor for OpenAI API changes
- Test after Django upgrades

---

**Last Updated:** January 22, 2026
**Version:** 1.0
**Status:** Production Ready ✅
