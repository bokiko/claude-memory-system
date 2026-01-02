#!/usr/bin/env python3
"""
bloxcue Indexer

Index and search markdown context blocks for Claude Code.
Reduces token usage by enabling on-demand retrieval.

Usage:
    python3 indexer.py              # Index all files
    python3 indexer.py --search "query"  # Search indexed files
    python3 indexer.py --list       # List all indexed files
    python3 indexer.py --rebuild    # Force rebuild index
    python3 indexer.py --file path  # Index single file
"""

import os
import sys
import json
import re
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Set

# Configuration
SCRIPT_DIR = Path(__file__).parent
MEMORY_DIR = SCRIPT_DIR.parent
INDEX_FILE = SCRIPT_DIR / ".index.json"

# Stopwords - common words to ignore in search
STOPWORDS = {
    'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
    'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
    'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
    'should', 'may', 'might', 'must', 'shall', 'can', 'need', 'dare', 'ought',
    'used', 'it', 'its', 'this', 'that', 'these', 'those', 'i', 'you', 'he',
    'she', 'we', 'they', 'what', 'which', 'who', 'whom', 'how', 'when', 'where',
    'why', 'all', 'each', 'every', 'both', 'few', 'more', 'most', 'other',
    'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than',
    'too', 'very', 'just', 'also', 'now', 'here', 'there', 'then', 'once',
    'my', 'your', 'his', 'her', 'our', 'their', 'me', 'him', 'us', 'them',
    'if', 'else', 'elif', 'while', 'until', 'unless', 'although', 'because',
    'since', 'about', 'into', 'through', 'during', 'before', 'after', 'above',
    'below', 'between', 'under', 'again', 'further', 'any', 'get', 'got',
    'use', 'using', 'make', 'makes', 'made', 'way', 'ways', 'want', 'wants',
    'like', 'just', 'know', 'take', 'come', 'see', 'look', 'think', 'back',
    'yeah', 'yes', 'yeah', 'okay', 'ok', 'well', 'right', 'good', 'going',
}


def normalize_word(word: str) -> str:
    """Normalize a word for comparison (lowercase, strip punctuation)."""
    return re.sub(r'[^\w]', '', word.lower())


def simple_stem(word: str) -> str:
    """Simple suffix stripping for better matching."""
    word = normalize_word(word)

    # Common suffixes to strip
    suffixes = ['ing', 'ed', 'es', 's', 'er', 'est', 'ly', 'tion', 'ment', 'ness', 'ful', 'less']

    for suffix in suffixes:
        if word.endswith(suffix) and len(word) > len(suffix) + 2:
            return word[:-len(suffix)]

    return word


def fuzzy_match(query_term: str, target: str) -> float:
    """Calculate similarity between two strings (0-1)."""
    query_term = normalize_word(query_term)
    target = normalize_word(target)

    if not query_term or not target:
        return 0.0

    # Exact match
    if query_term == target:
        return 1.0

    # Substring match
    if query_term in target:
        return 0.8
    if target in query_term:
        return 0.6

    # Stem match
    if simple_stem(query_term) == simple_stem(target):
        return 0.7

    # Prefix match (at least 3 chars)
    min_len = min(len(query_term), len(target))
    if min_len >= 3:
        prefix_len = 0
        for i in range(min_len):
            if query_term[i] == target[i]:
                prefix_len += 1
            else:
                break
        if prefix_len >= 3:
            return 0.4 * (prefix_len / min_len)

    return 0.0


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

    # Add tags (high priority)
    tags = frontmatter.get("tags", [])
    if isinstance(tags, list):
        keywords.update(tags)
    elif isinstance(tags, str):
        keywords.add(tags)

    # Add title words
    title = frontmatter.get("title", "")
    if title:
        for word in title.split():
            normalized = normalize_word(word)
            if normalized and normalized not in STOPWORDS and len(normalized) > 2:
                keywords.add(normalized)

    # Add category parts
    category = frontmatter.get("category", "")
    if category:
        for part in category.replace("/", " ").replace("-", " ").split():
            normalized = normalize_word(part)
            if normalized and normalized not in STOPWORDS:
                keywords.add(normalized)

    # Extract headings
    headings = re.findall(r"^#+\s+(.+)$", content, re.MULTILINE)
    for heading in headings:
        for word in heading.split():
            normalized = normalize_word(word)
            if normalized and normalized not in STOPWORDS and len(normalized) > 2:
                keywords.add(normalized)

    # Extract code block languages
    code_langs = re.findall(r"```(\w+)", content)
    keywords.update(code_langs)

    # Extract important terms (capitalized words, technical terms)
    technical_terms = re.findall(r'\b[A-Z][a-z]+(?:[A-Z][a-z]+)+\b', content)  # CamelCase
    for term in technical_terms:
        keywords.add(term.lower())

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
            "title": frontmatter.get("title", filepath.stem.replace("-", " ").replace("_", " ").title()),
            "category": frontmatter.get("category", str(relative_path.parent)),
            "tags": frontmatter.get("tags", []),
            "keywords": extract_keywords(body, frontmatter),
            "size": stat.st_size,
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "preview": body[:300].replace("\n", " ").strip(),
        }
    except Exception as e:
        print(f"Error indexing {filepath}: {e}", file=sys.stderr)
        return None


def build_index(single_file: Optional[Path] = None) -> Dict:
    """Build index of all markdown files or update single file."""

    # Load existing index if updating single file
    if single_file and INDEX_FILE.exists():
        try:
            index = json.loads(INDEX_FILE.read_text())
            # Remove existing entry for this file
            rel_path = str(single_file.relative_to(MEMORY_DIR))
            index["files"] = [f for f in index["files"] if f["path"] != rel_path]
        except:
            index = {"files": [], "built": datetime.now().isoformat()}
    else:
        index = {"files": [], "built": datetime.now().isoformat()}

    # Determine files to index
    if single_file:
        md_files = [single_file] if single_file.exists() else []
    else:
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

    index["built"] = datetime.now().isoformat()

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
    """Search indexed files with fuzzy matching."""
    index = load_index()

    # Parse query - remove stopwords but keep important terms
    query_terms = []
    for word in query.lower().split():
        normalized = normalize_word(word)
        if normalized and len(normalized) > 1:
            # Keep the word even if it's a stopword if it seems intentional
            if normalized not in STOPWORDS or len(query.split()) <= 2:
                query_terms.append(normalized)

    if not query_terms:
        query_terms = [normalize_word(w) for w in query.lower().split() if normalize_word(w)]

    results = []

    for entry in index.get("files", []):
        score = 0.0

        # Check title (highest weight)
        title = entry.get("title", "").lower()
        for term in query_terms:
            match_score = fuzzy_match(term, title)
            if match_score > 0:
                score += 15 * match_score
            # Also check individual title words
            for title_word in title.split():
                word_score = fuzzy_match(term, title_word)
                if word_score > 0.5:
                    score += 8 * word_score

        # Check tags (high weight)
        tags = entry.get("tags", [])
        if isinstance(tags, list):
            for tag in tags:
                for term in query_terms:
                    match_score = fuzzy_match(term, tag)
                    if match_score > 0:
                        score += 10 * match_score

        # Check keywords (medium weight)
        keywords = entry.get("keywords", [])
        for keyword in keywords:
            for term in query_terms:
                match_score = fuzzy_match(term, keyword)
                if match_score > 0:
                    score += 5 * match_score

        # Check category (medium weight)
        category = entry.get("category", "").lower()
        for term in query_terms:
            for cat_part in category.replace("/", " ").split():
                match_score = fuzzy_match(term, cat_part)
                if match_score > 0:
                    score += 4 * match_score

        # Check path (low weight but useful)
        path = entry.get("path", "").lower()
        for term in query_terms:
            if term in path:
                score += 2

        # Check preview (lowest weight)
        preview = entry.get("preview", "").lower()
        for term in query_terms:
            if term in preview:
                score += 1
            # Boost if multiple terms found in preview
            term_count = preview.count(term)
            if term_count > 1:
                score += 0.5 * min(term_count, 3)

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

    for i, result in enumerate(results, 1):
        entry = result["entry"]
        score = result["score"]
        filepath = MEMORY_DIR / entry["path"]

        print(f"\n{i}. {entry['title']}")
        print(f"   Path: {entry['path']}")
        print(f"   Category: {entry['category']}")
        if entry.get("tags"):
            tags_str = ', '.join(entry['tags']) if isinstance(entry['tags'], list) else entry['tags']
            print(f"   Tags: {tags_str}")

        if verbose:
            print(f"   Score: {score:.1f}")
            if filepath.exists():
                print(f"   Preview: {entry.get('preview', '')[:150]}...")


def list_files():
    """List all indexed files."""
    index = load_index()
    files = index.get("files", [])

    print(f"Indexed blocks: {len(files)}\n")

    if not files:
        print("No files indexed yet. Add some markdown files and run the indexer.")
        return

    # Group by category
    by_category = {}
    for entry in files:
        cat = entry.get("category", "uncategorized")
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(entry)

    for category in sorted(by_category.keys()):
        print(f"{category}/")
        for entry in sorted(by_category[category], key=lambda x: x.get("title", "")):
            print(f"  • {entry['title']}")
    print()


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
        description="bloxcue Indexer - Index and search context blocks"
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
        "--file", "-f", type=str, help="Index single file"
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

    if args.file:
        filepath = Path(args.file)
        if not filepath.is_absolute():
            filepath = MEMORY_DIR / filepath

        # Security: Validate file is within MEMORY_DIR
        try:
            filepath = filepath.resolve()
            memory_dir_resolved = MEMORY_DIR.resolve()
            if not str(filepath).startswith(str(memory_dir_resolved)):
                print(f"Error: File must be within {MEMORY_DIR}", file=sys.stderr)
                sys.exit(1)
        except Exception as e:
            print(f"Error validating path: {e}", file=sys.stderr)
            sys.exit(1)

        print(f"Indexing: {filepath}")
        index = build_index(single_file=filepath)
        print(f"✓ Index updated")

    elif args.rebuild:
        print("Rebuilding index...")
        index = build_index()
        print(f"\n✓ Indexed {len(index['files'])} blocks")

    elif args.list:
        list_files()

    elif args.search:
        results = search(args.search, limit=args.limit)

        if args.json:
            output = []
            for r in results:
                entry = r["entry"].copy()
                entry["content"] = get_file_content(entry["path"])
                entry["score"] = r["score"]
                output.append(entry)
            print(json.dumps(output, indent=2))
        else:
            display_results(results, verbose=args.verbose)

    else:
        # Default: build/update index
        index = build_index()
        print(f"\n✓ Indexed {len(index['files'])} blocks")


if __name__ == "__main__":
    main()
