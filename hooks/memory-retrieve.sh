#!/bin/bash
#
# Claude Memory Retrieve Hook
#
# Automatically injects relevant context from memory system
# when user prompts contain matching keywords.
#
# Install: Copy to ~/.claude/hooks/ and add to settings.json
#

set -e

# Configuration - Updated by install.sh
MEMORY_PATH="$HOME/.claude-memory"
MAX_RESULTS=3
MAX_CONTEXT_CHARS=2000

# Read input from Claude
INPUT=$(cat)

# Extract user message
USER_MESSAGE=$(echo "$INPUT" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(data.get('user_prompt', ''))
except:
    pass
" 2>/dev/null)

# Skip if no message or too short
if [ -z "$USER_MESSAGE" ] || [ ${#USER_MESSAGE} -lt 10 ]; then
    echo '{"result": "continue"}'
    exit 0
fi

# Search memory for relevant context
SEARCH_RESULTS=$(python3 "$MEMORY_PATH/scripts/indexer.py" --search "$USER_MESSAGE" --limit $MAX_RESULTS --json 2>/dev/null || echo "[]")

# Check if we have results
RESULT_COUNT=$(echo "$SEARCH_RESULTS" | python3 -c "import sys,json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo "0")

if [ "$RESULT_COUNT" = "0" ]; then
    echo '{"result": "continue"}'
    exit 0
fi

# Build context message
CONTEXT=$(python3 << PYTHON
import json
import sys

results = json.loads('''$SEARCH_RESULTS''')

if not results:
    print("")
    sys.exit(0)

output = []
total_chars = 0
max_chars = $MAX_CONTEXT_CHARS

for r in results:
    title = r.get('title', 'Unknown')
    path = r.get('path', '')
    content = r.get('content', '')[:500]  # Limit per-file

    entry = f"### {title} ({path})\n{content}\n"

    if total_chars + len(entry) > max_chars:
        break

    output.append(entry)
    total_chars += len(entry)

if output:
    header = "📚 Relevant context from memory:\n\n"
    print(header + "\n".join(output))
else:
    print("")
PYTHON
)

# Output result
if [ -n "$CONTEXT" ]; then
    # Escape for JSON
    ESCAPED_CONTEXT=$(echo "$CONTEXT" | python3 -c "import sys,json; print(json.dumps(sys.stdin.read()))")

    echo "{\"result\": \"continue\", \"message\": $ESCAPED_CONTEXT}"
else
    echo '{"result": "continue"}'
fi
