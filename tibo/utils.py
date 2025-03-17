import os
import json
import click
from dotenv import load_dotenv

CONFIG_PATH = os.path.expanduser("~/.tibo.env")
TIBO_DIR = ".tibo"
PROJECT_DETAILS_FILE_PATH = os.path.join(TIBO_DIR, "project_details.json")

TIBO_PYTHON_DIR = os.path.join(TIBO_DIR, "python")
CALL_GRAPH_PY_FILE_PATH = os.path.join(TIBO_PYTHON_DIR, "call_graph_py.json")
PROJECT_STRUCTURE_PY_FILE_PATH = os.path.join(TIBO_PYTHON_DIR, "project_structure_py.json")
CALL_GRAPH_PY_IMAGE_PATH = os.path.join(TIBO_PYTHON_DIR, "call_graph_py.png")

TIBO_TYPESCRIPT_DIR = os.path.join(TIBO_DIR, "typescript")
CALL_GRAPH_TS_FILE_PATH = os.path.join(TIBO_TYPESCRIPT_DIR, "call_graph_ts.json")
PROJECT_STRUCTURE_TS_FILE_PATH = os.path.join(TIBO_TYPESCRIPT_DIR, "project_structure_ts.json")
CALL_GRAPH_TS_IMAGE_PATH = os.path.join(TIBO_TYPESCRIPT_DIR, "call_graph_ts.png")

TIBO_CHUNKS_DIR = os.path.join(TIBO_DIR, "chunks")
FILE_CHUNKS_FILE_PATH = os.path.join(TIBO_CHUNKS_DIR, "file_chunks.json")

load_dotenv(CONFIG_PATH)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"

TIBO_VECTOR_DIR = os.path.join(TIBO_DIR, "vector")
FILE_CHUNKS_WITH_VECTORS_FILE_PATH = os.path.join(TIBO_VECTOR_DIR, "file_chunks_with_vectors.json")
FAISS_INDEX_PATH = os.path.join(TIBO_VECTOR_DIR, "chunks_vector_db.faiss")

QUERY_OUTPUT_DIR = os.path.join(TIBO_DIR, "query_output")
QUERY_OUTPUT_FILE_PATH = os.path.join(QUERY_OUTPUT_DIR, "query_output.json")


def save_json(data, output_file):
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def load_json_file(filename):
    with open(filename, 'r') as f:
        return json.load(f)

def echo_success(message):
    border = "=" * 50
    success_text = click.style(" SUCCESS", bold=True)
    click.secho(f"{border}\n{success_text} - {message}\n{border}")