import click
import os
from tibo.agent.claude_agent import ClaudeAgent

def start_agent_shell():
    """Start an interactive shell for the AI agent."""
    click.secho("\nStarting AI agent shell. Type 'exit' to quit.", fg="cyan", bold=True)
    agent = ClaudeAgent()
    
    try:
        while True:
            # Get user input with a prompt
            user_input = click.prompt("tibo-agent", prompt_suffix="> ", type=str)
            
            # Check if user wants to exit
            if user_input.lower() in ["exit", "quit"]:
                click.secho("Exiting AI agent shell.", fg="cyan")
                break
            
            # Check if user wants to reset conversation
            if user_input.lower() == "reset":
                agent.reset_conversation()
                click.secho("Conversation history reset.", fg="cyan")
                continue
                
            try:
                # Process the query with Claude
                click.secho("Thinking...", fg="cyan")
                response = agent.process_query(user_input)
                
                # Display the response
                click.secho("Tibo:", fg="green", bold=True, nl=False)
                click.echo(response)
                click.echo()  # Add a blank line for readability
            except Exception as e:
                click.secho(f"Error processing query: {e}", fg="red")
    
    except (KeyboardInterrupt, EOFError, click.Abort):
        click.secho("\nExiting AI agent shell.", fg="cyan")
    except Exception as e:
        # Handle other exceptions
        click.secho(f"Unexpected error: {str(e)}", fg="red")
