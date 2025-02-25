import json
import requests
import os
import click
from typing import Dict, List, Optional
from ...utils import FILE_CHUNKS_FILE_PATH, OPENAI_API_KEY, OPENAI_API_URL, save_json


def generate_summary(
    code_chunk: str,
    file_path: str,
    project_description: str,
    project_structure: str
) -> str:
    """
    Generate minimal summary of code chunk for NLP matching.
    """
    try:        
        prompt = (
            "Summarize this code chunk concisely using the following format:\n\n"
            "<function/class name>: <brief purpose of function/class in project, using 20 words or less>\n"
            "Rules:\n"
            "- Do NOT describe syntax, just the purpose and effect.\n"
            "- Avoid redundancy, focus on the core functionality.\n"
            "- Use consistent phrasing.\n\n"
            f"Project context: {project_description}\n\n"
            f"Project structure: {project_structure}\n\n"
            f"Code chunk is from file: {file_path}\n\n"
            f"Code chunk:\n```{code_chunk}```\n\n"
            "Output only the structured summary—nothing else."
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
        
        summary = response.json()["choices"][0]["message"]["content"]
        return summary
        
    except Exception as e:
        print(f"Error generating summary: {e}")
        return f"Error: {str(e)}"

def process_json_file(project_description: str, project_structure: str) -> None:
    """
    Process code chunks and generate concise summaries.
    """
    os.makedirs(os.path.dirname(FILE_CHUNKS_FILE_PATH), exist_ok=True)
    
    try:
        with open(FILE_CHUNKS_FILE_PATH, 'r') as f:
            data: Dict[str, List[Dict[str, str]]] = json.load(f)
    except FileNotFoundError:
        print(f"Input file {FILE_CHUNKS_FILE_PATH} not found")
        return
    
    total_chunks = sum(len(chunks) for chunks in data.values())
    click.secho(f"Processing {total_chunks} chunks...")
    with click.progressbar(length=total_chunks, label="", show_pos=True) as bar:
        processed_chunks = 0
        for file_path, chunks in data.items():
            file_name = os.path.basename(file_path)
            
            for chunk in chunks:
                if not chunk.get("en-chunk"):
                    code = chunk["code-chunk"]
                    summary = generate_summary(code, file_path, project_description, project_structure)
                    chunk["en-chunk"] = summary
                processed_chunks += 1
                bar.update(1)
    
    save_json(data, FILE_CHUNKS_FILE_PATH)
