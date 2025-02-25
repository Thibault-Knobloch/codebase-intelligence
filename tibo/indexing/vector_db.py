import click
import json
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import os
from ..utils import load_json_file, save_json, echo_success, TIBO_VECTOR_DIR, FILE_CHUNKS_FILE_PATH, FILE_CHUNKS_WITH_VECTORS_FILE_PATH, FAISS_INDEX_PATH

def save_to_vector_db():
    click.secho("\nSaving to vector database...", bold=True)
    
    # Check if input file exists
    if not os.path.exists(FILE_CHUNKS_FILE_PATH):
        print(f"Error: Input file '{FILE_CHUNKS_FILE_PATH}' not found.")
        return
    
    chunks_data = load_json_file(FILE_CHUNKS_FILE_PATH)
    click.echo("OK - Successfully loaded chunks data.")
    
    index, embeddings, chunk_references = embed_chunks(chunks_data)
    click.echo("OK - Successfully embedded chunks.")
    
    update_json_with_vector_references(chunks_data, chunk_references)
    click.echo("OK - Successfully updated chunk data with vector references.")
    
    save_faiss_index(index, FAISS_INDEX_PATH)
    click.echo(f"OK - Successfully saved FAISS index to {TIBO_VECTOR_DIR}.")
    
    echo_success("Chunk embeddings saved successfully.")

def embed_chunks(chunks_data, model_name='sentence-transformers/all-MiniLM-L6-v2'):
    model = SentenceTransformer(model_name)
    
    all_en_chunks = []
    chunk_references = []  
    
    for filepath, chunks in chunks_data.items():
        for chunk_idx, chunk in enumerate(chunks):
            all_en_chunks.append(chunk['en-chunk'])
            chunk_references.append((filepath, chunk_idx))
    
    # normalize embeddings for similarity search
    embeddings = model.encode(all_en_chunks, show_progress_bar=True)
    embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
    
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings.astype(np.float32))
    
    return index, embeddings, chunk_references

def update_json_with_vector_references(chunks_data, chunk_references):
    for i, (filepath, chunk_idx) in enumerate(chunk_references):
        chunks_data[filepath][chunk_idx]['vector_db_id'] = i
    
    save_json(chunks_data, FILE_CHUNKS_WITH_VECTORS_FILE_PATH)

def save_faiss_index(index, filename):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    faiss.write_index(index, filename)
