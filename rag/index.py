from pathlib import Path
import json

# paths are relative to this file, so the script works from the project root or from rag/
here = Path(__file__).parent

def load_chunks(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]

if __name__ == "__main__":
    chunks = load_chunks(here / "chunks.jsonl")
    print(f"loaded {len(chunks)} chunks")
