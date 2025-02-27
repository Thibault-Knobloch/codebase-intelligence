import click
import os
import sys
from dotenv import load_dotenv
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
        save_api_key(new_api_key)
        click.echo("OK - API key updated successfully. Saved to ~/.tibo.env")
    else:
        if api_key:
            click.echo("OK - No new API key provided. Configuration unchanged.")
        else:
            click.secho("WARN - OPENAI API key not set. Indexing not possible.", fg="yellow")
            sys.exit()


def save_api_key(api_key):
    """Save the API key to the config file."""
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        f.write(f"OPENAI_API_KEY={api_key}\n")
