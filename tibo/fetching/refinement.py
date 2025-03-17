import json
import os
import click
from ..utils import save_json, QUERY_OUTPUT_FILE_PATH, QUERY_OUTPUT_DIR

def load_json_file(filename):
    with open(filename, 'r') as f:
        return json.load(f)

def get_function_name_from_code(code_chunk):
    # Extract the function name from the first line of the code chunk
    first_line = code_chunk.strip().split('\n')[0]
    if first_line.startswith('def '):
        return first_line.split('def ')[1].split('(')[0].strip()
    return None

def determine_call_graph(chunk_path, func_name, python_lookup, typescript_lookup):
    """Determine which call graph to use based on file extension."""
    if chunk_path.endswith('.py:' + func_name):
        return python_lookup
    elif chunk_path.endswith(('.ts:' + func_name, '.tsx:' + func_name)):
        return typescript_lookup
    return None

def extract_chunk_info(chunk, file_path=None):
    """Extract full key and function name from a chunk."""
    code = chunk['code-chunk']
    chunk_path = chunk.get('chunk-path', '')
    
    if chunk_path:
        full_key = chunk_path
        func_name = chunk_path.rsplit(':', 1)[-1]
    else:
        func_name = get_function_name_from_code(code)
        full_key = None if not func_name else f"{file_path}:{func_name}"
    
    return full_key, func_name

def add_related_chunks(call_info, chunk_lookup, relevant_context):
    """Add related chunks from call graph to relevant context."""
    if call_info['user_function_calls']:
        for called_func in call_info['user_function_calls']:
            if called_func in chunk_lookup:
                related_chunk = chunk_lookup[called_func]
                file_path_related = called_func.rsplit(':', 1)[0]
                if file_path_related not in relevant_context:
                    relevant_context[file_path_related] = []
                relevant_context[file_path_related].append({
                    "vectorId": related_chunk['vectorId'],
                    "similarity": -1,
                    "code-chunk": related_chunk['code-chunk'],
                    "en-chunk": related_chunk['en-chunk'],
                    "chunk-path": related_chunk['chunk-path']
                })
    
    # Add functions that call this function (called_from)
    if call_info['called_from']:
        for caller in call_info['called_from']:
            if caller in chunk_lookup:
                related_chunk = chunk_lookup[caller]
                file_path_related = caller.rsplit(':', 1)[0]
                if file_path_related not in relevant_context:
                    relevant_context[file_path_related] = []
                relevant_context[file_path_related].append({
                    "vectorId": related_chunk['vectorId'],
                    "similarity": -1,
                    "code-chunk": related_chunk['code-chunk'],
                    "en-chunk": related_chunk['en-chunk'],
                    "chunk-path": related_chunk['chunk-path']
                })

def deduplicate_chunks(relevant_context):
    """Remove duplicate chunks based on chunk-path and code-chunk."""
    deduplicated = {}
    for file_path, chunks in relevant_context.items():
        deduplicated[file_path] = []
        seen = set()
        for chunk in chunks:
            key = (chunk['chunk-path'], chunk['code-chunk'])
            if key not in seen:
                seen.add(key)
                deduplicated[file_path].append(chunk)
    return deduplicated

def enhance_code_with_call_graph(python_call_graph, typescript_call_graph, query_chunks, file_chunks_with_vectors):
    python_call_graph_lookup = {key: value for key, value in python_call_graph.items()}
    typescript_call_graph_lookup = {key: value for key, value in typescript_call_graph.items()}
    
    chunk_lookup = {}
    for file_path, chunks in file_chunks_with_vectors.items():
        for chunk in chunks:
            if chunk.get('chunk-path'):
                chunk_lookup[chunk['chunk-path']] = {
                    "code-chunk": chunk['code-chunk'],
                    "en-chunk": chunk['en-chunk'],
                    "chunk-path": chunk['chunk-path'],
                    "vectorId": chunk.get('vector_db_id', -1)
                }

    relevant_context = {}

    for file_path, chunks in query_chunks.items():
        relevant_context[file_path] = []
        
        for chunk in chunks:
            code = chunk['code-chunk']
            full_key, func_name = extract_chunk_info(chunk, file_path)
            
            if not full_key or not func_name:
                relevant_context[file_path].append({
                    "vectorId": chunk.get('vectorId', -1),
                    "similarity": chunk.get('similarity', -1),
                    "code-chunk": code,
                    "en-chunk": chunk['en-chunk'],
                    "chunk-path": chunk.get('chunk-path', '')
                })
                continue
                
            relevant_context[file_path].append({
                "vectorId": chunk.get('vectorId', -1),
                "similarity": chunk.get('similarity', -1),
                "code-chunk": code,
                "en-chunk": chunk['en-chunk'],
                "chunk-path": full_key
            })
            
            # Determine appropriate call graph
            call_graph_lookup = determine_call_graph(full_key, func_name, python_call_graph_lookup, typescript_call_graph_lookup)
            
            # Look up and process call graph info
            if call_graph_lookup and full_key in call_graph_lookup:
                call_info = call_graph_lookup[full_key]
                add_related_chunks(call_info, chunk_lookup, relevant_context)
            else:
                # no call graph information available
                pass
            
    total_files = len(relevant_context)
    total_chunks = sum(len(chunks) for chunks in relevant_context.values())
    click.echo(f"OK - Call graph context added, new total {total_files} files with {total_chunks} chunks.")

    relevant_context = deduplicate_chunks(relevant_context)
    total_files = len(relevant_context)
    total_chunks = sum(len(chunks) for chunks in relevant_context.values())
    click.echo(f"OK - Duplicates removed, new total {total_files} files with {total_chunks} chunks.")


    save_json(relevant_context, QUERY_OUTPUT_FILE_PATH)
    click.echo(f"OK - Enhanced context saved to {QUERY_OUTPUT_DIR}")
    