import click
import os
from .call_graph import generate_call_graph
from .chunking import chunk_project
from .vector_db import save_to_vector_db
from ..utils import PROJECT_DESCRIPTION_FILE_PATH

def index_project(path):
    click.secho(f"Indexing project at: {path}")

    if not os.path.exists(PROJECT_DESCRIPTION_FILE_PATH):
        # ask user for optional project description
        project_description = input("Enter a short description of the project to improve indexing (optional): \n")

    
    generate_call_graph(path)

    chunk_data = chunk_project(path)

    save_to_vector_db(chunk_data)





            
