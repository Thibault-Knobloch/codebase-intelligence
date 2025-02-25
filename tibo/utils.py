import os
import json

TIBO_DIR = ".tibo"
PROJECT_DESCRIPTION_FILE_PATH = os.path.join(TIBO_DIR, "project_details.json")

TIBO_PYTHON_DIR = os.path.join(TIBO_DIR, "python")
CALL_GRAPH_PY_FILE_PATH = os.path.join(TIBO_PYTHON_DIR, "call_graph_py.json")
PROJECT_STRUCTURE_PY_FILE_PATH = os.path.join(TIBO_PYTHON_DIR, "project_structure_py.json")
CALL_GRAPH_PY_IMAGE_PATH = os.path.join(TIBO_PYTHON_DIR, "call_graph_py.png")

TIBO_TYPESCRIPT_DIR = os.path.join(TIBO_DIR, "typescript")
CALL_GRAPH_TS_FILE_PATH = os.path.join(TIBO_TYPESCRIPT_DIR, "call_graph_ts.json")
PROJECT_STRUCTURE_TS_FILE_PATH = os.path.join(TIBO_TYPESCRIPT_DIR, "project_structure_ts.json")
CALL_GRAPH_TS_IMAGE_PATH = os.path.join(TIBO_TYPESCRIPT_DIR, "call_graph_ts.png")

def save_json(data, output_file):
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)