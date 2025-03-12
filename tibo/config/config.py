import click
import os
import sys
from dotenv import load_dotenv, dotenv_values
from ..utils import CONFIG_PATH


def config_project():
    """Configure the project."""
    load_dotenv(CONFIG_PATH)
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        click.echo(f"INFO - No OPENAI API key found. Please enter it here.")
    else:
        click.echo(f"INFO - OPENAI API key already setup. Enter a new key here to edit.") 
    
    new_api_key = input("Enter your OPENAI API key: ")
    # if api key not empty, save it
    if new_api_key:
        update_env_variable("OPENAI_API_KEY", new_api_key)
        click.echo("OK - API key updated successfully. Saved to ~/.tibo.env")
    else:
        if api_key:
            click.echo("OK - No new API key provided. Configuration unchanged.")
        else:
            click.secho("WARN - OPENAI API key not set. Indexing not possible.", fg="yellow")
            sys.exit()
    
    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
    if not anthropic_api_key:
        click.echo(f"INFO - No Anthropic API key found. Please enter it here.")
    else:
        click.echo(f"INFO - Anthropic API key already setup. Enter a new key here to edit.")

    new_anthropic_api_key = input("Enter your ANTHROPIC API key: ")
    if new_anthropic_api_key:
        update_env_variable("ANTHROPIC_API_KEY", new_anthropic_api_key)
        click.echo("OK - Anthropic API key updated successfully. Saved to ~/.tibo.env")
    else:
        if anthropic_api_key:
            click.echo("OK - No new Anthropic API key provided. Configuration unchanged.")
        else:
            click.secho("WARN - Anthropic API key not set. Agent functionality not available.", fg="yellow")
    
    if not anthropic_api_key and not api_key:
        sys.exit()

def update_env_variable(key, value):
    """Update a single environment variable in the config file."""
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    
    # Read existing environment variables or create empty dict if file doesn't exist
    env_vars = {}
    if os.path.exists(CONFIG_PATH):
        env_vars = dotenv_values(CONFIG_PATH)
    
    # Update the specified key
    env_vars[key] = value
    
    # Write back to the file
    with open(CONFIG_PATH, "w") as f:
        for k, v in env_vars.items():
            f.write(f"{k}={v}\n")
