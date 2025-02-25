import os
import json
from collections import defaultdict
from graphviz import Digraph
from .ParserClassTS import CodeStructureExtractor, CallGraphExtractor
import click
from ....utils import save_json

IGNORE_DIRS = ["node_modules", ".next"]

def get_module_name(file_path, project_path):
    rel_path = os.path.relpath(file_path, project_path)
    if rel_path.endswith((".ts", ".tsx")):
        rel_path = rel_path.rsplit(".", 1)[0]
    return rel_path.replace(os.sep, ".").replace(".__init__", "")

def extract_ts_project_structure_and_call_graph(project_path):
    project_structure = {}
    module_to_file = {}
    module_to_functions = defaultdict(list)
    typescript_files_found = False

    for root, _, files in os.walk(project_path):
        # Skip directories we don't want to analyze
        if any(ignored in root for ignored in IGNORE_DIRS):
            continue

        for file in files:
            if file.endswith((".ts", ".tsx")) and not file.endswith(".d.ts"):
                typescript_files_found = True
                file_path = os.path.join(root, file)
                module_name = get_module_name(file_path, project_path)
                extractor = CodeStructureExtractor(file_path, module_name)
                structure = extractor.extract()
                project_structure[file_path] = structure
                module_to_file[module_name] = file_path
                module_to_functions[module_name].extend(
                    structure["functions"] + structure["arrow_functions"] + structure["components"]
                )
                click.secho(f" [✓] analyzed file: {file} - {file_path}")

    if not typescript_files_found:
        # return empty to signal no python files in root dir, skipping call graph generation
        return {}, {}
    
    call_graph = defaultdict(lambda: {
        "all_function_calls": [],
        "user_function_calls": [],
        "called_from": []
    })
    for file_path in project_structure:
        module_name = get_module_name(file_path, project_path)
        extractor = CallGraphExtractor(
            file_path, module_name, project_structure,
            module_to_file, module_to_functions, call_graph
        )
        extractor.extract()

    return project_structure, dict(call_graph)

