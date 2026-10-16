# Project plan and progress

## Step 1: Choose a domain and build the ingestion pipeline
- [x] Select a document collection of 30-75 markdown, text, or HTML files from a real open-source project or public docs.
  - Powertools for AWS Lambda (Python) docs: 111 files loaded, ~60 contribute chunks after `:::` and `--8<--` stubs are skipped.
- [x] Write an ingestion script that loads files, extracts plain text, preserves metadata (source, section, chunk index), and skips empty content.
- [ ] Choose a chunking strategy (header-based splitting with fixed-size fallback) and document average chunk size and total chunk count.

## Step 2: Generate embeddings and index in ChromaDB
- [ ] Use the all-MiniLM-L6-v2 sentence-transformer model to generate embeddings for each chunk.
- [ ] Index chunks in ChromaDB with their text, embeddings, metadata, and unique chunk IDs.
- [ ] Confirm the index supports a full re-run from scratch and verify retrieval with a test query.

## Step 3: Build the RAG answer generation pipeline
- [ ] Implement a semantic search function that retrieves the top 3 chunks for a user question.
- [ ] Build a RAG prompt instructing the LLM to answer using only retrieved context and cite sources with bracketed labels.
- [ ] Create the Streamlit interface with a question input, generated answer, source list, and expandable retrieved context.

## Step 4: Add logging and evaluate the system
- [ ] Log each interaction to a JSONL file: timestamp, question, retrieved source IDs, scores, and the generated answer.
- [ ] Create an evaluation dataset of 15-20 questions and measure SourceHitRate@3 across the test set.
- [ ] Manually review answer quality and classify results as Accurate, Partially Accurate, Incorrect, or Not Answerable.

## Step 5: Deploy and document
- [ ] Deploy the app to Streamlit Community Cloud or Hugging Face Spaces.
- [ ] Write EVALUATION.md: dataset details, SourceHitRate@3, answer quality results, improvement ideas.
- [ ] Write a README: live demo link, architecture overview, setup instructions, example questions, and known limitations.

## Stretch goals (only after the five steps)
- [ ] Use Claude as the generation model.
- [ ] Lightweight graph-expanded retrieval from markdown links, compared against baseline SourceHitRate@3.
- [ ] Make the docs folder a setting so the pipeline runs on any corpus.
- [ ] FastAPI endpoint and Dockerfile.

## Current status (Step 1)
- Done: `load_txt`, `load_md`, `load_html`, `split_sections` (with code-fence handling), `ingest`.
- Done: `section` field, `chunk_index`, boilerplate filter (65 skipped), `chunks.jsonl` from `__main__` (931 chunks, 60 files).
- Next: fixed-size fallback for long sections, then chunk stats.