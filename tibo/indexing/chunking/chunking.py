import click
import ast
import os
import json
import re
from tree_sitter import Language, Parser
from .llm_pass import process_json_file
from ...utils import save_json, load_json_file, echo_success
from ...utils import PROJECT_STRUCTURE_PY_FILE_PATH, PROJECT_STRUCTURE_TS_FILE_PATH, FILE_CHUNKS_FILE_PATH, PROJECT_DETAILS_FILE_PATH
from .python.chunk_python import chunk_python_file
from .typescript.chunk_typescript import chunk_typescript_file


def chunk_project():
    click.secho("\nChunking project...", bold=True)
    
    # Load the project structure files if they exist
    project_files = {}
    if os.path.exists(PROJECT_STRUCTURE_PY_FILE_PATH):
        py_structure = load_json_file(PROJECT_STRUCTURE_PY_FILE_PATH)
        project_files.update(py_structure)
    if os.path.exists(PROJECT_STRUCTURE_TS_FILE_PATH):
        ts_structure = load_json_file(PROJECT_STRUCTURE_TS_FILE_PATH)
        project_files.update(ts_structure)

    if not project_files:
        print("No project structure files found. Expected at least one of project_structure_py.json or project_structure_ts.json.")
        exit(1)

    chunks_data = process_files(project_files)
    if not chunks_data:
        print("No valid files found to chunk from the project structures.")
        exit(1)
    
    save_json(chunks_data, FILE_CHUNKS_FILE_PATH)
    click.secho("OK - Successfully generated file chunks.")
    
    # Get project description and structure
    project_data = load_json_file(PROJECT_DETAILS_FILE_PATH)
    project_description = project_data["project_description"]
    project_structure = project_data["project_structure"]

    process_json_file(project_description, project_structure)
    click.secho("OK - Successfully enhanced chunk context.")  

    echo_success("Codebase files chunked and enhanced.") 



def process_files(project_files):
    result = {}
    for file_path in project_files.keys():
        file_path = os.path.abspath(file_path)
        # Skip if the file doesn't exist or matches ignore patterns
        if not os.path.exists(file_path):
            continue
        
        # Process based on file extension
        if file_path.endswith('.py'):
            result[file_path] = chunk_python_file(file_path)
        elif file_path.endswith(('.ts', '.tsx', '.js', '.jsx')) and not file_path.endswith('.d.ts'):
            result[file_path] = chunk_typescript_file(file_path)
        elif file_path.endswith('.json'):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            result[file_path] = [{"code-chunk": content, "en-chunk": "", "chunk-path": file_path}]
    return result