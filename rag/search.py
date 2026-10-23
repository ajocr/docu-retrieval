from pathlib import Path
import chromadb
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction

# paths are relative to this file, so the script works from the project root or from rag/
here = Path(__file__).parent

client = chromadb.PersistentClient(path=str(here / "chroma_db"))
collection = client.get_collection("docs", embedding_function=DefaultEmbeddingFunction())

def search(question, k=3):
    results = collection.query(query_texts=[question], n_results=k)

    # chroma returns one inner list per question; we only ask one, so take [0]
    ids = results["ids"][0]
    docs = results["documents"][0]
    metas = results["metadatas"][0]
    distances = results["distances"][0]

    hits = []
    for i in range(len(ids)):
        hits.append({
            "id": ids[i],
            "source": metas[i]["source"],
            "section": metas[i]["section"],
            "text": docs[i],
            # cosine similarity: 1 means identical, higher is better
            "score": 1 - distances[i],
        })
    return hits

if __name__ == "__main__":
    for hit in search("How do I add a correlation ID to my logs?"):
        print(f"{hit['score']:.3f}  {hit['id']}  ({hit['section']})")