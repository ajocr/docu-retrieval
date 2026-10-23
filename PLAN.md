# Project plan and progress

## Step 1: Choose a domain and build the ingestion pipeline
- [x] Select a document collection of 30-75 markdown, text, or HTML files from a real open-source project or public docs.
  - Powertools for AWS Lambda (Python) docs: 54 files contribute chunks, after site-build files and `includes/` are excluded and `:::` / `--8<--` stubs are skipped.
- [x] Write an ingestion script that loads files, extracts plain text, preserves metadata (source, section, chunk index), and skips empty content.
- [x] Choose a chunking strategy (header-based splitting with fixed-size fallback) and document average chunk size and total chunk count.
  - Header-based sections; sections over 200 words are packed by paragraph (no overlap). 1,038 chunks, average 83 words, max 200. 64 boilerplate sections skipped.

## Step 2: Generate embeddings and index in ChromaDB
- [x] Use the all-MiniLM-L6-v2 sentence-transformer model to generate embeddings for each chunk.
- [x] Index chunks in ChromaDB with their text, embeddings, metadata, and unique chunk IDs.
- [x] Confirm the index supports a full re-run from scratch and verify retrieval with a test query.

## Step 3: Build the RAG answer generation pipeline
- [x] Implement a semantic search function that retrieves the top 3 chunks for a user question.
- [ ] Build a RAG prompt instructing the LLM to answer using only retrieved context and cite sources with bracketed labels.
- [ ] Create the Streamlit interface with a question input, generated answer, source list, and expandable retrieved context.

## Step 4: Add logging and evaluate the system
- [ ] Log each interaction to a JSONL file: timestamp, question, retrieved source IDs, scores, and the generated answer.
  - [ ] Also log latency and token cost (input/output tokens) per query.
- [ ] Create an evaluation dataset of 15-20 questions and measure SourceHitRate@3 across the test set.
  - [ ] Include 3-5 out-of-scope questions the docs can't answer; check the app says "I don't know" and doesn't invent an answer.
- [ ] Manually review answer quality and classify results as Accurate, Partially Accurate, Incorrect, or Not Answerable.
- [ ] Run one before/after chunking experiment (e.g. no overlap vs overlap) and report both SourceHitRate@3 values. "No difference" is a valid finding.

## Step 5: Deploy and document
- [ ] Deploy the app to Streamlit Community Cloud or Hugging Face Spaces.
- [ ] Write EVALUATION.md: dataset details, SourceHitRate@3, answer quality results, improvement ideas.
- [ ] Write a README: live demo link, architecture overview, setup instructions, example questions, and known limitations.
  - [ ] Add a "What broke" section: empty `api_doc/` chunks (`:::` stubs), code samples missing behind `--8<--` includes, and what was done about each.

## Stretch goals (only after the five steps)
- [ ] Use Claude as the generation model.
- [ ] Lightweight graph-expanded retrieval from markdown links, compared against baseline SourceHitRate@3.
- [ ] Make the docs folder a setting so the pipeline runs on any corpus.
- [ ] FastAPI endpoint and Dockerfile.

## Current status
- Step 1 done: `chunks.jsonl` has 1,038 chunks from 54 files (average 83 words).
- Step 2 done: 1,038 chunks indexed in `rag/chroma_db/` (cosine, built-in MiniLM embedder) in ~9s.
- Test query "How do I add a correlation ID to my logs?" returned 3 core/logger.md correlation-ID chunks (distance 0.38-0.45).
- Step 3: `search(question, k=3)` in rag/search.py returns id, source, section, text, score (cosine similarity).
- Next: choose the LLM, then build the RAG prompt.