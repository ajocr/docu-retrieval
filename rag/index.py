from pathlib import Path
import json
import chromadb
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction

# paths are relative to this file, so the script works from the project root or from rag/
here = Path(__file__).parent
COLLECTION = "docs"

def load_chunks(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]

def fresh_collection(client):
    # rebuild from scratch every run, so the index always matches chunks.jsonl exactly
    if COLLECTION in [c.name for c in client.list_collections()]:
        client.delete_collection(COLLECTION)
        print(f"deleted old '{COLLECTION}' collection")

    # the built-in embedder is all-MiniLM-L6-v2; cosine compares vector direction, the usual choice for this model
    return client.create_collection(
        name=COLLECTION,
        embedding_function=DefaultEmbeddingFunction(),
        configuration={"hnsw": {"space": "cosine"}},
    )

if __name__ == "__main__":
    chunks = load_chunks(here / "chunks.jsonl")
    print(f"loaded {len(chunks)} chunks")

    # PersistentClient saves the database to disk in rag/chroma_db/
    client = chromadb.PersistentClient(path=str(here / "chroma_db"))
    collection = fresh_collection(client)
    #print(f"created '{collection.name}' collection")

    ids, docs, meta = [], [], []
    for c in chunks:
        ids.append(c["id"])
        docs.append(c["text"])
        meta.append({"source": c["source"], "section": c["section"], "chunk_index": c["chunk_index"]})

    collection.add(ids=ids, documents=docs, metadatas=meta)
    print(collection.count())