# Document Q&A with RAG

A retrieval-augmented Q&A app over the public docs of Powertools for AWS Lambda (Python).
Portfolio project for AI ops / solutions engineer/ AI engineer roles. The goal is a deployed, measured system.

## How to work with me

I am rebuilding my coding skills and I am on a job-application deadline.

- Say in one or two sentences what you are about to do before writing code.
- Make one small change at a time, then stop so I can run it.
- Do not rewrite code I wrote. Point out the bug and explain it. Tiny obvious fixes are fine if you tell me.
- Propose options for chunking, eval questions, and prompt design, and let me decide.
- Ask me when something is ambiguous instead of guessing.
- Explain errors in plain language before fixing them.

## Stack

Python 3 on Windows (use `pathlib`), BeautifulSoup, `all-MiniLM-L6-v2` embeddings,
ChromaDB, Streamlit. LLM: Claude Haiku 5.5 (`claude-haiku-5-5`) via the `anthropic` Python SDK, chosen for cost; compare against Opus 5.5 in the eval if quality looks weak. Deployment target: TBD.

## Decisions already made

- Chunking is header-based, with a fixed-size fallback for long sections: `split_long` packs whole paragraphs up to 200 words, with no overlap. Judge it by SourceHitRate@3 on the eval set and record the result in EVALUATION.md.
- Chunk record fields: `id` (`source#chunk_index`), `source` (path relative to docs/), `section`, `chunk_index` (0-based per file, kept chunks only), `text`.
- Embeddings use Chroma's built-in `DefaultEmbeddingFunction` (all-MiniLM-L6-v2 via ONNX, no PyTorch). Use the same function for chunks and queries.
- ChromaDB is stored in `rag/chroma_db/` (git-ignored, rebuilt by `index.py`). Each run of `index.py` deletes and recreates the collection. The collection uses cosine distance. Search results report `score` as cosine similarity (1 - distance, higher is better).
- RAG prompt: retrieved chunks are numbered `[1] [2] [3]` with source and section; Claude answers only from them, cites with `[n]`, and replies exactly "I don't know based on the Powertools docs." when the context doesn't answer the question. Plain-text output.
- `#` lines inside fenced code blocks are not headings.
- Skip a chunk if every non-blank line starts with `--8<--`, `:::`, `<!--`, or a code fence. Indented lines under a `:::` directive (its options) also count as boilerplate. Log how many were skipped.
- Code samples are pulled in by `--8<--` includes and are not indexed yet. List this under known limitations.

## Rules

- Public documents only. Never use employer or clinical data.
- Never read, open, or edit `.env` files, `.streamlit/secrets.toml`, or any other file that holds credentials. Never commit API keys. If a key is needed, tell me and I will set it up myself.
- The app lives in `rag/`. Build file paths from the script's location (`Path(__file__).parent`) so scripts run from the project root or from `rag/`.

## Task list

The full five-step task list and current progress are in PLAN.md. Read it when starting a task
or when I ask what is next. Tick the checkbox when I finish a sub-step.
