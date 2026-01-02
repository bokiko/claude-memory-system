# Security Policy

## Security Rating: LOW RISK

BloxCue is a **local-only** Claude Code plugin. All operations happen on your machine - no data is transmitted externally.

## What BloxCue Accesses

| Location | Access | Purpose |
|----------|--------|---------|
| `~/.claude-memory/` | Read/Write | Store and index your context blocks |
| `~/.claude/settings.json` | Read/Write | Register the retrieval hook |
| `~/.claude/hooks/` | Write | Install the hook script |

## Security Guarantees

- **No network activity** - All operations are local
- **No telemetry** - No usage data collected
- **No external dependencies** - Uses only Python standard library
- **User-controlled data** - All files stay on your machine
- **MIT License** - Fully transparent, auditable code

## Installation Safety

The `install.sh` script:
1. Creates backup of `settings.json` before modification
2. Only writes to user-controlled directories
3. Validates paths before file operations
4. Does not require elevated privileges

## Reporting Vulnerabilities

If you discover a security issue, please:
1. **Do not** open a public GitHub issue
2. Email the maintainer directly
3. Allow 90 days for a fix before public disclosure

## Audit History

| Date | Auditor | Result |
|------|---------|--------|
| 2025-01-01 | Automated Security Analysis + Corridor | SAFE |

---

## Full Security Audit Report

<details>
<summary><strong>Click to expand full audit report</strong></summary>

### Executive Summary

**BloxCue** is a Claude Code plugin that reduces token usage by implementing on-demand memory retrieval through context blocks. The repository is **legitimate and safe to use**.

### Overall Security Rating: LOW RISK

- No malicious code detected
- No network exfiltration
- No credential harvesting
- Scripts modify system configuration files (expected behavior)
- Requires file system write permissions (expected for installation)

### Detailed Analysis

#### 1. Installation Script (`install.sh`)

**Security Status: SAFE**

- Creates `~/.claude-memory/` directory structure
- Modifies `~/.claude/settings.json` to add hooks
- Creates backup before modifying settings
- No network requests during installation
- No credential collection

#### 2. Python Indexer Script (`scripts/indexer.py`)

**Security Status: SAFE**

- Reads markdown files from `~/.claude-memory/` only
- Creates local index file
- Implements path validation to prevent directory traversal
- Sanitizes search input
- Uses only Python standard library

#### 3. Hook Script (`hooks/memory-retrieve.sh`)

**Security Status: SAFE**

- Triggered on `UserPromptSubmit` event
- Calls indexer.py to find relevant blocks
- Runs in Claude Code's controlled environment
- No network activity
- Input properly sanitized before processing

#### 4. Network Security

**Status: NO NETWORK ACTIVITY**

- No HTTP/HTTPS requests
- No external API calls
- No data exfiltration
- No credential transmission
- No telemetry or tracking

#### 5. Data Privacy

- Stores markdown files locally in `~/.claude-memory/`
- Creates search index locally
- No data collection, analytics, or tracking
- All data accessible only by the user

### Vulnerability Assessment

| Severity | Count | Details |
|----------|-------|---------|
| Critical | 0 | None |
| High | 0 | None |
| Medium | 0 | Path traversal and injection mitigated |
| Low | 0 | Recommendations implemented |

### Security Checklist

- [x] No malicious code detected
- [x] No network exfiltration
- [x] No credential harvesting
- [x] No unauthorized file access
- [x] Local operations only
- [x] MIT License (transparent)
- [x] Input validation implemented
- [x] Path traversal protection
- [x] Settings backup mechanism
- [x] Error handling

</details>

---

*Last security review: 2025-01-01*
