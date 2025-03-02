import ast
import os
from collections import defaultdict
from graphviz import Digraph
from .ParserClassPY import CodeStructureExtractor, CallGraphExtractor
import click


def get_module_name(file_path, project_path):
    rel_path = os.path.relpath(file_path, project_path)
    if rel_path.endswith(".py"):
        rel_path = rel_path[:-3]
    return rel_path.replace(os.sep, ".").replace(".__init__", "")


def extract_structure_from_file(file_path, module_name):
    with open(file_path, "r", encoding="utf-8") as f:
        try:
            tree = ast.parse(f.read(), filename=file_path)
            extractor = CodeStructureExtractor(file_path, module_name)
            extractor.visit(tree)
            return extractor.get_structure()
        except Exception as e:
            print(f"Skipping {file_path}: {e}")
            return {}


def extract_python_project_structure_and_call_graph(project_path):
    IGNORE_DIRS = ["node_modules", ".next"]

    project_structure = {}
    module_to_file = {}
    module_to_functions = defaultdict(list)
    python_files_found = False

    for root, _, files in os.walk(project_path):
        if any(ignored in root for ignored in IGNORE_DIRS):
            continue

        for file in files:
            if file.endswith(".py"):
                python_files_found = True
                file_path = os.path.join(root, file)
                module_name = get_module_name(file_path, project_path)
                structure = extract_structure_from_file(file_path, module_name)
                project_structure[file_path] = structure
                module_to_file[module_name] = file_path
                module_to_functions[module_name].extend(
                    structure["functions"] + structure["async_functions"]
                )
                click.secho(f" [✓] analyzed file: {file} - {file_path}")

    if not python_files_found:
        # return empty to signal no python files in root dir, skipping call graph generation
        return {}, {}
    
    call_graph = defaultdict(lambda: {
        "all_function_calls": [],
        "user_function_calls": [],
        "called_from": []
    })
    for file_path in project_structure:
        module_name = get_module_name(file_path, project_path)
        extractor = CallGraphExtractor(file_path, module_name, project_structure, module_to_file, module_to_functions, call_graph)
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                tree = ast.parse(f.read(), filename=file_path)
                extractor.visit(tree)
            except Exception as e:
                print(f"Skipping {file_path}: {e}")

    return project_structure, dict(call_graph)



def save_call_graph_image(call_graph, filename):
    """Save the call graph as an image file in the specified directory."""
    dot = Digraph(comment="Call Graph", format="png", graph_attr={'rankdir': 'TB'})
    func_to_short = {func: func.split(":")[-1] for func in call_graph}
    func_to_label = {func: os.path.basename(func.split(":")[0]) + "." + func.split(":")[-1] for func in call_graph}
    func_to_nodeid = {func: func.split(":")[-1].replace(".", "_") for func in call_graph}
    
    for func in call_graph:
        dot.node(func_to_nodeid[func], func_to_label[func], shape="ellipse")
    
    for func, details in call_graph.items():
        short_func = func_to_nodeid[func]
        for call in details["all_function_calls"]:
            full_call = next((f for f in call_graph if f.endswith(f":{call}")), None)
            if full_call:
                short_call = func_to_nodeid[full_call]
                dot.edge(short_func, short_call, label="calls", color="blue", arrowhead="normal")
        for caller in details["called_from"]:
            short_caller = func_to_nodeid[caller]
            dot.edge(short_caller, short_func, label="called", color="red", arrowhead="normal")
    
    try:
        dot.render(filename, view=False)
    except Exception as e:
        click.echo(
            "WARN - Failed to generate (optional) call graph image due to missing Graphviz executables. "
            "The call graph JSON is still saved. To generate the image, install Graphviz:\n"
            "macOS -> brew install graphviz"
        )