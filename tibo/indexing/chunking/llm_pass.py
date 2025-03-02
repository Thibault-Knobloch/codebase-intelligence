import json
import requests
import os
import click
from typing import Dict, List, Optional
import time
from requests.exceptions import HTTPError
from ...utils import FILE_CHUNKS_FILE_PATH, OPENAI_API_KEY, OPENAI_API_URL, save_json


def generate_summaries_for_file(
    code_chunks: List[str],
    file_path: str,
    project_description: str,
    project_structure: str
) -> List[str]:
    """
    Generate minimal summaries for all code chunks in a file in one API call.
    """
    retry_delays = [1, 2, 4, 8, 16]  # Exponential backoff delays in seconds
    
    if not any(chunk.strip() for chunk in code_chunks):
        return ["Empty chunk: No functionality to summarize."] * len(code_chunks)

    for attempt, delay in enumerate(retry_delays + [None]):
        try:
            # Format all chunks into a single prompt with explicit numbering
            chunks_text = "\n\n".join(
                f"Chunk {i}:\n```python\n{chunk.strip()}\n```" for i, chunk in enumerate(code_chunks)
            )
            prompt = (
                "Summarize each code chunk concisely using this format:\n"
                "<function/class name/CHUNK_<index> if not found>: <brief purpose in 20 words or less>\n"
                "Rules:\n"
                "- Provide EXACTLY one summary per chunk, even if empty, trivial, or redundant.\n"
                "- Match the number of summaries to the number of chunks (e.g., if 9 chunks, return 9 summaries).\n"
                "- Do NOT skip chunks or combine them—treat each as independent.\n"
                "- Output ONLY the summaries, one per line, with NO extra blank lines or text.\n"
                "- Use 'CHUNK_<index>' (e.g., CHUNK_0) if no clear function/class name is present.\n"
                f"Project context: {project_description}\n"
                f"Project structure: {project_structure}\n"
                f"File: {file_path}\n"
                f"Chunks (total: {len(code_chunks)}):\n{chunks_text}\n"
            )
            
            headers = {
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 250 * len(code_chunks),
                "temperature": 0.3  # Lower temperature for stricter adherence
            }
            
            response = requests.post(OPENAI_API_URL, headers=headers, json=payload)
            response.raise_for_status()
            
            # Parse summaries
            raw_response = response.json()["choices"][0]["message"]["content"].strip()
            summaries = [line.strip() for line in raw_response.split("\n") if line.strip()]
            
            # Validate length and pad/truncate if necessary
            if len(summaries) != len(code_chunks):
                print(f"\nWarning: Expected {len(code_chunks)} summaries, got {len(summaries)}. Adjusting...")
                # Pad with error messages if too few
                if len(summaries) < len(code_chunks):
                    summaries.extend(
                        [f"CHUNK_{i}: Error - Summary missing from LLM response" 
                         for i in range(len(summaries), len(code_chunks))]
                    )
                # Truncate if too many
                summaries = summaries[:len(code_chunks)]
            return summaries
        
        except HTTPError as e:
            if e.response.status_code == 400:
                return [f"Error: Bad Request - Invalid input for chunk {i}" for i in range(len(code_chunks))]
            elif e.response.status_code == 429 and delay is not None:
                print(f"Rate limit hit for file {file_path}, retrying in {delay}s...")
                time.sleep(delay)
            else:
                return [f"Error: HTTP {e.response.status_code} for chunk {i}" for i in range(len(code_chunks))]
        except Exception as e:
            return [f"Error: {str(e)}" for _ in range(len(code_chunks))]
        

def process_json_file(project_description: str, project_structure: str) -> None:
    """
    Process code chunks and generate concise summaries, batching by file.
    """
    os.makedirs(os.path.dirname(FILE_CHUNKS_FILE_PATH), exist_ok=True)
    
    try:
        with open(FILE_CHUNKS_FILE_PATH, 'r') as f:
            data: Dict[str, List[Dict[str, str]]] = json.load(f)
    except FileNotFoundError:
        print(f"Input file {FILE_CHUNKS_FILE_PATH} not found")
        return
    
    total_chunks = sum(len(chunks) for chunks in data.values())
    total_files = len(data)
    click.secho(f"Processing {total_chunks} chunks across {total_files} files...")
    with click.progressbar(length=total_files, label="", show_pos=True) as bar:
        for file_path, chunks in data.items():
            # Collect all code chunks for this file
            code_chunks = [chunk["code-chunk"] for chunk in chunks if not chunk.get("en-chunk")]
            if code_chunks:  # Only make a call if there are unsummarized chunks
                summaries = generate_summaries_for_file(code_chunks, file_path, project_description, project_structure)
                # Assign summaries back to chunks that need them
                summary_idx = 0
                for chunk in chunks:
                    if not chunk.get("en-chunk"):
                        chunk["en-chunk"] = summaries[summary_idx]
                        summary_idx += 1
            bar.update(1)
    
    save_json(data, FILE_CHUNKS_FILE_PATH)
