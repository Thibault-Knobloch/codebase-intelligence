import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import json
import os
import requests
import click
from ..utils import save_json, load_json_file, echo_success
from ..utils import FILE_CHUNKS_WITH_VECTORS_FILE_PATH, FAISS_INDEX_PATH, PROJECT_DETAILS_FILE_PATH, QUERY_OUTPUT_DIR, QUERY_OUTPUT_FILE_PATH, OPENAI_API_KEY, OPENAI_API_URL
from ..utils import CALL_GRAPH_PY_FILE_PATH, CALL_GRAPH_TS_FILE_PATH
from .refinement import enhance_code_with_call_graph

def fetch_query(query):
    click.secho("\nFetching results...", bold=True)
    print(f"query: {query}")

    model_name = 'sentence-transformers/all-MiniLM-L6-v2'

    # Check if files exist
    if not os.path.exists(FAISS_INDEX_PATH) or not os.path.exists(FILE_CHUNKS_WITH_VECTORS_FILE_PATH):
        print("Error: Required database files not found. Please run 'tibo index' in the root directory of your project first.")
        return

    index = load_faiss_index(FAISS_INDEX_PATH)
    click.echo("OK - Chunks leaded from vector db.")
    
    file_chunks_with_vectors = load_json_file(FILE_CHUNKS_WITH_VECTORS_FILE_PATH)
    project_data = load_json_file(PROJECT_DETAILS_FILE_PATH)
    project_description = project_data["project_description"]
    project_structure = project_data["project_structure"]
    
    model = SentenceTransformer(model_name)
    click.echo(f"OK - Sentence transformer model ({model_name}) loaded.")

    enhanced_query = enhance_query(query, project_description, project_structure)
    click.echo(f"OK - Enhanced query with project context.")
    click.echo(f"Enhanced query: {enhanced_query}")

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

    save_json(output_data, QUERY_OUTPUT_FILE_PATH)
    click.echo(f"OK - Matches: {len(output_data)} files, {sum(len(v) for v in output_data.values())} chunks total")
    echo_success(f"Relevant chunks fetched.")

    click.secho("\nRefining results with code graph...", bold=True)
    py_call_graph_data = {}
    ts_call_graph_data = {}
    
    if os.path.exists(CALL_GRAPH_PY_FILE_PATH):
        py_call_graph_data = load_json_file(CALL_GRAPH_PY_FILE_PATH)
    
    if os.path.exists(CALL_GRAPH_TS_FILE_PATH):
        ts_call_graph_data = load_json_file(CALL_GRAPH_TS_FILE_PATH)
    
    enhance_code_with_call_graph(py_call_graph_data, ts_call_graph_data, output_data, file_chunks_with_vectors)
    echo_success("Enhanced chunks saved.")

    click.secho("\nRelevant context files for the query:", bold=True)
    for file, chunks in output_data.items():
        click.echo(f" - {file}: {len(chunks)} chunks")


def load_faiss_index(filename):
    return faiss.read_index(filename)

def get_embedding(query, model):
    embedding = model.encode([query])[0]
    # Normalize the query embedding to match our normalized database
    embedding = embedding / np.linalg.norm(embedding)
    return embedding.reshape(1, -1).astype(np.float32)

def search_faiss_index(index, query_embedding, k=15):
    distances, indices = index.search(query_embedding, k)
    return distances[0][::-1], indices[0][::-1]

def get_chunk_info(json_data, vector_id):
    for filepath, chunks in json_data.items():
        for chunk in chunks:
            if chunk.get('vector_db_id') == vector_id:
                return filepath, chunk['en-chunk'], chunk['code-chunk'], chunk['chunk-path']
    return None, "", "", ""

def enhance_query(
    query: str,
    project_description: str,
    project_structure: str
) -> str:
    """
    Generate minimal summary of code chunk for NLP matching.
    """
    try:        
        prompt = (
            "Use the context below to improve the query to make sure it encorporates relevant information."
            f"Project description: {project_description}\n\n"
            f"Project structure: {project_structure}\n\n"
            f"Query: {query}\n\n"
            "Output only the improved query—nothing else."
        )
        
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 100
        }
        
        response = requests.post(OPENAI_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        
        enhanced_query = response.json()["choices"][0]["message"]["content"]
        return enhanced_query
        
    except Exception as e:
        print(f"Error generating enhanced query: {e}")
        return f"Error: {str(e)}"
    