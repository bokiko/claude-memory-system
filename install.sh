#!/bin/bash
set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║           Claude Memory System - Setup Wizard             ║"
echo "║         Reduce context usage by 90%                       ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Detect script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ============================================
# STEP 1: Installation Scope
# ============================================
echo -e "${YELLOW}Step 1/4: Installation Scope${NC}"
echo ""
echo "Where should Claude Memory be installed?"
echo ""
echo "  1) Global (~/.claude-memory)"
echo "     Best for: Infrastructure docs, personal notes, cross-project knowledge"
echo ""
echo "  2) Project-specific (./claude-memory)"
echo "     Best for: Project-only context, team sharing via git"
echo ""
echo "  3) Both (global + project)"
echo "     Best for: Personal infra docs + project-specific code context"
echo ""
read -p "Choose [1/2/3] (default: 1): " SCOPE_CHOICE
SCOPE_CHOICE=${SCOPE_CHOICE:-1}

case $SCOPE_CHOICE in
    1) INSTALL_PATHS=("$HOME/.claude-memory") ;;
    2) INSTALL_PATHS=("$(pwd)/claude-memory") ;;
    3) INSTALL_PATHS=("$HOME/.claude-memory" "$(pwd)/claude-memory") ;;
    *) INSTALL_PATHS=("$HOME/.claude-memory") ;;
esac

echo ""

# ============================================
# STEP 2: Directory Structure
# ============================================
echo -e "${YELLOW}Step 2/4: Directory Structure${NC}"
echo ""
echo "How do you want to organize your knowledge?"
echo ""
echo "  1) By Subject (recommended)"
echo "     infrastructure/, projects/, runbooks/, decisions/"
echo ""
echo "  2) By Project"
echo "     project-a/, project-b/, shared/"
echo ""
echo "  3) Minimal"
echo "     docs/, notes/"
echo ""
echo "  4) Custom"
echo "     You specify the folders"
echo ""
read -p "Choose [1/2/3/4] (default: 1): " STRUCTURE_CHOICE
STRUCTURE_CHOICE=${STRUCTURE_CHOICE:-1}

case $STRUCTURE_CHOICE in
    1)
        FOLDERS=("infrastructure/servers" "infrastructure/network" "infrastructure/services" "projects" "runbooks" "decisions")
        ;;
    2)
        echo ""
        read -p "Enter project names (comma-separated, e.g., api,frontend,shared): " PROJECTS
        IFS=',' read -ra PROJECT_ARRAY <<< "$PROJECTS"
        FOLDERS=()
        for proj in "${PROJECT_ARRAY[@]}"; do
            FOLDERS+=("$(echo "$proj" | xargs)")  # trim whitespace
        done
        FOLDERS+=("shared")
        ;;
    3)
        FOLDERS=("docs" "notes")
        ;;
    4)
        echo ""
        read -p "Enter folder names (comma-separated): " CUSTOM_FOLDERS
        IFS=',' read -ra FOLDERS <<< "$CUSTOM_FOLDERS"
        ;;
esac

echo ""

# ============================================
# STEP 3: Install Hooks
# ============================================
echo -e "${YELLOW}Step 3/4: Auto-Retrieval Hooks${NC}"
echo ""
echo "Install Claude Code hooks for automatic context injection?"
echo "This adds relevant memory to your prompts automatically."
echo ""
read -p "Install hooks? [Y/n] (default: Y): " INSTALL_HOOKS
INSTALL_HOOKS=${INSTALL_HOOKS:-Y}

echo ""

# ============================================
# STEP 4: Confirm
# ============================================
echo -e "${YELLOW}Step 4/4: Confirm Installation${NC}"
echo ""
echo "Ready to install with these settings:"
echo ""
echo -e "  ${GREEN}Install paths:${NC}"
for path in "${INSTALL_PATHS[@]}"; do
    echo "    - $path"
done
echo ""
echo -e "  ${GREEN}Folders:${NC}"
for folder in "${FOLDERS[@]}"; do
    echo "    - $folder/"
done
echo ""
echo -e "  ${GREEN}Hooks:${NC} $([ "$INSTALL_HOOKS" = "Y" ] || [ "$INSTALL_HOOKS" = "y" ] && echo "Yes" || echo "No")"
echo ""
read -p "Proceed? [Y/n]: " CONFIRM
CONFIRM=${CONFIRM:-Y}

if [ "$CONFIRM" != "Y" ] && [ "$CONFIRM" != "y" ]; then
    echo "Installation cancelled."
    exit 0
fi

echo ""
echo -e "${BLUE}Installing...${NC}"
echo ""

# ============================================
# CREATE DIRECTORIES
# ============================================
for INSTALL_PATH in "${INSTALL_PATHS[@]}"; do
    echo -e "${GREEN}Creating $INSTALL_PATH${NC}"

    mkdir -p "$INSTALL_PATH"

    # Create folder structure
    for folder in "${FOLDERS[@]}"; do
        mkdir -p "$INSTALL_PATH/$folder"
        echo "  Created: $folder/"
    done

    # Create scripts directory
    mkdir -p "$INSTALL_PATH/scripts"

    # Copy indexer
    cp "$SCRIPT_DIR/scripts/indexer.py" "$INSTALL_PATH/scripts/"
    echo "  Installed: scripts/indexer.py"

    # Create example file
    FIRST_FOLDER="${FOLDERS[0]}"
    cat > "$INSTALL_PATH/$FIRST_FOLDER/example.md" << 'EXAMPLE'
---
title: Example Document
category: example
tags: [example, template]
updated: $(date +%Y-%m-%d)
---

# Example Document

This is an example memory file. Replace with your own content.

## Structure

Each file should have:
1. YAML frontmatter (title, category, tags)
2. Markdown content
3. Focused, single-topic information

## Tips

- One topic per file
- Use descriptive tags
- Keep files under 500 lines
- Run indexer after adding files
EXAMPLE
    echo "  Created: $FIRST_FOLDER/example.md"

    # Create CLAUDE.md pointer
    cat > "$INSTALL_PATH/CLAUDE.md" << CLAUDEMD
# Claude Memory

Knowledge base location: $INSTALL_PATH

## Search

\`\`\`bash
python3 $INSTALL_PATH/scripts/indexer.py --search "query"
\`\`\`

## Structure

$(for folder in "${FOLDERS[@]}"; do echo "- $folder/"; done)

## Index

Run after adding new files:
\`\`\`bash
python3 $INSTALL_PATH/scripts/indexer.py
\`\`\`
CLAUDEMD
    echo "  Created: CLAUDE.md"
done

# ============================================
# INSTALL HOOKS
# ============================================
if [ "$INSTALL_HOOKS" = "Y" ] || [ "$INSTALL_HOOKS" = "y" ]; then
    echo ""
    echo -e "${GREEN}Installing hooks...${NC}"

    HOOKS_DIR="$HOME/.claude/hooks"
    mkdir -p "$HOOKS_DIR"

    # Copy hook files
    cp "$SCRIPT_DIR/hooks/memory-retrieve.sh" "$HOOKS_DIR/"
    chmod +x "$HOOKS_DIR/memory-retrieve.sh"
    echo "  Installed: memory-retrieve.sh"

    # Update the hook to use correct path
    MEMORY_PATH="${INSTALL_PATHS[0]}"
    sed -i.bak "s|MEMORY_PATH=.*|MEMORY_PATH=\"$MEMORY_PATH\"|" "$HOOKS_DIR/memory-retrieve.sh" 2>/dev/null || \
    sed -i '' "s|MEMORY_PATH=.*|MEMORY_PATH=\"$MEMORY_PATH\"|" "$HOOKS_DIR/memory-retrieve.sh"
    rm -f "$HOOKS_DIR/memory-retrieve.sh.bak"

    # Check if settings.json exists
    SETTINGS_FILE="$HOME/.claude/settings.json"
    if [ -f "$SETTINGS_FILE" ]; then
        echo ""
        echo -e "${YELLOW}Note: ~/.claude/settings.json exists.${NC}"
        echo "Add this hook configuration manually:"
        echo ""
        cat << 'HOOKCONFIG'
{
  "hooks": {
    "UserPromptSubmit": [{
      "hooks": [{
        "type": "command",
        "command": "~/.claude/hooks/memory-retrieve.sh"
      }]
    }]
  }
}
HOOKCONFIG
    else
        # Create settings.json
        cat > "$SETTINGS_FILE" << 'SETTINGS'
{
  "hooks": {
    "UserPromptSubmit": [{
      "hooks": [{
        "type": "command",
        "command": "~/.claude/hooks/memory-retrieve.sh"
      }]
    }]
  }
}
SETTINGS
        echo "  Created: ~/.claude/settings.json"
    fi
fi

# ============================================
# RUN INITIAL INDEX
# ============================================
echo ""
echo -e "${GREEN}Running initial index...${NC}"
for INSTALL_PATH in "${INSTALL_PATHS[@]}"; do
    python3 "$INSTALL_PATH/scripts/indexer.py" 2>/dev/null || echo "  Index will run when you add files"
done

# ============================================
# DONE
# ============================================
echo ""
echo -e "${BLUE}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                    Setup Complete!                        ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "Next steps:"
echo ""
echo "  1. Add your knowledge files to:"
for INSTALL_PATH in "${INSTALL_PATHS[@]}"; do
    echo "     $INSTALL_PATH"
done
echo ""
echo "  2. Index your files:"
echo "     python3 ${INSTALL_PATHS[0]}/scripts/indexer.py"
echo ""
echo "  3. Search:"
echo "     python3 ${INSTALL_PATHS[0]}/scripts/indexer.py --search \"keyword\""
echo ""
echo "  4. Update your project's CLAUDE.md to point to memory system"
echo ""
echo -e "${GREEN}Enjoy 90% less context usage!${NC}"
