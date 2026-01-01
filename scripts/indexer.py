#!/usr/bin/env python3
"""
Claude Memory Indexer

Index and search markdown knowledge files for Claude Code.
Reduces context usage by enabling on-demand retrieval.

Usage:
    python3 indexer.py              # Index all files
    python3 indexer.py --search "query"  # Search indexed files
    python3 indexer.py --list       # List all indexed files
    python3 indexer.py --rebuild    # Force rebuild index
"""

import os
import sys
import json
import re
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# Configuration
SCRIPT_DIR = Path(__file__).parent
MEMORY_DIR = SCRIPT_DIR.parent
INDEX_FILE = SCRIPT_DIR / ".index.json"
CACHE_DIR = SCRIPT_DIR / ".cache"


def parse_frontmatter(content: str) -> Tuple[Dict, str]:
    """Extract YAML frontmatter and content from markdown."""
    frontmatter = {}
    body = content

    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            fm_text = parts[1].strip()
            body = parts[2].strip()

            # Simple YAML parsing (no external deps)
            for line in fm_text.split("\n"):
                if ":" in line:
                    key, value = line.split(":", 1)
                    key = key.strip()
                    value = value.strip()

                    # Handle arrays [item1, item2]
                    if value.startswith("[") and value.endswith("]"):
                        items = value[1:-1].split(",")
                        value = [item.strip().strip("'\"") for item in items]

                    frontmatter[key] = value

    return frontmatter, body


def extract_keywords(content: str, frontmatter: Dict) -> List[str]:
    """Extract searchable keywords from content."""
    keywords = set()

    # Add tags
    tags = frontmatter.get("tags", [])
    if isinstance(tags, list):
        keywords.update(tags)
    elif isinstance(tags, str):
        keywords.add(tags)

    # Add title words
    title = frontmatter.get("title", "")
    if title:
        keywords.update(title.lower().split())

    # Add category
    category = frontmatter.get("category", "")
    if category:
        keywords.update(category.lower().replace("/", " ").split())

    # Extract headings
    headings = re.findall(r"^#+\s+(.+)$", content, re.MULTILINE)
    for heading in headings:
        keywords.update(heading.lower().split())

    # Extract code block languages
    code_langs = re.findall(r"```(\w+)", content)
    keywords.update(code_langs)

    # Clean keywords
    keywords = {k.strip().lower() for k in keywords if len(k) > 2}

    return list(keywords)


def index_file(filepath: Path) -> Optional[Dict]:
    """Index a single markdown file."""
    try:
        content = filepath.read_text(encoding="utf-8")
        frontmatter, body = parse_frontmatter(content)

        relative_path = filepath.relative_to(MEMORY_DIR)
        stat = filepath.stat()

        return {
            "path": str(relative_path),
            "title": frontmatter.get("title", filepath.stem),
            "category": frontmatter.get("category", str(relative_path.parent)),
            "tags": frontmatter.get("tags", []),
            "keywords": extract_keywords(body, frontmatter),
            "size": stat.st_size,
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "preview": body[:200].replace("\n", " ").strip(),
        }
    except Exception as e:
        print(f"Error indexing {filepath}: {e}", file=sys.stderr)
        return None


def build_index() -> Dict:
    """Build index of all markdown files."""
    index = {"files": [], "built": datetime.now().isoformat()}

    # Find all markdown files
    md_files = list(MEMORY_DIR.rglob("*.md"))

    for filepath in md_files:
        # Skip hidden files and scripts directory
        if any(part.startswith(".") for part in filepath.parts):
            continue
        if "scripts" in filepath.parts:
            continue

        entry = index_file(filepath)
        if entry:
            index["files"].append(entry)
            print(f"Indexed: {entry['path']}")

    # Save index
    INDEX_FILE.parent.mkdir(parents=True, exist_ok=True)
    INDEX_FILE.write_text(json.dumps(index, indent=2))

    return index


def load_index() -> Dict:
    """Load existing index or build new one."""
    if INDEX_FILE.exists():
        try:
            return json.loads(INDEX_FILE.read_text())
        except:
            pass
    return build_index()


def search(query: str, limit: int = 5) -> List[Dict]:
    """Search indexed files."""
    index = load_index()
    query_terms = query.lower().split()
    results = []

    for entry in index.get("files", []):
        score = 0

        # Check title
        title = entry.get("title", "").lower()
        for term in query_terms:
            if term in title:
                score += 10

        # Check tags
        tags = entry.get("tags", [])
        if isinstance(tags, list):
            for tag in tags:
                for term in query_terms:
                    if term in tag.lower():
                        score += 5

        # Check keywords
        keywords = entry.get("keywords", [])
        for keyword in keywords:
            for term in query_terms:
                if term in keyword:
                    score += 2

        # Check category
        category = entry.get("category", "").lower()
        for term in query_terms:
            if term in category:
                score += 3

        # Check preview
        preview = entry.get("preview", "").lower()
        for term in query_terms:
            if term in preview:
                score += 1

        if score > 0:
            results.append({"entry": entry, "score": score})

    # Sort by score
    results.sort(key=lambda x: x["score"], reverse=True)

    return results[:limit]


def display_results(results: List[Dict], verbose: bool = False):
    """Display search results."""
    if not results:
        print("No results found.")
        return

    for result in results:
        entry = result["entry"]
        filepath = MEMORY_DIR / entry["path"]

        print(f"\n📄 {entry['title']} ({entry['path']})")
        print(f"   Category: {entry['category']}")
        if entry.get("tags"):
            print(f"   Tags: {', '.join(entry['tags']) if isinstance(entry['tags'], list) else entry['tags']}")

        if verbose and filepath.exists():
            print(f"   ---")
            content = filepath.read_text()[:500]
            _, body = parse_frontmatter(content)
            print(f"   {body[:300]}...")


def list_files():
    """List all indexed files."""
    index = load_index()

    print(f"Indexed files ({len(index.get('files', []))}):\n")

    # Group by category
    by_category = {}
    for entry in index.get("files", []):
        cat = entry.get("category", "uncategorized")
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(entry)

    for category in sorted(by_category.keys()):
        print(f"{category}/")
        for entry in by_category[category]:
            print(f"  - {entry['title']}")


def get_file_content(path: str) -> str:
    """Get full content of a file for context injection."""
    filepath = MEMORY_DIR / path
    if filepath.exists():
        content = filepath.read_text()
        _, body = parse_frontmatter(content)
        return body
    return ""


def main():
    parser = argparse.ArgumentParser(
        description="Claude Memory Indexer - Index and search knowledge files"
    )
    parser.add_argument(
        "--search", "-s", type=str, help="Search query"
    )
    parser.add_argument(
        "--list", "-l", action="store_true", help="List all indexed files"
    )
    parser.add_argument(
        "--rebuild", "-r", action="store_true", help="Force rebuild index"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Show more details"
    )
    parser.add_argument(
        "--limit", "-n", type=int, default=5, help="Max results (default: 5)"
    )
    parser.add_argument(
        "--json", "-j", action="store_true", help="Output as JSON"
    )

    args = parser.parse_args()

    if args.rebuild:
        print("Rebuilding index...")
        index = build_index()
        print(f"\n✅ Indexed {len(index['files'])} files")

    elif args.list:
        list_files()

    elif args.search:
        results = search(args.search, limit=args.limit)

        if args.json:
            output = []
            for r in results:
                entry = r["entry"]
                entry["content"] = get_file_content(entry["path"])
                output.append(entry)
            print(json.dumps(output, indent=2))
        else:
            display_results(results, verbose=args.verbose)

    else:
        # Default: build/update index
        index = build_index()
        print(f"\n✅ Indexed {len(index['files'])} files")


if __name__ == "__main__":
    main()
