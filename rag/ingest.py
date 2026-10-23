from pathlib import Path
import json
import re
from bs4 import BeautifulSoup

def load_txt(path):
    with open(path, encoding="utf-8") as f:
        content = f.read()

    return content

def load_md(path):
    with open(path, encoding="utf-8") as f:
        content = f.read()

    if content.startswith("---"):
        #content.find("---")
        end_position = content.find("---", 3)

        if end_position != -1:
            content = content[end_position + 3:]
            
    return content.strip()

def load_html(path):
    all_tags = ['script', 'style', 'nav', 'header', 'footer']
    with open(path, encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')
        for tag in all_tags:
            #soup.find_all(tag)
            for t in soup.find_all(tag):
                t.decompose()
        text = soup.get_text(separator="\n")

    return text.strip()

LOADERS = {".txt": load_txt, ".md": load_md, ".html": load_html}

# files that build the docs site rather than document Powertools (paths relative to docs/)
EXCLUDE = {"requirements.txt", "overrides/main.html", "diagram_src/cicd_steps.md"}
# includes/ snippets get pasted into other pages at build time, so their text is already indexed there
EXCLUDE_DIRS = ("includes/",)

HEADING = re.compile(r"^#{1,6}\s")

def split_sections(text):
    sections = []
    section = ""
    body_lines = []
    in_code = False

    # return a list of (section, body) pairs
    # for markdown: a new section starts at each line beginning with "#"
    for line in text.split("\n"):
        # lines inside ``` fences can start with "#" (python comments), so don't treat them as sections
        if line.lstrip().startswith("```"):
            in_code = not in_code

        # real headings have a space after the hashes, so "#hashtag" or "#!/bin/bash" don't count
        if not in_code and HEADING.match(line):
            sections.append((section, "\n".join(body_lines)))
            section = line.lstrip("#").strip()
            body_lines = []
        else:
            body_lines.append(line)

    sections.append((section, "\n".join(body_lines)))
    return sections

def is_boilerplate(body):
    # api_doc pages are just "::: module.path" lines (plus indented options and lint comments)
    # that mkdocs expands at build time, so there's no real text to retrieve
    prefixes = ("--8<--", ":::", "<!--", "```")
    lines = [l for l in body.split("\n") if l.strip()]
    if not lines:
        return False
    # indented lines are only boilerplate when they're options under a ::: directive
    has_directive = any(l.lstrip().startswith(":::") for l in lines)
    return all(l.strip().startswith(prefixes) or (has_directive and l.startswith((" ", "\t"))) for l in lines)

# all-MiniLM-L6-v2 stops reading at 256 tokens, which is roughly 200 words of prose
MAX_WORDS = 200

def split_long(body, max_words=MAX_WORDS):
    # sections short enough for the model to read whole stay as one chunk
    if len(body.split()) <= max_words:
        return [body]

    # 1. break the body into paragraphs on blank lines, keeping ``` code blocks in one piece
    paragraphs = []
    para_lines = []
    in_code = False
    for line in body.split("\n"):
        if line.lstrip().startswith("```"):
            in_code = not in_code
        if not in_code and not line.strip():
            if para_lines:
                paragraphs.append("\n".join(para_lines))
                para_lines = []
        else:
            para_lines.append(line)
    if para_lines:
        paragraphs.append("\n".join(para_lines))

    # 2. pack paragraphs into chunks of up to max_words, no overlap
    chunks = []
    packed = []
    packed_words = 0
    for para in paragraphs:
        words = len(para.split())
        if words > max_words:
            # one paragraph is too long by itself: close the current chunk, then cut it into fixed word windows
            if packed:
                chunks.append("\n\n".join(packed))
                packed, packed_words = [], 0
            para_words = para.split()
            for i in range(0, len(para_words), max_words):
                chunks.append(" ".join(para_words[i:i + max_words]))
            continue
        if packed and packed_words + words > max_words:
            chunks.append("\n\n".join(packed))
            packed, packed_words = [], 0
        packed.append(para)
        packed_words += words
    if packed:
        chunks.append("\n\n".join(packed))

    return chunks

def ingest(docs_dir):
    records = []
    # 1. walk docs_dir for files
    # 2. pick the loader by file extension
    # 3. split into sections
    # 4. skip any section where body.strip() is empty
    # 5. build a record dict for each remaining one
    docs_dir = Path(docs_dir)
    skipped = 0

    for path in sorted(docs_dir.rglob("*")):
        loader = LOADERS.get(path.suffix.lower())
        if not path.is_file() or loader is None:
            continue

        source = path.relative_to(docs_dir).as_posix()
        if source in EXCLUDE or source.startswith(EXCLUDE_DIRS):
            continue
        text = loader(path)

        chunk_index = 0
        for section, body in split_sections(text):
            if not body.strip():
                continue
            if is_boilerplate(body):
                skipped += 1
                continue
            for piece in split_long(body.strip()):
                records.append({
                "id": f"{source}#{chunk_index}",
                "source": source,
                "section": section,
                "chunk_index": chunk_index,
                "text": piece,
                })
                chunk_index += 1

    print(f"skipped {skipped} boilerplate chunks")
    return records

if __name__ == "__main__":
    # paths are relative to this file, so the script works from the project root or from rag/
    here = Path(__file__).parent
    records = ingest(here / "docs")
    with open(here / "chunks.jsonl", "w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    print(f"wrote {len(records)} records to chunks.jsonl")

    word_counts = [len(r["text"].split()) for r in records]
    print(f"average chunk size: {sum(word_counts) / len(word_counts):.0f} words (max {max(word_counts)})")
