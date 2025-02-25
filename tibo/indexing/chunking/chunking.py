import click
import ast
import os
import json
from tree_sitter import Language, Parser
from .llm_pass import process_json_file
from ...utils import save_json, load_json_file, echo_success, FILE_CHUNKS_FILE_PATH, PROJECT_DETAILS_FILE_PATH

# Path to the compiled TypeScript language library (adjust if needed)
TS_LANGUAGE_PATH = os.path.join(os.path.dirname(__file__), '..', 'call_graph_utils', 'typescript', 'build', 'typescript.so')
try:
    TS_LANGUAGE = Language(TS_LANGUAGE_PATH, "typescript")
    TS_PARSER = Parser()
    TS_PARSER.set_language(TS_LANGUAGE)
except Exception as e:
    print(f"Failed to load TypeScript language: {e}")
    print("Ensure the .so file is built and the path is correct.")
    raise

def chunk_project(path):
    click.secho("\nChunking project...", bold=True)
    
    chunks_data = process_path(path)
    if not chunks_data:
        print("No Python or TypeScript files found.")
        exit(1)
    
    save_json(chunks_data, FILE_CHUNKS_FILE_PATH)
    click.secho("OK - Successfully generated file chunks.")
    
    # get project description and structure
    project_data = load_json_file(PROJECT_DETAILS_FILE_PATH)
    project_description = project_data["project_description"]
    project_structure = project_data["project_structure"]

    process_json_file(project_description, project_structure)
    click.secho("OK - Successfully enhanced chunk context.")  

    echo_success("Codebase files chunked and enhanced.")  


def chunk_python_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    chunks = []
    try:
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                start = node.lineno - 1
                end = node.end_lineno
                chunk = ''.join(content.splitlines(True)[start:end]).strip()
                chunk_path = f"{file_path}:{node.name}"
                chunks.append({"code-chunk": chunk, "en-chunk": "", "chunk-path": chunk_path})
    except SyntaxError:
        if '\n\n' in content:
            chunks = [{"code-chunk": c.strip(), "en-chunk": "", "chunk-path": ""} for c in content.split('\n\n') if c.strip()]
        else:
            chunks = [{"code-chunk": content.strip(), "en-chunk": "", "chunk-path": ""}]
    return chunks

def chunk_typescript_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    chunks = []
    tree = TS_PARSER.parse(content.encode('utf-8'))
    root_node = tree.root_node

    def extract_chunks(node):
        if node.type in ["function_declaration", "class_declaration"]:
            start, end = node.start_byte, node.end_byte
            chunk = content[start:end].strip()
            name_node = node.child_by_field_name("name")
            chunk_path = f"{file_path}:{name_node.text.decode('utf-8')}" if name_node else ""
            chunks.append({"code-chunk": chunk, "en-chunk": "", "chunk-path": chunk_path})
        elif node.type == "variable_declarator":
            value_node = node.child_by_field_name("value")
            if value_node and value_node.type == "arrow_function":
                start, end = node.start_byte, node.end_byte
                chunk = content[start:end].strip()
                name_node = node.child_by_field_name("name")
                chunk_path = f"{file_path}:{name_node.text.decode('utf-8')}" if name_node else ""
                chunks.append({"code-chunk": chunk, "en-chunk": "", "chunk-path": chunk_path})
        for child in node.children:
            extract_chunks(child)

    extract_chunks(root_node)

    # Fallback if nothing found
    if not chunks:
        if '\n\n' in content:
            chunks = [{"code-chunk": c.strip(), "en-chunk": "", "chunk-path": ""} for c in content.split('\n\n') if c.strip()]
        else:
            chunks = [{"code-chunk": content.strip(), "en-chunk": "", "chunk-path": ""}]

    return chunks

def process_path(path):
    result = {}
    if os.path.isdir(path):
        for root, _, files in os.walk(path):
            for file in files:
                if file.endswith('.py') or (file.endswith(('.ts', '.tsx')) and not file.endswith('.d.ts')):
                    file_path = os.path.abspath(os.path.join(root, file))
                    if file.endswith('.py'):
                        result[file_path] = chunk_python_file(file_path)
                    else:
                        result[file_path] = chunk_typescript_file(file_path)
    elif os.path.isfile(path):
        file_path = os.path.abspath(path)
        if file_path.endswith('.py'):
            result[file_path] = chunk_python_file(file_path)
        elif file_path.endswith(('.ts', '.tsx')) and not file_path.endswith('.d.ts'):
            result[file_path] = chunk_typescript_file(file_path)
    return result
    