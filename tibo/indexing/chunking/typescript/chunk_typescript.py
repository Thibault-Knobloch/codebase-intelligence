from .ChunkingTypescript import ChunkingTypescript, parser

def chunk_typescript_file(file_path):
    """Chunk a TypeScript file into structural units."""
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    chunks = []
    try:
        tree = parser.parse(content.encode('utf-8'))
        chunker = ChunkingTypescript(file_path, content)
        chunker.visit(tree)
        chunks = chunker.get_chunks()
    except Exception as e:
        print(f"Failed to parse TypeScript file {file_path}: {e}")
        if '\n\n' in content:
            chunks = [
                {"code-chunk": c.strip(), "en-chunk": "", "chunk-path": f"{file_path}:block_{i}", "type": "raw"}
                for i, c in enumerate(content.split('\n\n')) if c.strip()
            ]
        else:
            chunks = [{"code-chunk": content.strip(), "en-chunk": "", "chunk-path": file_path, "type": "raw"}]

    return chunks

if __name__ == "__main__":
    # Example usage
    file_path = "example.ts"
    chunks = chunk_typescript_file(file_path)
    for chunk in chunks:
        print(f"Type: {chunk['type']}, Path: {chunk['chunk-path']}")
        print(chunk['code-chunk'])
        print("-" * 50)