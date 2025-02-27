import click
import os
import sys
from dotenv import load_dotenv
from pathlib import Path
from tibo.indexing.indexing import index_project
from tibo.fetching.fetching import fetch_query
from tibo.config.config import config_project
from tibo.utils import CONFIG_PATH

@click.group()
def cli():
    pass

@cli.command()
def index():
    """Index a project directory."""

    # check prerequisite env variables
    load_dotenv(CONFIG_PATH)
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        click.secho(f"WARN - No OPENAI API key found. Run 'tibo config' to set it up.", fg="yellow")
        sys.exit()

    # get root path (we want to index the directpry this command runs in)
    project_root = Path.cwd()

    # make sure .tibo directory exists for storing outputs
    tibo_dir = project_root / ".tibo"
    tibo_dir.mkdir(exist_ok=True)

    # start index project
    click.secho("\nStarting project indexing. Hang tight!", fg="cyan", bold=True)
    try:
        index_project(project_root)
        click.secho("\n✅ Indexing complete!\n", fg="green", bold=True)

    except Exception as e:
        click.secho(f"\n❌ Error during indexing: {e}\n", fg="red", bold=True)
        sys.exit(1)

@cli.command()
@click.argument("query", required=False)
def fetch(query):
    """Fetch relevant chunks based on a user query."""
    if not query:
        click.secho("WARN - Please provide a query.")
        click.secho("Usage: tibo fetch <query>", fg="yellow")
        sys.exit(1)
    click.secho("\nSearching codebase...", fg="cyan", bold=True)
    
    try:
        # start fetching
        fetch_query(query)
        click.secho("\n✅ Relevant context fetched!\n", fg="green", bold=True)
    except Exception as e:
        click.secho(f"\n❌ Error during search: {e}\n", fg="red", bold=True)
        sys.exit(1)

@cli.command()
def config():
    """Configure the required environment variables."""
    click.secho("\nConfiguring project...", fg="cyan", bold=True)
    config_project()
    click.secho("\n✅ Project configured!\n", fg="green", bold=True)


if __name__ == '__main__':
    cli()