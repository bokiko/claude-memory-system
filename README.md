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
    <img src="https://img.shields.io/badge/saves-60%25+%20tokens-orange" alt="60%+ savings" />
  </a>
  <a href="https://github.com/bokiko/bloxcue/blob/main/LICENSE">
    <img src="https://img.shields.io/badge/license-MIT-green" alt="MIT License" />
  </a>
</p>

<p>
  <a href="https://bokiko.io">bokiko.io</a> · <a href="https://twitter.com/bokiko">@bokiko</a>
</p>

</div>

---

## The Story

After using [Continuous-Claude](https://github.com/AnandChowdhary/continuous-claude) (created by [Anand Chowdhary](https://github.com/AnandChowdhary)) for a while, we noticed something: our `CLAUDE.md` files kept growing. Every time we documented something new, added a guide, or saved a configuration... the file got bigger.

**The problem?** Claude loads your entire `CLAUDE.md` on every single prompt. That 30KB file? Loaded 20+ times per session. That's hundreds of thousands of tokens wasted on stuff Claude didn't even need for that prompt.

**Why does this matter?** Whether you're on Claude Pro ($20/month) or Pro Max ($200/month), you have a monthly token budget. Wasting 60%+ of your tokens on irrelevant context means less tokens for actual thinking, coding, and building your projects.

**The idea:** What if Claude could pull in just the context it needs, like building blocks? You ask about your database, Claude grabs the database block. You ask about deployment, Claude grabs the deployment block. Everything else stays on the shelf.

That's **bloxcue** - context blocks that get cued up when you need them. More tokens for thinking, less tokens wasted on context you don't need.

---

## Who is this for?

| If you're... | bloxcue helps you... |
|--------------|----------------------|
| **A Claude Code user** | Stop burning tokens on context you're not using |
| **Managing multiple configs** | Keep docs, guides, and configs organized and searchable |
| **Working on several projects** | Switch context without reloading everything |
| **Hitting token limits** | Stretch your monthly budget 60%+ further |
| **New to Claude Code** | Start with good habits from day one |

---

## How it works (simple version)

**Before bloxcue:**
```
You: "How do I deploy to production?"

Claude loads: ENTIRE CLAUDE.md (34KB)
  - Your coding standards (not needed)
  - Your API documentation (not needed)
  - Your 10 different project configs (not needed)
  - Your deployment guide (NEEDED!)
  - Everything else (not needed)

Result: 8,600 tokens used, only 800 were relevant
= 90% of tokens wasted
```

**After bloxcue:**
```
You: "How do I deploy to production?"

Claude loads: Just the deployment block (1.5KB)
  - Environment setup
  - Deploy commands
  - Rollback procedures

Result: 800 tokens used, all relevant
= 60%+ more tokens available for thinking & coding
```

---

## Requirements

### You need Continuous-Claude first

bloxcue is designed to work **alongside** Continuous-Claude. They're complementary tools that make Claude Code significantly more powerful.

**What is Continuous-Claude?**

Created by [Anand Chowdhary](https://github.com/AnandChowdhary), [Continuous-Claude](https://github.com/AnandChowdhary/continuous-claude) is a context management system that helps Claude "remember" your work across sessions through ledgers, handoffs, and learnings.

| Tool | What it does |
|------|--------------|
| **Continuous-Claude** | Helps Claude remember across sessions (ledgers, handoffs, learnings) |
| **bloxcue** | Reduces token waste by loading context on-demand |

**Think of it this way:**
- Continuous-Claude = Claude's **memory** (what to remember)
- bloxcue = Claude's **filing cabinet** (where to find it efficiently)

**Install Continuous-Claude first using our guide:**
```bash
git clone https://github.com/bokiko/continuous-claude-guide.git
cd continuous-claude-guide
# Follow the step-by-step setup in the README
```

Or check out the [original repository](https://github.com/AnandChowdhary/continuous-claude) by Anand Chowdhary.

---

## Quick Start

### The Easy Way (Recommended)

**Let Claude install bloxcue for you!** This is the smoothest experience - Claude knows exactly how to set this up.

Just tell Claude:

```
Please install bloxcue for me from https://github.com/bokiko/bloxcue
Clone the repo, run the installer, and set everything up.
```

Claude will:
1. Clone the repository
2. Run the interactive installer
3. Configure the hooks
4. Set up your memory structure
5. Guide you through any choices

**That's it!** Claude handles the technical details. This is the recommended approach for most users.

---

### The Manual Way (Power Users)

If you prefer to control every step, here's the manual installation:

#### Step 1: Clone bloxcue

```bash
git clone https://github.com/bokiko/bloxcue.git
cd bloxcue
```

#### Step 2: Run the installer

```bash
./install.sh
```

The installer will ask you a few simple questions:

**Question 1: Where to install?**
- **Global** (`~/.claude-memory`) - for knowledge you use across all projects
- **Project** (`./claude-memory`) - for project-specific docs only
- **Both** - recommended for most users

**Question 2: How to organize?**
- **By subject** - infrastructure, guides, projects (best for general use)
- **By project** - project-a, project-b (best for freelancers/agencies)
- **Minimal** - just docs and notes (simplest option)

**Question 3: What categories do you need?**

Examples for common use cases:

| Use Case | Suggested Categories |
|----------|---------------------|
| **Web Developer** | apis, databases, deployment, frontend, backend |
| **DevOps/SysAdmin** | servers, networking, monitoring, security |
| **Data Scientist** | datasets, models, notebooks, pipelines |
| **Freelancer** | clients, contracts, templates, billing |
| **Student** | courses, notes, assignments, research |
| **General** | projects, guides, references, notes |

Pick what makes sense for your work. You can always add more later.

#### Step 3: Add your first block

Create a markdown file in your memory folder. Here's an example:

```bash
nano ~/.claude-memory/guides/deployment.md
```

```markdown
---
title: Production Deployment
category: guides
tags: [deployment, production, devops]
---

# Production Deployment

## Prerequisites
- SSH access to production server
- Environment variables configured
- Database migrations ready

## Deploy Steps
1. Run tests locally
2. Push to main branch
3. SSH into server
4. Pull latest changes
5. Run migrations
6. Restart services

## Rollback
If something breaks:
1. Revert to previous commit
2. Run down migrations
3. Restart services
```

#### Step 4: Index your blocks

```bash
python3 ~/.claude-memory/scripts/indexer.py
```

#### Step 5: Test it

```bash
python3 ~/.claude-memory/scripts/indexer.py --search "deployment"
```

You should see your deployment guide in the results!

---

## Enable Auto-Retrieval

**This step is required for bloxcue to work automatically.** Without this, you'd have to manually search every time.

> Want to disable auto-retrieval later? You can always remove the hook from your settings. But we recommend keeping it on - that's the whole point!

### Step 1: Add the hook

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

### Step 2: Restart Claude Code

Close and reopen Claude Code for the changes to take effect.

### Step 3: Test auto-retrieval

Ask Claude about something you documented:

```
You: "How do I deploy to production?"
```

Claude will automatically receive your deployment block as context - no manual search needed!

---

## For Existing Claude Users

Already have a big `CLAUDE.md` file? Here's how to migrate:

### Option A: Let Claude migrate for you (Recommended)

Tell Claude:

```
I have an existing CLAUDE.md file that's gotten too big.
Help me migrate it to bloxcue by:
1. Reading my current CLAUDE.md
2. Identifying distinct topics
3. Creating separate block files for each topic
4. Updating my CLAUDE.md to be minimal
```

Claude will handle the heavy lifting!

### Option B: Migrate manually

1. **Identify sections** in your current CLAUDE.md
2. **Create a block file** for each major section
3. **Move content** from CLAUDE.md to the appropriate blocks
4. **Trim your CLAUDE.md** to just essentials:

```markdown
# My Workspace

Knowledge base at `~/.claude-memory/`.
Claude automatically retrieves relevant context via hooks.

## Essential Info Only
- Project: MyApp
- Stack: Node.js, PostgreSQL
```

### For New Users / New Machines

Starting fresh? Even easier:

1. Install Continuous-Claude first
2. Install bloxcue (let Claude do it!)
3. Start with a minimal CLAUDE.md
4. Add blocks as you go

Your CLAUDE.md stays small forever because everything goes into blocks.

---

## Token Savings

Real numbers from actual usage:

| Metric | Before bloxcue | After bloxcue | Improvement |
|--------|----------------|---------------|-------------|
| Tokens per prompt | ~8,600 | ~1,200 | **86% reduction** |
| Tokens per session | ~172,000 | ~24,000 | **86% reduction** |
| Useful token ratio | ~10% | ~70%+ | **7x more efficient** |

### What this means for you

| Plan | Monthly Tokens | Before (wasted) | After (saved) |
|------|----------------|-----------------|---------------|
| **Pro** | ~45M tokens | 90% on context | 60%+ for thinking |
| **Pro Max** | ~unlimited | Still wastes context window | Cleaner, faster responses |

**Bottom line:** More tokens available for Claude to actually think about your problems instead of loading docs you don't need.

---

## Directory Structure

### By Subject (Default)

Best for: General use, mixed work, personal knowledge base

```
~/.claude-memory/
├── guides/             # How-to guides
├── references/         # Quick reference docs
├── projects/           # Project-specific info
├── configs/            # Configuration templates
├── notes/              # General notes
└── scripts/
    └── indexer.py      # Search engine
```

### By Project

Best for: Freelancers, agencies, multiple client work

```
~/.claude-memory/
├── client-alpha/
│   ├── requirements.md
│   ├── api.md
│   └── contacts.md
├── client-beta/
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

1. **Keep your CLAUDE.md minimal** - Just essentials, let blocks handle details
2. **One topic per file** - Better search precision
3. **Use frontmatter** - Title, category, tags help indexing
4. **Use descriptive tags** - `[deployment, production, aws]` not just `[deploy]`
5. **Re-index after adding files** - Run the indexer after new docs

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

The retrieval hook can return multiple relevant blocks based on keyword matching. If you ask about "database deployment", it might return both the database block and the deployment block.
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
- Any backup solution you already use
</details>

<details>
<summary><strong>Can I disable auto-retrieval?</strong></summary>

Yes, just remove the hook from your `~/.claude/settings.json`. But we recommend keeping it on - that's the whole point of bloxcue!
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

### Already have a big CLAUDE.md?

See the "For Existing Claude Users" section above - we've got you covered!

---

## Contributing

Ideas welcome! Some things we'd love help with:

- Better search algorithms (fuzzy matching, embeddings)
- VSCode extension for browsing blocks
- Web UI for managing your memory
- Sync across machines

---

## Credits

- [Anand Chowdhary](https://github.com/AnandChowdhary) - Creator of [Continuous-Claude](https://github.com/AnandChowdhary/continuous-claude)

---

## License

MIT - Use it however you want.

---

<div align="center">

Made by [@bokiko](https://twitter.com/bokiko) · [bokiko.io](https://bokiko.io)

</div>
