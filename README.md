# Claude Memory System

> Reduce Claude Code context usage by 90% with on-demand memory retrieval.

## The Problem

Claude Code loads your entire `CLAUDE.md` file on every prompt. As your documentation grows, you waste thousands of tokens loading irrelevant context.

```
Traditional: 34KB CLAUDE.md × 20 prompts = 172,980 tokens/session
This system: 2KB base + on-demand lookups = 17,160 tokens/session

Savings: 90% fewer tokens, ~$350/month on Opus
```

## The Solution

Instead of one massive CLAUDE.md, distribute knowledge into searchable markdown files. Claude queries only what's needed, when it's needed.

```
~/.claude-memory/           # or ./claude-memory/ for project-specific
├── infrastructure/         # Network, servers, services
├── projects/               # Project docs and status
├── runbooks/               # How-to guides
├── decisions/              # Architecture decisions
└── scripts/
    └── indexer.py          # Search index
```

## Quick Start

```bash
# Clone and run interactive setup
git clone https://github.com/YOUR_USERNAME/claude-memory-system.git
cd claude-memory-system
./install.sh
```

The installer will ask:
1. **Scope**: Global (`~/.claude-memory`) or project-specific (`./claude-memory`)?
2. **Structure**: By subject (infrastructure, projects) or by project (project-a, project-b)?
3. **Categories**: What categories do you need?

## How It Works

### 1. Write Once
Create markdown files with frontmatter:

```markdown
---
title: My API Server
category: infrastructure/servers
tags: [api, nodejs, production]
---

# My API Server

IP: 192.168.1.100
SSH: ssh user@192.168.1.100
...
```

### 2. Index
```bash
python3 ~/.claude-memory/scripts/indexer.py
```

### 3. Search (Manual or Auto)
```bash
# Manual search
python3 ~/.claude-memory/scripts/indexer.py --search "api server"

# Auto: Install hooks to inject context into prompts
```

### 4. Claude Retrieves On-Demand
When you ask about "API server", only that file's content is loaded—not your entire knowledge base.

## Installation Options

### Option A: Global Memory (Recommended)
For infrastructure, personal notes, cross-project knowledge:
```bash
./install.sh --global
```
Creates `~/.claude-memory/` accessible from any project.

### Option B: Project-Specific
For project-only context:
```bash
./install.sh --project
```
Creates `./claude-memory/` in current directory.

### Option C: Both
```bash
./install.sh --both
```
Global for infrastructure, project-specific for code context.

## Directory Templates

### By Subject (Default)
```
claude-memory/
├── infrastructure/
│   ├── servers/
│   ├── network/
│   └── services/
├── projects/
├── runbooks/
├── decisions/
└── scripts/
```

### By Project
```
claude-memory/
├── project-alpha/
│   ├── architecture.md
│   ├── api.md
│   └── deployment.md
├── project-beta/
│   └── ...
└── scripts/
```

### Minimal
```
claude-memory/
├── docs/
├── notes/
└── scripts/
```

## Hooks (Auto-Retrieval)

Install hooks to automatically inject relevant context:

```bash
# Add to ~/.claude/settings.json
{
  "hooks": {
    "UserPromptSubmit": [{
      "hooks": [{
        "type": "command",
        "command": "~/.claude-memory/hooks/memory-retrieve.sh"
      }]
    }]
  }
}
```

When you mention keywords, relevant docs are automatically added to context.

## Commands

```bash
# Index all files
python3 scripts/indexer.py

# Search
python3 scripts/indexer.py --search "keyword"

# List all indexed files
python3 scripts/indexer.py --list

# Rebuild index
python3 scripts/indexer.py --rebuild
```

## Token Savings Breakdown

| Scenario | Traditional | This System | Saved |
|----------|-------------|-------------|-------|
| Per prompt (avg) | 8,649 tokens | 1,214 tokens | 86% |
| Per session (20 prompts) | 172,980 | 17,160 | 90% |
| Per month (150 sessions) | 25.9M | 2.6M | 90% |

### Cost Savings (Claude Opus)

| Period | Traditional | This System | Saved |
|--------|-------------|-------------|-------|
| Per session | $2.59 | $0.26 | $2.34 |
| Per month | $389 | $39 | **$350** |

## Best Practices

1. **Keep CLAUDE.md minimal** - Just pointers to memory system
2. **Use frontmatter** - Helps indexer categorize and search
3. **One topic per file** - Better retrieval precision
4. **Use tags** - Improves search relevance
5. **Regular indexing** - Run after adding new files

## Example CLAUDE.md

After setup, your CLAUDE.md becomes minimal:

```markdown
# My Project

Knowledge base at `~/.claude-memory/`. Search with:
python3 ~/.claude-memory/scripts/indexer.py --search "query"

## Quick Reference
- Infrastructure: `~/.claude-memory/infrastructure/`
- Runbooks: `~/.claude-memory/runbooks/`
```

## Contributing

PRs welcome! Ideas:
- Better search algorithms
- VSCode extension
- Web UI for browsing memory
- Sync across machines

## License

MIT
