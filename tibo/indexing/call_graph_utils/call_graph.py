import click
import sys
import os
from ...utils import save_json, echo_success
from ...utils import PROJECT_STRUCTURE_PY_FILE_PATH, CALL_GRAPH_PY_FILE_PATH, CALL_GRAPH_PY_IMAGE_PATH, TIBO_PYTHON_DIR
from ...utils import PROJECT_STRUCTURE_TS_FILE_PATH, CALL_GRAPH_TS_FILE_PATH, CALL_GRAPH_TS_IMAGE_PATH, TIBO_TYPESCRIPT_DIR
from .python.call_graph_py import extract_python_project_structure_and_call_graph, save_call_graph_image
from .typescript.call_graph_ts import extract_ts_project_structure_and_call_graph

def generate_call_graph(path):
    click.secho("\nGenerating call graphs...", bold=True)
    
    # extract project structure and call graph for python files
    project_structure_py, call_graph_py = extract_python_project_structure_and_call_graph(path)
    
    if not project_structure_py and not call_graph_py:
        click.secho(f"INFO - No Python files found - nothing to save.", fg="yellow")
    else:
        # save python project structure and call graph to output directory
        save_json(project_structure_py, PROJECT_STRUCTURE_PY_FILE_PATH)
        save_json(call_graph_py, CALL_GRAPH_PY_FILE_PATH)
        save_call_graph_image(call_graph_py, CALL_GRAPH_PY_IMAGE_PATH)
        click.secho(f"OK - Python project structure and call graph saved to {TIBO_PYTHON_DIR}.")
    
    
     # extract project structure and call graph for python files
    project_structure_ts, call_graph_ts = extract_ts_project_structure_and_call_graph(path)

    if not project_structure_ts and not call_graph_ts:
        click.secho(f"INFO - No TypeScript files found - nothing to save.", fg="yellow")
    else:
        # save typescript project structure and call graph to output directory
        save_json(project_structure_ts, PROJECT_STRUCTURE_TS_FILE_PATH)
        save_json(call_graph_ts, CALL_GRAPH_TS_FILE_PATH)
        save_call_graph_image(call_graph_ts, CALL_GRAPH_TS_IMAGE_PATH)
        click.secho(f"OK - TypeScript project structure and call graph saved to {TIBO_TYPESCRIPT_DIR}.")
   
    if not project_structure_py and not project_structure_ts:
        click.secho(f"\n❌ No python or typescript files found, aborting indexing.", bold=True)
        sys.exit(1)
    
    echo_success("Call graph generation complete.")


def get_project_structure(root_dir, indent=0):
    result = ""
    items = sorted(os.listdir(root_dir))
    for index, item in enumerate(items):
        path = os.path.join(root_dir, item)
        prefix = "  " * indent + "- "
        
        if os.path.isdir(path):
            result += f"{prefix}{item}/\n"
            result += get_project_structure(path, indent + 1)
        else:
            result += f"{prefix}{item}\n"
    
    return result







    
    