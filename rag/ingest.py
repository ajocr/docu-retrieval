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

        text = loader(path)
        source = path.relative_to(docs_dir).as_posix()

        chunk_index = 0
        for section, body in split_sections(text):
            if not body.strip():
                continue
            if is_boilerplate(body):
                skipped += 1
                continue
            records.append({
                "id": f"{source}#{chunk_index}",
                "source": source,
                "section": section,
                "chunk_index": chunk_index,
                "text": body.strip(),
            })
            chunk_index += 1

    print(f"skipped {skipped} boilerplate chunks")
    return records

if __name__ == "__main__":
    records = ingest("docs")
    with open("chunks.jsonl", "w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    print(f"wrote {len(records)} records to chunks.jsonl")
