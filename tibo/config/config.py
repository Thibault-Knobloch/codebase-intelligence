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



def config_local():
    """Configure local LLM settings."""
    load_dotenv(CONFIG_PATH)
    local_llm = os.getenv("LOCAL_LLM")
    
    if not local_llm:
        click.echo("INFO - No LOCAL_LLM settings found. Please configure it now.")
    else:
        current_setting = "enabled" if local_llm.lower() == "true" else "disabled"
        click.echo(f"INFO - Local LLM is currently {current_setting}. Enter a new value to change.")
    
    while True:
        use_local_input = input("Use local LLM? (y/n): ").strip().lower()
        if use_local_input in ['y', 'n']:
            break
        click.echo("Please enter 'y' or 'n'")
    
    new_local_llm = "True" if use_local_input == 'y' else "False"
    update_env_variable("LOCAL_LLM", new_local_llm)
    click.echo(f"OK - LOCAL_LLM set to {new_local_llm}. Saved to ~/.tibo.env")
    
    # If LOCAL_LLM is True, ask for the URL
    if new_local_llm == "True":
        local_model_name = os.getenv("LOCAL_MODEL_NAME")
        if not local_model_name:
            click.echo("INFO - No LOCAL_MODEL_NAME found. Please enter it here.")
        else:
            click.echo(f"INFO - LOCAL_MODEL_NAME already set to {local_model_name}. Enter a new name to edit.")
            
        new_local_model_name = input("Enter the name of your local LLM model: ")

        if new_local_model_name:
            update_env_variable("LOCAL_MODEL_NAME", new_local_model_name)
            click.echo("OK - LOCAL_MODEL_NAME updated successfully. Saved to ~/.tibo.env")
        else:
            if local_model_name:
                click.echo("OK - No new LOCAL_MODEL_NAME provided. Configuration unchanged.")
            else:
                click.secho("WARN - LOCAL_MODEL_NAME not set. Local LLM functionality may not work correctly.", fg="yellow")
                sys.exit()

        local_llm_url = os.getenv("LOCAL_LLM_URL")
        
        if not local_llm_url:
            click.echo("INFO - No LOCAL_LLM_URL found. Please enter it here.")
        else:
            click.echo(f"INFO - LOCAL_LLM_URL already set to {local_llm_url}. Enter a new URL to edit.")
        
        new_local_llm_url = input("Enter the URL for your local LLM (e.g., http://localhost:11434/api/generate): ")
        
        if new_local_llm_url:
            update_env_variable("LOCAL_LLM_URL", new_local_llm_url)
            click.echo("OK - LOCAL_LLM_URL updated successfully. Saved to ~/.tibo.env")
        else:
            if local_llm_url:
                click.echo("OK - No new LOCAL_LLM_URL provided. Configuration unchanged.")
            else:
                click.secho("WARN - LOCAL_LLM_URL not set. Local LLM functionality may not work correctly.", fg="yellow")
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