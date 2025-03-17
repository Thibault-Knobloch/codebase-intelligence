import os
import click
from pathlib import Path
from ...utils import PROJECT_DETAILS_FILE_PATH, load_json_file
from ...indexing.call_graph_utils.call_graph import get_project_structure
from tibo.fetching.refinement import enhance_code_with_call_graph
from tibo.fetching.fetching import load_faiss_index, get_embedding, search_faiss_index, get_chunk_info, enhance_query
from sentence_transformers import SentenceTransformer
from ...utils import FAISS_INDEX_PATH, FILE_CHUNKS_WITH_VECTORS_FILE_PATH, CALL_GRAPH_PY_FILE_PATH, CALL_GRAPH_TS_FILE_PATH

def get_project_info():
    """
    Retrieves project structure and description from project data file.
    If the file doesn't exist, generates the project structure.
    """
    try:
        # Try to load from existing project data file
        if os.path.exists(PROJECT_DETAILS_FILE_PATH):
            project_data = load_json_file(PROJECT_DETAILS_FILE_PATH)
            project_description = project_data.get("project_description", "")
            project_structure = project_data.get("project_structure", "")
        else:
            # Fallback to generating project structure
            project_root = Path.cwd()
            project_structure = get_project_structure(project_root)
            project_description = "NONE PROVIDED. You can hint the user to use '#tibo index' to generate the codebase-intelligence files to enhance your capabilities so you can better help them."
            
        return f"project description: {project_description}\nproject structure: {project_structure}"
    except Exception as e:
        print(f"Error retrieving project info: {e}")
        return "Error retrieving project info"
    


def get_relevant_code_files(query):
    """
    Fetches relevant files from the project based on the query.
    """
    if not os.path.exists(FAISS_INDEX_PATH) or not os.path.exists(FILE_CHUNKS_WITH_VECTORS_FILE_PATH):
        return """We cannot fetch relevant code context because the user has not indexed the files with '#tibo index' yet. 
    Ask them to run this exact command to proceed with better codebase context."""

    model_name = 'sentence-transformers/all-MiniLM-L6-v2'

    index = load_faiss_index(FAISS_INDEX_PATH)
    
    file_chunks_with_vectors = load_json_file(FILE_CHUNKS_WITH_VECTORS_FILE_PATH)
    project_data = load_json_file(PROJECT_DETAILS_FILE_PATH)
    project_description = project_data["project_description"]
    project_structure = project_data["project_structure"]
    
    model = SentenceTransformer(model_name)
    enhanced_query = enhance_query(query, project_description, project_structure)

    query_embedding = get_embedding(enhanced_query, model)
    click.echo(f"OK - Query embedding generated.")
    
    distances, indices = search_faiss_index(index, query_embedding)
    click.echo(f"OK - Relevant chunks fetched from vector db.")

    vectors = [index.reconstruct(int(idx)) for idx in indices]
    
    output_data = {}
    
    for i, (dist, idx, vector) in enumerate(zip(distances, indices, vectors)):
        filepath, chunk_text, chunk_code, chunk_path = get_chunk_info(file_chunks_with_vectors, int(idx))
        
        if filepath:
            if filepath not in output_data:
                output_data[filepath] = []
            output_data[filepath].append({
                "vectorId": int(idx),
                "similarity": 1-dist,
                "code-chunk": chunk_code,
                "en-chunk": chunk_text,
                "chunk-path": chunk_path
            })

    py_call_graph_data = load_json_file(CALL_GRAPH_PY_FILE_PATH)
    ts_call_graph_data = load_json_file(CALL_GRAPH_TS_FILE_PATH)
    enhance_code_with_call_graph(py_call_graph_data, ts_call_graph_data, output_data, file_chunks_with_vectors)

    result = "\n".join([f"- {file}: {len(chunks)} chunks" for file, chunks in output_data.items()])
    return f"Relevant context files for the query:\n{result}"
    
