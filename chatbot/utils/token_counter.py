"""
Token Counter
Estimates token usage for conversation context management
"""
import tiktoken
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class TokenCounter:
    """
    Estimates token counts for messages and manages context windows.
    Uses tiktoken library for accurate counting.
    """
    
    def __init__(self, model: str = "gpt-4o-mini"):
        """
        Initialize token counter for a specific model.
        
        Args:
            model: OpenAI model name
        """
        self.model = model
        try:
            self.encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            logger.warning(f"Model {model} not found, using cl100k_base encoding")
            self.encoding = tiktoken.get_encoding("cl100k_base")
    
    def count_tokens(self, text: str) -> int:
        """
        Count tokens in a text string.
        
        Args:
            text: Input text
            
        Returns:
            Number of tokens
        """
        try:
            return len(self.encoding.encode(text))
        except Exception as e:
            logger.error(f"Error counting tokens: {e}")
            # Fallback: rough estimate (1 token ≈ 4 characters)
            return len(text) // 4
    
    def count_messages_tokens(self, messages: List[Dict[str, str]]) -> int:
        """
        Count total tokens in a conversation message list.
        Includes OpenAI's message formatting overhead.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            
        Returns:
            Total token count
        """
        try:
            total_tokens = 0
            
            for message in messages:
                # Add tokens for message structure
                total_tokens += 4  # Every message has: role, content, name (optional), function_call (optional)
                
                # Count tokens in content
                content = message.get('content', '')
                if content:
                    total_tokens += self.count_tokens(content)
                
                # Count role
                role = message.get('role', '')
                if role:
                    total_tokens += self.count_tokens(role)
            
            # Add 2 tokens for assistant reply priming
            total_tokens += 2
            
            return total_tokens
        
        except Exception as e:
            logger.error(f"Error counting message tokens: {e}")
            # Fallback estimate
            total_chars = sum(len(msg.get('content', '')) for msg in messages)
            return total_chars // 4
    
    def estimate_function_tokens(self, function_definition: Dict) -> int:
        """
        Estimate tokens used by a function definition.
        
        Args:
            function_definition: OpenAI function definition dict
            
        Returns:
            Estimated token count
        """
        import json
        function_str = json.dumps(function_definition)
        return self.count_tokens(function_str)
    
    def estimate_all_functions_tokens(self, functions: List[Dict]) -> int:
        """
        Estimate total tokens for all function definitions.
        
        Args:
            functions: List of function definitions
            
        Returns:
            Total estimated tokens
        """
        return sum(self.estimate_function_tokens(func) for func in functions)
    
    def prune_conversation(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int,
        keep_system: bool = True
    ) -> List[Dict[str, str]]:
        """
        Prune conversation history to fit within token limit.
        Keeps most recent messages and optionally preserves system message.
        
        Args:
            messages: List of conversation messages
            max_tokens: Maximum allowed tokens
            keep_system: Whether to always keep system message
            
        Returns:
            Pruned message list
        """
        if not messages:
            return []
        
        # Separate system messages from others
        system_messages = [msg for msg in messages if msg.get('role') == 'system']
        other_messages = [msg for msg in messages if msg.get('role') != 'system']
        
        # Start with system messages if keeping them
        result = system_messages.copy() if keep_system else []
        current_tokens = self.count_messages_tokens(result)
        
        # Add messages from most recent, working backwards
        for message in reversed(other_messages):
            message_tokens = self.count_messages_tokens([message])
            
            if current_tokens + message_tokens <= max_tokens:
                result.insert(len(system_messages) if keep_system else 0, message)
                current_tokens += message_tokens
            else:
                # Can't fit more messages
                break
        
        # Restore chronological order
        if keep_system and system_messages:
            # System messages stay at start, rest in order
            non_system = [msg for msg in result if msg.get('role') != 'system']
            result = system_messages + non_system
        
        logger.info(f"Pruned conversation from {len(messages)} to {len(result)} messages ({current_tokens} tokens)")
        
        return result
    
    def get_available_tokens(
        self,
        messages: List[Dict[str, str]],
        functions: List[Dict],
        model_limit: int = 16000,
        reserve_for_response: int = 1000
    ) -> int:
        """
        Calculate available tokens for new content.
        
        Args:
            messages: Current conversation messages
            functions: Function definitions
            model_limit: Model's context window size
            reserve_for_response: Tokens to reserve for assistant response
            
        Returns:
            Number of tokens available
        """
        used_tokens = self.count_messages_tokens(messages)
        function_tokens = self.estimate_all_functions_tokens(functions)
        
        available = model_limit - used_tokens - function_tokens - reserve_for_response
        
        return max(0, available)
    
    def should_prune(
        self,
        messages: List[Dict[str, str]],
        functions: List[Dict],
        threshold: float = 0.8,
        model_limit: int = 16000
    ) -> bool:
        """
        Check if conversation should be pruned based on token usage.
        
        Args:
            messages: Current messages
            functions: Function definitions
            threshold: Usage threshold (0.0-1.0) to trigger pruning
            model_limit: Model's context window
            
        Returns:
            True if pruning is recommended
        """
        used_tokens = self.count_messages_tokens(messages)
        function_tokens = self.estimate_all_functions_tokens(functions)
        total_used = used_tokens + function_tokens
        
        usage_ratio = total_used / model_limit
        
        return usage_ratio >= threshold
