import ast
import os

class ChunkingPython(ast.NodeVisitor):
    def __init__(self, file_path, content):
        self.file_path = file_path
        self.content = content.splitlines(True)  # Preserve newlines for slicing
        self.chunks = []
        self.last_end_line = 0  # Track the end of the last processed block
    
    def visit_FunctionDef(self, node):
        self._add_preceding_code(node.lineno - 1)
        start = node.lineno - 1
        end = node.end_lineno
        chunk = ''.join(self.content[start:end]).strip()
        chunk_path = f"{self.file_path}:{node.name}"
        self.chunks.append({"code-chunk": chunk, "en-chunk": "", "chunk-path": chunk_path, "type": "function"})
        self.last_end_line = end
        self.generic_visit(node)
    
    def visit_AsyncFunctionDef(self, node):
        self._add_preceding_code(node.lineno - 1)
        start = node.lineno - 1
        end = node.end_lineno
        chunk = ''.join(self.content[start:end]).strip()
        chunk_path = f"{self.file_path}:{node.name}"
        self.chunks.append({"code-chunk": chunk, "en-chunk": "", "chunk-path": chunk_path, "type": "async_function"})
        self.last_end_line = end
        self.generic_visit(node)
    
    def visit_ClassDef(self, node):
        self._add_preceding_code(node.lineno - 1)
        start = node.lineno - 1
        end = node.end_lineno
        chunk = ''.join(self.content[start:end]).strip()
        chunk_path = f"{self.file_path}:{node.name}"
        self.chunks.append({"code-chunk": chunk, "en-chunk": "", "chunk-path": chunk_path, "type": "class"})
        self.last_end_line = end
        self.generic_visit(node)
    
    def _add_preceding_code(self, current_start):
        """Capture code between the last block and the current one."""
        if self.last_end_line < current_start:
            chunk = ''.join(self.content[self.last_end_line:current_start]).strip()
            if chunk:
                chunk_path = f"{self.file_path}:top_level_{self.last_end_line + 1}-{current_start}"
                self.chunks.append({"code-chunk": chunk, "en-chunk": "", "chunk-path": chunk_path, "type": "top_level"})
    
    def get_chunks(self):
        """Finalize and return all chunks, including any remaining code."""
        if self.last_end_line < len(self.content):
            chunk = ''.join(self.content[self.last_end_line:]).strip()
            if chunk:
                chunk_path = f"{self.file_path}:top_level_{self.last_end_line + 1}-end"
                self.chunks.append({"code-chunk": chunk, "en-chunk": "", "chunk-path": chunk_path, "type": "top_level"})
        return self.chunks