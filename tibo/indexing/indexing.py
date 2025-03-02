import click
import os
from .call_graph_utils.call_graph import generate_call_graph, get_project_structure
from .chunking.chunking import chunk_project
from .vector_db import save_to_vector_db
from ..utils import PROJECT_DETAILS_FILE_PATH, save_json, TIBO_DIR

def index_project(path):
    click.secho(f"Indexing project at: {path}")

    if not os.path.exists(PROJECT_DETAILS_FILE_PATH):
        # ask user for optional project description
        project_description = input("Enter a short description of the project to improve indexing (optional): \n")
        project_structure = get_project_structure(path)
        project_data = {
            "project_description": project_description,
            "project_structure": project_structure
        }
        save_json(project_data, PROJECT_DETAILS_FILE_PATH)
        click.secho(f"Project details saved to {TIBO_DIR}")

    # generate and save call graphs
    generate_call_graph(path)

    # chunk project and keep mappings
    chunk_project()

    # save chunks to vector database
    save_to_vector_db()





            
