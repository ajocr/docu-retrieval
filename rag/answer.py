import anthropic
from dotenv import load_dotenv
from search import search

load_dotenv()
client = anthropic.Anthropic()
MODEL = "claude-haiku-5-5"

SYSTEM_PROMPT = """You are a documentation assistant for Powertools for AWS Lambda (Python).

Rules:
1. Answer only from the numbered context passages. Do not use outside knowledge,
   even if you know the answer.
2. Cite each sentence that uses the context with its passage number, like [1].
   Only cite passages you actually used.
3. If the context only partly answers the question, answer that part and say
   what the docs here don't cover.
4. If the context does not answer the question at all, reply exactly:
   I don't know based on the Powertools docs.
5. Plain text only: no markdown headings, bold, or bullet lists. Keep it under
   150 words."""


def build_context(hits):
    # number passages from 1 so the labels match the [n] citations in the answer
    blocks = []
    for n, hit in enumerate(hits, start=1):
        blocks.append(f"[{n}] {hit['source']} — {hit['section']}\n{hit['text']}")
    return "\n\n".join(blocks)


def build_user_message(question, hits):
    return f"Context:\n{build_context(hits)}\n\nQuestion: {question}"


def answer(question, k=3):
    hits = search(question, k=k)
    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        # low effort: short grounded answers don't need much thinking, and it keeps cost down
        output_config={"effort": "low"},
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": build_user_message(question, hits)}],
    )
    # response.content can include thinking blocks; keep only the text
    text = "".join(block.text for block in response.content if block.type == "text")
    return {
        "answer": text,
        "hits": hits,
        "stop_reason": response.stop_reason,
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
    }


if __name__ == "__main__":
    result = answer("How do I add a correlation ID to my logs?")
    print(result["answer"])
    print("\nSources:")
    for n, hit in enumerate(result["hits"], start=1):
        print(f"[{n}] {hit['source']} — {hit['section']} (score {hit['score']:.3f})")
    print(
        f"\nstop_reason={result['stop_reason']}  tokens in/out: {result['input_tokens']}/{result['output_tokens']}"
    )
