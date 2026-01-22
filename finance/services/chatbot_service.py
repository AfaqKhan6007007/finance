"""
Chatbot Service Layer
Decoupled service for handling OpenAI API interactions and conversation management.
"""
from openai import OpenAI
from django.conf import settings
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class ChatbotService:
    """
    Service class for managing chatbot conversations using OpenAI API.
    Handles conversation context, memory management, and API interactions.
    """
    
    # Configuration
    MAX_CONVERSATION_HISTORY = 20  # Keep last 20 messages for context
    MODEL = "gpt-3.5-turbo"  # Using GPT-3.5 for cost efficiency
    SYSTEM_PROMPT = """You are a helpful assistant for a financial management system. 
You can help users with questions about accounting, invoices, suppliers, customers, 
budgets, cost centers, journal entries, and tax management. Be concise and professional."""
    
    def __init__(self):
        """Initialize OpenAI client with API key from settings."""
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    def get_conversation_from_session(self, session: dict) -> List[Dict[str, str]]:
        """
        Retrieve conversation history from Django session.
        
        Args:
            session: Django session object
            
        Returns:
            List of message dicts with 'role' and 'content' keys
        """
        return session.get('chatbot_conversation', [])
    
    def save_conversation_to_session(self, session: dict, conversation: List[Dict[str, str]]) -> None:
        """
        Save conversation history to Django session.
        Limits conversation to MAX_CONVERSATION_HISTORY messages.
        
        Args:
            session: Django session object
            conversation: List of message dicts
        """
        # Keep only the last MAX_CONVERSATION_HISTORY messages
        if len(conversation) > self.MAX_CONVERSATION_HISTORY:
            # Keep system message if exists + last N messages
            system_messages = [msg for msg in conversation if msg.get('role') == 'system']
            user_assistant_messages = [msg for msg in conversation if msg.get('role') != 'system']
            conversation = system_messages + user_assistant_messages[-self.MAX_CONVERSATION_HISTORY:]
        
        session['chatbot_conversation'] = conversation
        session.modified = True
    
    def clear_conversation(self, session: dict) -> None:
        """
        Clear conversation history from session.
        
        Args:
            session: Django session object
        """
        if 'chatbot_conversation' in session:
            del session['chatbot_conversation']
            session.modified = True
    
    def send_message(self, user_message: str, session: dict) -> Dict[str, any]:
        """
        Send a message to the chatbot and get a response.
        Maintains conversation context from session.
        
        Args:
            user_message: The user's input message
            session: Django session object for storing conversation
            
        Returns:
            Dict with 'success', 'response', and optional 'error' keys
        """
        try:
            # Get existing conversation or start new one
            conversation = self.get_conversation_from_session(session)
            
            # Add system prompt if this is the first message
            if not conversation:
                conversation.append({
                    'role': 'system',
                    'content': self.SYSTEM_PROMPT
                })
            
            # Add user message to conversation
            conversation.append({
                'role': 'user',
                'content': user_message
            })
            
            # Call OpenAI API with conversation history
            response = self.client.chat.completions.create(
                model=self.MODEL,
                messages=conversation,
                temperature=0.7,
                max_tokens=500
            )
            
            # Extract assistant's response
            assistant_message = response.choices[0].message.content
            
            # Add assistant response to conversation
            conversation.append({
                'role': 'assistant',
                'content': assistant_message
            })
            
            # Save updated conversation to session
            self.save_conversation_to_session(session, conversation)
            
            return {
                'success': True,
                'response': assistant_message,
                'conversation_length': len(conversation)
            }
            
        except Exception as e:
            logger.error(f"Chatbot service error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'response': "I'm sorry, I encountered an error. Please try again."
            }
    
    def get_conversation_history(self, session: dict, include_system: bool = False) -> List[Dict[str, str]]:
        """
        Get conversation history for display.
        
        Args:
            session: Django session object
            include_system: Whether to include system messages
            
        Returns:
            List of message dicts (without system messages by default)
        """
        conversation = self.get_conversation_from_session(session)
        
        if not include_system:
            # Filter out system messages for UI display
            conversation = [msg for msg in conversation if msg.get('role') != 'system']
        
        return conversation
