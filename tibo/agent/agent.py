import click
import time
import threading
import os
from tibo.agent.claude_agent import ClaudeAgent
from tibo.utils import ANTHROPIC_API_KEY
from tibo.agent.tools.search_tool import web_search
from tibo.agent.tools.terminal_tool import execute_command
from tibo.agent.tools.codebase_intteligence import get_relevant_code_files
from tibo.agent.tools.file_tool import modify_file

def start_agent_shell():
    """Start an interactive shell for the AI agent."""
    click.secho("\nStarting AI agent shell. Type 'exit' to quit.", fg="cyan", bold=True)
    agent = ClaudeAgent(anthropic_api_key=ANTHROPIC_API_KEY)

    try:
        while True:
            user_input = click.prompt(
                click.style("tibo-agent>", bold=True), 
                prompt_suffix="",
                type=str
            )
            if user_input.lower() in ["exit", "quit"]:
                click.secho("Exiting AI agent shell.", fg="cyan")
                break
            if user_input.lower() == "reset":
                agent.reset_conversation()
                click.secho("Conversation history reset.", fg="cyan")
                continue
            if user_input.startswith("#"):
                command = user_input[1:].strip()
                os.system(command)
                continue

            stop_animation = run_thinking_animation()
            
            try:
                response = agent.process_query(user_input, stop_animation, run_thinking_animation)
                # Stop the animation
                stop_animation()
                
                click.secho("Tibo: ", fg="green", bold=True, nl=False)
                click.echo(response)
                click.echo()
            except Exception as e:
                # Stop the animation
                stop_animation()
                
                click.secho(f"Error processing query: {e}", fg="red")

    except (KeyboardInterrupt, EOFError, click.Abort):
        click.secho("\nExiting AI agent shell.", fg="cyan")
    except Exception as e:
        click.secho(f"Unexpected error: {str(e)}", fg="red")



def run_thinking_animation():
    """
    Run an animated 'Thinking...' indicator with cycling dots in green.
    Returns a function to stop the animation.
    """
    thinking_animation_active = True
    
    def animate_thinking():
        dots = 0
        while thinking_animation_active:
            # Use click.secho with green color and overwrite the line
            click.echo("\r" + " " * 12 + "\r", nl=False)  # Clear previous line
            click.secho("Thinking" + "." * dots + " " * (3 - dots), fg="green", nl=False)
            dots = (dots + 1) % 4
            time.sleep(0.5)
        # Clear the line when animation stops
        click.echo("\r" + " " * 12 + "\r", nl=False)
    
    animation_thread = threading.Thread(target=animate_thinking)
    animation_thread.daemon = True
    animation_thread.start()
    
    def stop_animation():
        nonlocal thinking_animation_active
        thinking_animation_active = False
        animation_thread.join(1.0)  # Wait for thread to finish
        
    return stop_animation