<div align="center">

# bloxcue

<h3>Context blocks for Claude Code. Use what you need, when you need it.</h3>

<p>
  <a href="https://github.com/bokiko/continuous-claude-guide">
    <img src="https://img.shields.io/badge/Requires-Continuous--Claude-blue?style=for-the-badge" alt="Requires Continuous-Claude" />
  </a>
</p>

<p>
  <a href="#quick-start">
    <img src="https://img.shields.io/badge/setup-5%20minutes-success" alt="5 min setup" />
  </a>
  <a href="#token-savings">
    <img src="https://img.shields.io/badge/saves-90%25%20tokens-orange" alt="90% savings" />
  </a>
  <a href="https://github.com/bokiko/bloxcue/blob/main/LICENSE">
    <img src="https://img.shields.io/badge/license-MIT-green" alt="MIT License" />
  </a>
</p>

</div>

---

## The Story

After using [Continuous-Claude](https://github.com/bokiko/continuous-claude-guide) for a while, we noticed something: our `CLAUDE.md` files kept growing. Every time we documented a server, added a runbook, or saved a decision... the file got bigger.

**The problem?** Claude loads your entire `CLAUDE.md` on every single prompt. That 30KB file? Loaded 20+ times per session. That's hundreds of thousands of tokens wasted on stuff Claude didn't even need for that prompt.

**The idea:** What if Claude could pull in just the context it needs, like building blocks? You ask about your Plex server, Claude grabs the Plex block. You ask about deployment, Claude grabs the deployment block. Everything else stays on the shelf.

That's **bloxcue** - context blocks that get cued up when you need them.

---

## Who is this for?

| If you're... | bloxcue helps you... |
|--------------|----------------------|
| **A Claude Code power user** | Stop burning tokens on context you're not using |
| **Managing infrastructure** | Keep server docs, runbooks, and configs organized and searchable |
| **Working on multiple projects** | Switch context without reloading everything |
| **Paying for Claude API** | Save ~$350/month on Opus (seriously) |
| **New to Claude Code** | Start with good habits from day one |

---

## How it works (simple version)

**Before bloxcue:**
```
You: "How do I restart the Plex server?"

Claude loads: ENTIRE CLAUDE.md (34KB)
  - Your git workflow (not needed)
  - Your API keys reference (not needed)
  - Your 15 project configs (not needed)
  - Your Plex server docs (NEEDED!)
  - Everything else (not needed)

Result: 8,600 tokens used, only 500 were relevant
```

**After bloxcue:**
```
You: "How do I restart the Plex server?"

Claude loads: Just the Plex server block (2KB)
  - SSH command
  - Service name
  - Troubleshooting tips

Result: 500 tokens used, all relevant
```

---

## Requirements

### You need Continuous-Claude first

bloxcue is designed to work **alongside** [Continuous-Claude](https://github.com/bokiko/continuous-claude-guide). They're complementary:

| Tool | What it does |
|------|--------------|
| **Continuous-Claude** | Helps Claude remember across sessions (ledgers, handoffs, learnings) |
| **bloxcue** | Reduces token waste by loading context on-demand |

**Think of it this way:**
- Continuous-Claude = Claude's **memory** (what to remember)
- bloxcue = Claude's **filing cabinet** (where to find it efficiently)

If you haven't set up Continuous-Claude yet, do that first:
```bash
# Install Continuous-Claude first
git clone https://github.com/bokiko/continuous-claude-guide.git
cd continuous-claude-guide
# Follow the setup guide in the README
```

---

## Quick Start

### Step 1: Clone bloxcue

```bash
git clone https://github.com/bokiko/bloxcue.git
cd bloxcue
```

### Step 2: Run the installer

```bash
./install.sh
```

The installer will ask you a few simple questions:

1. **Where to install?**
   - Global (`~/.claude-memory`) - for stuff you use across all projects
   - Project (`./claude-memory`) - for project-specific docs
   - Both - recommended for most users

2. **How to organize?**
   - By subject (infrastructure, runbooks, projects)
   - By project (project-a, project-b)
   - Minimal (just docs and notes)

3. **What categories do you need?**
   - Pick what makes sense for you

### Step 3: Add your first block

Create a markdown file in your memory folder:

```bash
# Example: Add a server doc
nano ~/.claude-memory/infrastructure/servers/plex-server.md
```

```markdown
---
title: Plex Server
category: infrastructure/servers
tags: [plex, media, streaming]
---

# Plex Server

IP: 192.168.3.83
SSH: ssh bokiko@192.168.3.83

## Restart
sudo systemctl restart plexmediaserver

## Logs
sudo journalctl -u plexmediaserver -f
```

### Step 4: Index your blocks

```bash
python3 ~/.claude-memory/scripts/indexer.py
```

### Step 5: Test it

```bash
# Search for your block
python3 ~/.claude-memory/scripts/indexer.py --search "plex"
```

You should see your Plex server doc in the results!

---

## Part 2: Enable Auto-Retrieval (Optional but Recommended)

This is where the magic happens. Instead of manually searching, Claude automatically pulls relevant blocks when you mention keywords.

### Step 2.1: Add the hook

Edit your Claude settings:

```bash
nano ~/.claude/settings.json
```

Add this to your hooks section:

```json
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

### Step 2.2: Test auto-retrieval

Start a new Claude session and ask about something you documented:

```
You: "How do I check the Plex server logs?"
```

Claude will automatically receive the Plex server block as context - no manual search needed!

---

## Token Savings

Real numbers from actual usage:

| Metric | Before bloxcue | After bloxcue | Saved |
|--------|----------------|---------------|-------|
| Per prompt (average) | 8,649 tokens | 1,214 tokens | **86%** |
| Per session (20 prompts) | 172,980 tokens | 17,160 tokens | **90%** |
| Per month (150 sessions) | 25.9M tokens | 2.6M tokens | **90%** |

### Cost Savings (Claude Opus)

| Period | Before | After | You Save |
|--------|--------|-------|----------|
| Per session | $2.59 | $0.26 | $2.34 |
| Per month | $389 | $39 | **$350** |

---

## Directory Structure

### By Subject (Default)

Best for: Infrastructure, mixed projects, personal knowledge base

```
~/.claude-memory/
├── infrastructure/
│   ├── servers/        # Server docs
│   ├── network/        # Network configs
│   └── services/       # Service runbooks
├── projects/
│   ├── _index.md       # Project list
│   └── project-name/   # Per-project docs
├── runbooks/           # How-to guides
├── decisions/          # Why we chose X over Y
└── scripts/
    └── indexer.py      # Search engine
```

### By Project

Best for: Multiple distinct projects with separate contexts

```
~/.claude-memory/
├── project-alpha/
│   ├── architecture.md
│   ├── api.md
│   └── deployment.md
├── project-beta/
│   └── ...
└── scripts/
```

---

## Commands Reference

```bash
# Index all your blocks
python3 ~/.claude-memory/scripts/indexer.py

# Search for something
python3 ~/.claude-memory/scripts/indexer.py --search "keyword"

# List all indexed blocks
python3 ~/.claude-memory/scripts/indexer.py --list

# Rebuild index from scratch
python3 ~/.claude-memory/scripts/indexer.py --rebuild
```

---

## Best Practices

1. **Keep your CLAUDE.md minimal** - Just point to the memory system
2. **One topic per file** - Better search precision
3. **Use frontmatter** - Title, category, tags help indexing
4. **Use descriptive tags** - `[plex, media, streaming]` not just `[server]`
5. **Re-index after adding files** - Run the indexer after new docs

### Example: Minimal CLAUDE.md

After setting up bloxcue, your CLAUDE.md becomes tiny:

```markdown
# My Project

Documentation lives in `~/.claude-memory/`.
Claude automatically retrieves relevant context via hooks.

## Quick Links
- Infrastructure: ~/.claude-memory/infrastructure/
- Runbooks: ~/.claude-memory/runbooks/
- Projects: ~/.claude-memory/projects/
```

---

## FAQ

<details>
<summary><strong>Do I need Continuous-Claude to use this?</strong></summary>

Technically no, but we strongly recommend it. Continuous-Claude handles session memory (remembering what you were working on), while bloxcue handles knowledge retrieval (finding the right docs). They complement each other perfectly.

Without Continuous-Claude, you'll save tokens but lose the session continuity features.
</details>

<details>
<summary><strong>Will this work with Cursor/VS Code extensions?</strong></summary>

This is designed for **Claude Code CLI** (the terminal tool). It may work with other Claude integrations that support hooks, but we haven't tested them.
</details>

<details>
<summary><strong>How is this different from just using a smaller CLAUDE.md?</strong></summary>

Two key differences:

1. **Scalability** - Your knowledge can grow without growing your token usage
2. **Relevance** - Only the blocks relevant to your current question get loaded

A smaller CLAUDE.md means less information available. bloxcue means the right information available at the right time.
</details>

<details>
<summary><strong>What if Claude needs info from multiple blocks?</strong></summary>

The retrieval hook can return multiple relevant blocks based on keyword matching. If you ask about "Plex deployment", it might return both the Plex server block and the deployment runbook.
</details>

<details>
<summary><strong>Can I use this for project-specific docs too?</strong></summary>

Yes! You can have both:
- Global: `~/.claude-memory/` for cross-project stuff
- Project: `./claude-memory/` for project-specific docs

The installer supports setting up both.
</details>

<details>
<summary><strong>How do I back up my blocks?</strong></summary>

They're just markdown files! Back them up however you back up other files:
- Git repo (recommended)
- Cloud sync (Dropbox, iCloud, etc.)
- rsync to a NAS
</details>

---

## Troubleshooting

### "Command not found: python3"

Install Python 3:
```bash
# macOS
brew install python3

# Ubuntu/Debian
sudo apt install python3
```

### "No results found" when searching

1. Make sure you've run the indexer: `python3 ~/.claude-memory/scripts/indexer.py`
2. Check your files have the `.md` extension
3. Verify files are in the right directory

### Hook not triggering

1. Check your `~/.claude/settings.json` syntax (valid JSON?)
2. Make sure the hook path is correct
3. Restart Claude Code after changing settings

---

## Contributing

Ideas welcome! Some things we'd love help with:

- Better search algorithms (fuzzy matching, embeddings)
- VSCode extension for browsing blocks
- Web UI for managing your memory
- Sync across machines

---

## License

MIT - Use it however you want.

---

<div align="center">

**Part of the BLOX toolkit**

[bloxchaser](https://github.com/bokiko/bloxchaser) | [BloxEye](https://github.com/bokiko/BloxEye) | **bloxcue**

</div>
