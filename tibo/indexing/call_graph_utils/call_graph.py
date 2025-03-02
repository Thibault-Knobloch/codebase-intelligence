import click
import sys
import os
import re
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
    """
    Generate a concise project structure, ignoring non-user-generated directories and files.
    """
    # Directories to ignore (build artifacts, caches, configs, etc.)
    ignore_dirs = {
        '.git', '.DS_Store', '__pycache__', '.idea', '.vscode', 'node_modules',
        'dist', 'build', '.pytest_cache', '.coverage', 'venv', 'env', '.env',
        '.next', 'migrations', 'static', 'cache', 'vendor-chunks', 'types',
        'logs', 'media', 'server', 'pages', 'objects', 'refs', 'hooks'
    }
    
    # Patterns for files that are typically generated (regex)
    ignore_file_patterns = [
        r'.*manifest.*\.json$',  # e.g., build-manifest.json, app-paths-manifest.json
        r'.*_manifest\.js$',     # e.g., page_client-reference-manifest.js
        r'.*\.hot-update.*$',    # e.g., webpack.2eca37c2e243fb2a.hot-update.js
        r'.*[0-9a-f]{8,}.*',     # Files with long hex hashes (e.g., 2ee76f9cb227_...)
        r'.*_compiled.*$',       # Compiled outputs
        r'.*env.*$',             # Environment files (e.g., .env.local)
        r'.*cache.*$',           # Cache-related files
        r'^_.*\.js$',            # e.g., _app.js, _error.js (Next.js defaults)
    ]
    
    # Allowed source file extensions (user-authored code)
    source_extensions = ('.py', '.ts', '.tsx', '.js', '.jsx', '.json', '.md')

    result = ""
    try:
        items = sorted(os.listdir(root_dir))
    except OSError:
        return result  # Skip inaccessible directories
    
    for item in items:
        # Skip ignored directories
        if item in ignore_dirs:
            continue
        
        path = os.path.join(root_dir, item)
        prefix = "  " * indent + "- "
        
        if os.path.isdir(path):
            result += f"{prefix}{item}/\n"
            result += get_project_structure(path, indent + 1)
        else:
            # Skip files that don’t match source extensions or match ignore patterns
            if not item.endswith(source_extensions):
                continue
            if any(re.match(pattern, item) for pattern in ignore_file_patterns):
                continue
            result += f"{prefix}{item}\n"
    
    return result
