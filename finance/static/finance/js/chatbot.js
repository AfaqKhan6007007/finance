/**
 * Chatbot Widget JavaScript
 * Handles UI interactions and API communication for the chatbot
 * Version: 2.0 - Markdown Support Added
 */

(function() {
    'use strict';

    // DOM Elements
    const toggleBtn = document.getElementById('chatbot-toggle-btn');
    const closeBtn = document.getElementById('chatbot-close-btn');
    const clearBtn = document.getElementById('chatbot-clear-btn');
    const chatWindow = document.getElementById('chatbot-window');
    const messagesContainer = document.getElementById('chatbot-messages');
    const chatForm = document.getElementById('chatbot-form');
    const chatInput = document.getElementById('chatbot-input');
    const sendBtn = document.getElementById('chatbot-send-btn');
    const typingIndicator = document.getElementById('chatbot-typing');

    // State
    let isOpen = false;
    let isProcessing = false;

    // API Endpoints
    const API_ENDPOINTS = {
        send: '/finance/chatbot/send/',
        history: '/finance/chatbot/history/',
        clear: '/finance/chatbot/clear/'
    };

    // CSRF Token
    function getCsrfToken() {
        const csrfCookie = document.cookie
            .split('; ')
            .find(row => row.startsWith('csrftoken='));
        return csrfCookie ? csrfCookie.split('=')[1] : '';
    }

    // Toggle Chat Window
    function toggleChat() {
        isOpen = !isOpen;
        chatWindow.style.display = isOpen ? 'flex' : 'none';
        
        if (isOpen) {
            chatInput.focus();
            loadConversationHistory();
        }
    }

    // Simple Markdown Parser (converts common markdown syntax to HTML)
    function parseMarkdown(text) {
        if (!text) return '';
        
        // Escape HTML to prevent XSS
        let html = text
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;');
        
        // Parse markdown syntax (order matters!)
        html = html
            // Headers (must come before bold/italic)
            .replace(/^### (.+)$/gm, '<h3>$1</h3>')
            .replace(/^## (.+)$/gm, '<h2>$1</h2>')
            .replace(/^# (.+)$/gm, '<h1>$1</h1>')
            // Bold: **text** or __text__ (must come before italic)
            .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
            .replace(/__(.+?)__/g, '<strong>$1</strong>')
            // Italic: *text* or _text_
            .replace(/\*(?!\*)(.+?)\*/g, '<em>$1</em>')
            .replace(/_(?!_)(.+?)_/g, '<em>$1</em>')
            // Code: `code`
            .replace(/`(.+?)`/g, '<code>$1</code>')
            // Links: [text](url)
            .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>');
        
        // Don't convert lines with "- Something:" to lists (they're just formatting)
        // Only convert actual list items that don't have colons immediately after
        // Line breaks - preserve as-is, don't try to parse lists
        html = html.replace(/\n/g, '<br>');
        
        return html;
    }

    // Add Message to UI
    function addMessage(content, role) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('chatbot-message');
        messageDiv.classList.add(role === 'user' ? 'chatbot-message-user' : 'chatbot-message-assistant');
        
        // For assistant messages, parse markdown. For user messages, keep as plain text.
        if (role === 'assistant') {
            messageDiv.innerHTML = parseMarkdown(content);
        } else {
            messageDiv.textContent = content;
        }
        
        messagesContainer.appendChild(messageDiv);
        scrollToBottom();
    }

    // Add Error Message
    function addErrorMessage(errorText) {
        const errorDiv = document.createElement('div');
        errorDiv.classList.add('chatbot-error-message');
        errorDiv.textContent = `⚠️ ${errorText}`;
        
        messagesContainer.appendChild(errorDiv);
        scrollToBottom();
    }

    // Show/Hide Typing Indicator
    function setTypingIndicator(show) {
        typingIndicator.style.display = show ? 'flex' : 'none';
        if (show) {
            scrollToBottom();
        }
    }

    // Scroll to Bottom of Messages
    function scrollToBottom() {
        setTimeout(() => {
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }, 100);
    }

    // Load Conversation History
    async function loadConversationHistory() {
        try {
            const response = await fetch(API_ENDPOINTS.history, {
                method: 'GET',
                headers: {
                    'X-CSRFToken': getCsrfToken()
                }
            });

            const data = await response.json();

            if (data.success && data.conversation && data.conversation.length > 0) {
                // Clear existing messages except welcome message
                const welcomeMsg = messagesContainer.querySelector('.chatbot-welcome-message');
                messagesContainer.innerHTML = '';
                if (welcomeMsg) {
                    messagesContainer.appendChild(welcomeMsg);
                }

                // Add historical messages
                data.conversation.forEach(msg => {
                    addMessage(msg.content, msg.role);
                });
            }
        } catch (error) {
            console.error('Error loading conversation history:', error);
        }
    }

    // Send Message
    async function sendMessage(message) {
        if (!message.trim() || isProcessing) {
            return;
        }

        isProcessing = true;
        sendBtn.disabled = true;
        chatInput.disabled = true;

        // Add user message to UI
        addMessage(message, 'user');
        chatInput.value = '';

        // Show typing indicator
        setTypingIndicator(true);

        try {
            const response = await fetch(API_ENDPOINTS.send, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                },
                body: JSON.stringify({ message: message })
            });

            const data = await response.json();

            // Hide typing indicator
            setTypingIndicator(false);

            if (data.success) {
                // Add assistant response to UI
                addMessage(data.response, 'assistant');
            } else {
                // Show error message
                addErrorMessage(data.error || 'Failed to get response. Please try again.');
            }

        } catch (error) {
            console.error('Error sending message:', error);
            setTypingIndicator(false);
            addErrorMessage('Network error. Please check your connection and try again.');
        } finally {
            isProcessing = false;
            sendBtn.disabled = false;
            chatInput.disabled = false;
            chatInput.focus();
        }
    }

    // Clear Conversation
    async function clearConversation() {
        if (!confirm('Are you sure you want to clear the conversation?')) {
            return;
        }

        try {
            const response = await fetch(API_ENDPOINTS.clear, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCsrfToken()
                }
            });

            const data = await response.json();

            if (data.success) {
                // Clear messages except welcome message
                const welcomeMsg = messagesContainer.querySelector('.chatbot-welcome-message');
                messagesContainer.innerHTML = '';
                if (welcomeMsg) {
                    messagesContainer.appendChild(welcomeMsg);
                }

                // Show success message
                const successDiv = document.createElement('div');
                successDiv.classList.add('chatbot-message-assistant');
                successDiv.textContent = '✅ Conversation cleared successfully!';
                messagesContainer.appendChild(successDiv);
                
                setTimeout(() => {
                    successDiv.remove();
                }, 3000);

            } else {
                addErrorMessage('Failed to clear conversation.');
            }

        } catch (error) {
            console.error('Error clearing conversation:', error);
            addErrorMessage('Failed to clear conversation.');
        }
    }

    // Event Listeners
    toggleBtn.addEventListener('click', toggleChat);
    closeBtn.addEventListener('click', toggleChat);
    clearBtn.addEventListener('click', clearConversation);

    chatForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const message = chatInput.value.trim();
        if (message) {
            sendMessage(message);
        }
    });

    // Allow Enter key to send message
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            chatForm.dispatchEvent(new Event('submit'));
        }
    });

    // Close chat window when clicking outside (optional)
    document.addEventListener('click', (e) => {
        if (isOpen && 
            !chatWindow.contains(e.target) && 
            !toggleBtn.contains(e.target)) {
            // Uncomment to enable click-outside-to-close
            // toggleChat();
        }
    });

    // Initialize
    console.log('Chatbot widget initialized');

})();
