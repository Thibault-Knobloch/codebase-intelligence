import ast
from .ChunkingPython import ChunkingPython

def chunk_python_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    chunks = []
    try:
        tree = ast.parse(content)
        chunker = ChunkingPython(file_path, content)
        chunker.visit(tree)
        chunks = chunker.get_chunks()
    except SyntaxError:
        if '\n\n' in content:
            chunks = [
                {"code-chunk": c.strip(), "en-chunk": "", "chunk-path": f"{file_path}:block_{i}", "type": "raw"}
                for i, c in enumerate(content.split('\n\n')) if c.strip()
            ]
        else:
            chunks = [{"code-chunk": content.strip(), "en-chunk": "", "chunk-path": file_path, "type": "raw"}]
    
    return chunks