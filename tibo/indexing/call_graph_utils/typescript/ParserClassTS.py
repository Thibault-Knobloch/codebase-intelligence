import os
from tree_sitter import Language, Parser
import warnings

warnings.simplefilter("ignore", FutureWarning)

# Path to the compiled TypeScript language library
TS_LANGUAGE_PATH = os.path.join(os.path.dirname(__file__), 'build', 'typescript.so')

try:
    TS_LANGUAGE = Language(TS_LANGUAGE_PATH, "typescript")
    parser = Parser()
    parser.set_language(TS_LANGUAGE)
except Exception as e:
    print(f"Failed to load TypeScript language: {e}")
    print("Ensure the .so file is built and the path is correct. See setup instructions.")
    raise

class CodeStructureExtractor:
    def __init__(self, file_path, module_name):
        self.file_path = file_path
        self.module_name = module_name
        self.structure = {
            "functions": [],
            "arrow_functions": [],
            "components": []
        }

    def extract(self):
        with open(self.file_path, "r", encoding="utf-8") as f:
            code = f.read()
            tree = parser.parse(code.encode("utf-8"))
            self._traverse(tree.root_node)
        return self.structure

    def _traverse(self, node):
        # Function declarations
        if node.type == "function_declaration":
            name_node = node.child_by_field_name("name")
            if name_node:
                self.structure["functions"].append(name_node.text.decode("utf-8"))

        # Arrow functions
        elif node.type == "variable_declarator":
            name_node = node.child_by_field_name("name")
            value_node = node.child_by_field_name("value")
            if name_node and value_node and value_node.type == "arrow_function":
                self.structure["arrow_functions"].append(name_node.text.decode("utf-8"))

        # React components (simple heuristic)
        elif node.type in ["function_declaration", "variable_declarator"]:
            name_node = node.child_by_field_name("name")
            if name_node:
                name = name_node.text.decode("utf-8")
                if name and name[0].isupper():
                    self.structure["components"].append(name)

        for child in node.children:
            self._traverse(child)

class CallGraphExtractor:
    def __init__(self, file_path, module_name, project_structure, module_to_file, module_to_functions, call_graph):
        self.file_path = file_path
        self.module_name = module_name
        self.current_scope = []
        self.call_graph = call_graph
        self.imported_names = {}
        self.project_structure = project_structure
        self.module_to_file = module_to_file
        self.module_to_functions = module_to_functions
        self.local_functions = set(
            self.project_structure.get(file_path, {}).get("functions", []) +
            self.project_structure.get(file_path, {}).get("arrow_functions", []) +
            self.project_structure.get(file_path, {}).get("components", [])
        )

    def extract(self):
        with open(self.file_path, "r", encoding="utf-8") as f:
            code = f.read()
            tree = parser.parse(code.encode("utf-8"))
            self._traverse(tree.root_node)
        return dict(self.call_graph)

    def _traverse(self, node):
        if node.type == "import_statement":
            import_clause = node.child_by_field_name("source")
            if import_clause:
                module = import_clause.text.decode("utf-8").strip("'\"")
                for child in node.children:
                    if child.type in ["named_imports", "import_specifier"]:
                        name_node = child.child_by_field_name("name")
                        alias_node = child.child_by_field_name("alias")
                        name = alias_node.text.decode("utf-8") if alias_node else name_node.text.decode("utf-8")
                        self.imported_names[name] = (module, name_node.text.decode("utf-8"))

        elif node.type in ["function_declaration", "arrow_function"]:
            name_node = node.child_by_field_name("name") if node.type == "function_declaration" else None
            if not name_node and node.parent and node.parent.type == "variable_declarator":
                name_node = node.parent.child_by_field_name("name")
            if name_node:
                self.current_scope.append(f"{self.file_path}:{name_node.text.decode('utf-8')}")
                for child in node.children:
                    self._traverse(child)
                self.current_scope.pop()

        elif node.type == "call_expression":
            if self.current_scope:
                caller = self.current_scope[-1]
                func_node = node.child_by_field_name("function")
                if func_node:
                    call_name = func_node.text.decode("utf-8")
                    full_call_name = self._resolve_call(call_name)
                    if full_call_name:
                        self.call_graph[caller]["all_function_calls"].append(call_name)
                        if self._is_project_function(full_call_name):
                            self.call_graph[caller]["user_function_calls"].append(full_call_name)
                            self.call_graph[full_call_name]["called_from"].append(caller)

        for child in node.children:
            self._traverse(child)

    def _resolve_call(self, call_name):
        if "." in call_name:
            module_alias, func = call_name.split(".", 1)
            if module_alias in self.imported_names:
                module, _ = self.imported_names[module_alias]
                return self._resolve_module_function(module, func)
            return call_name
        if call_name in self.local_functions:
            return f"{self.file_path}:{call_name}"
        if call_name in self.imported_names:
            module, orig_name = self.imported_names[call_name]
            return self._resolve_module_function(module, orig_name)
        return call_name

    def _resolve_module_function(self, module, func_name):
        if module in self.module_to_file:
            file_path = self.module_to_file[module]
            if func_name in self.module_to_functions.get(module, []):
                return f"{file_path}:{func_name}"
        return f"{module}.{func_name}"

    def _is_project_function(self, full_name):
        return ":" in full_name and full_name.split(":")[0] in self.project_structure