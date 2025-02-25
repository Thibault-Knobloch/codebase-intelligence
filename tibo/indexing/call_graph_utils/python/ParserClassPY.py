import ast


class CodeStructureExtractor(ast.NodeVisitor):
    def __init__(self, file_path, module_name):
        self.file_path = file_path
        self.module_name = module_name
        self.structure = {
            "functions": [],
            "async_functions": [],
            "classes": []
        }
    
    def visit_FunctionDef(self, node):
        self.structure["functions"].append(node.name)
        self.generic_visit(node)
    
    def visit_AsyncFunctionDef(self, node):
        self.structure["async_functions"].append(node.name)
        self.generic_visit(node)
    
    def visit_ClassDef(self, node):
        self.structure["classes"].append(node.name)
        self.generic_visit(node)
    
    def get_structure(self):
        return self.structure


class CallGraphExtractor(ast.NodeVisitor):
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
            self.project_structure.get(file_path, {}).get("async_functions", [])
        )

    def visit_Import(self, node):
        for alias in node.names:
            self.imported_names[alias.asname or alias.name] = (alias.name, alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        module = node.module or ""
        for alias in node.names:
            self.imported_names[alias.asname or alias.name] = (module, alias.name)
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        full_name = f"{self.file_path}:{node.name}"
        self.call_graph[full_name]  # Ensure entry exists
        self.current_scope.append(full_name)
        self.generic_visit(node)
        self.current_scope.pop()

    def visit_AsyncFunctionDef(self, node):
        full_name = f"{self.file_path}:{node.name}"
        self.call_graph[full_name]  # Ensure entry exists
        self.current_scope.append(full_name)
        self.generic_visit(node)
        self.current_scope.pop()

    def visit_Call(self, node):
        if not self.current_scope:
            return
        caller = self.current_scope[-1]

        call_name = None
        full_call_name = None

        if isinstance(node.func, ast.Name):
            call_name = node.func.id
            full_call_name = self._resolve_simple_call(call_name)
        elif isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
            module_alias = node.func.value.id
            call_name = node.func.attr
            full_call_name = self._resolve_attribute_call(module_alias, call_name)

        if call_name and full_call_name:
            self.call_graph[caller]["all_function_calls"].append(call_name)
            is_project_func = self._is_project_function(full_call_name)
            if is_project_func:
                self.call_graph[caller]["user_function_calls"].append(full_call_name)
                self.call_graph[full_call_name]["called_from"].append(caller)
            elif call_name in self._get_all_project_functions():
                # Fallback: if it's a project function but wasn't resolved with a path, find its full name
                full_call_name = self._find_full_function_name(call_name)
                if full_call_name and self._is_project_function(full_call_name):
                    self.call_graph[caller]["user_function_calls"].append(full_call_name)
                    self.call_graph[full_call_name]["called_from"].append(caller)

        self.generic_visit(node)

    def _is_local_function(self, func_name):
        return func_name in self.local_functions

    def _resolve_simple_call(self, call_name):
        if self._is_local_function(call_name):
            return f"{self.file_path}:{call_name}"
        if call_name in self.imported_names:
            module, orig_name = self.imported_names[call_name]
            return self._resolve_module_function(module, orig_name)
        return call_name

    def _resolve_attribute_call(self, module_alias, call_name):
        if module_alias in self.imported_names:
            module, _ = self.imported_names[module_alias]
            return self._resolve_module_function(module, call_name)
        elif module_alias in self.module_to_file:
            return self._resolve_module_function(module_alias, call_name)
        return f"{module_alias}.{call_name}"

    def _resolve_module_function(self, module, func_name):
        if module in self.module_to_file:
            file_path = self.module_to_file[module]
            if func_name in self.module_to_functions.get(module, []):
                return f"{file_path}:{func_name}"
        return f"{module}.{func_name}"

    def _is_project_function(self, full_name):
        return ":" in full_name and full_name.split(":")[0] in self.project_structure

    def _get_all_project_functions(self):
        # Collect all function names defined in the project
        all_funcs = set()
        for file_path, structure in self.project_structure.items():
            all_funcs.update(structure.get("functions", []) + structure.get("async_functions", []))
        return all_funcs

    def _find_full_function_name(self, func_name):
        # Search project structure for the full path of a function
        for file_path, structure in self.project_structure.items():
            if func_name in structure.get("functions", []) or func_name in structure.get("async_functions", []):
                return f"{file_path}:{func_name}"
        return None

    def get_graph(self):
        return dict(self.call_graph)
        