import os
import anthropic
from typing import Optional

class ClaudeAgent:
    """Agent that uses Claude API to process user queries."""
    
    def __init__(self):
        """Initialize the Claude agent with API key from environment."""
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-3-sonnet-20240229"  # Default model
        self.conversation_history = []
    
    def process_query(self, query: str) -> str:
        """Process a user query through Claude and return the response."""
        # Add user message to history
        self.conversation_history.append({"role": "user", "content": query})
        
        # Create messages for the API call
        messages = self.conversation_history.copy()
        
        # Call Claude API
        response = self.client.messages.create(
            model=self.model,
            messages=messages,
            max_tokens=1024
        )
        
        # Extract the response content
        assistant_message = response.content[0].text
        
        # Add assistant response to history
        self.conversation_history.append({"role": "assistant", "content": assistant_message})
        
        return assistant_message
    
    def reset_conversation(self) -> None:
        """Reset the conversation history."""
        self.conversation_history = []
