import os
from tree_sitter import Language, Parser

# Path to the compiled TypeScript language library (adjust as needed)
TS_LANGUAGE_PATH = os.path.join(os.path.dirname(__file__), '../../call_graph_utils/typescript/build', 'typescript.so')
try:
    TS_LANGUAGE = Language(TS_LANGUAGE_PATH, "typescript")
    parser = Parser()
    parser.set_language(TS_LANGUAGE)
except Exception as e:
    raise Exception(f"Failed to load TypeScript language: {e}. Ensure the .so file is built and the path is correct.")

class ChunkingTypescript:
    def __init__(self, file_path, content):
        self.file_path = file_path
        self.content = content.splitlines(True)  # Preserve newlines for slicing
        self.chunks = []
        self.last_end_line = 0  # Track the end of the last processed block

    def _process_function(self, node):
        """Process function declarations (including async)."""
        self._add_preceding_code(node.start_point[0])
        start = node.start_point[0]
        end = node.end_point[0] + 1  # Include the last line
        chunk = ''.join(self.content[start:end]).strip()
        name_node = node.child_by_field_name('name')
        name = name_node.text.decode('utf-8') if name_node else 'anonymous'
        chunk_path = f"{self.file_path}:{name}"
        # Check for async modifier
        is_async = any(child.type == 'async' for child in node.children)
        chunk_type = 'async_function' if is_async else 'function'
        self.chunks.append({"code-chunk": chunk, "en-chunk": "", "chunk-path": chunk_path, "type": chunk_type})
        self.last_end_line = end

    def _process_class(self, node):
        """Process class declarations."""
        self._add_preceding_code(node.start_point[0])
        start = node.start_point[0]
        end = node.end_point[0] + 1
        chunk = ''.join(self.content[start:end]).strip()
        name_node = node.child_by_field_name('name')
        name = name_node.text.decode('utf-8') if name_node else 'anonymous'
        chunk_path = f"{self.file_path}:{name}"
        self.chunks.append({"code-chunk": chunk, "en-chunk": "", "chunk-path": chunk_path, "type": "class"})
        self.last_end_line = end

    def _add_preceding_code(self, current_start):
        """Capture code between the last block and the current one."""
        if self.last_end_line < current_start:
            chunk = ''.join(self.content[self.last_end_line:current_start]).strip()
            if chunk:
                chunk_path = f"{self.file_path}:top_level_{self.last_end_line + 1}-{current_start}"
                self.chunks.append({"code-chunk": chunk, "en-chunk": "", "chunk-path": chunk_path, "type": "top_level"})

    def visit(self, tree):
        """Traverse the tree_sitter AST and chunk based on structure."""
        def traverse(node):
            if node.type == 'function_declaration':
                self._process_function(node)
            elif node.type == 'class_declaration':
                self._process_class(node)
            for child in node.children:
                traverse(child)

        traverse(tree.root_node)

    def get_chunks(self):
        """Finalize and return all chunks, including any remaining code."""
        if self.last_end_line < len(self.content):
            chunk = ''.join(self.content[self.last_end_line:]).strip()
            if chunk:
                chunk_path = f"{self.file_path}:top_level_{self.last_end_line + 1}-end"
                self.chunks.append({"code-chunk": chunk, "en-chunk": "", "chunk-path": chunk_path, "type": "top_level"})
        return self.chunks