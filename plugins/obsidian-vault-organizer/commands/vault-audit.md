---
description: Audit your vault for tagging, linking, and structural issues
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
argument-hint: [--redetect to change vault]
---

The user wants to audit their Obsidian vault. Args: $ARGUMENTS

Follow the obsidian-vault-organizer skill — specifically the **Vault Discovery** section first (if args contain "redetect" or "change vault", clear cached path and re-detect).

1. **Resolve vault path** using the skill's vault discovery logic.
2. **Run the scanner:**
   ```bash
   python3 ${CLAUDE_PLUGIN_ROOT}/skills/obsidian-vault-organizer/scripts/scan_vault.py <vault-path>
   ```
3. **Summarize findings** grouped by category: missing frontmatter, missing type/domain/tags, unknown tags, standalone hashtags, empty Related sections.
4. **Propose fixes** for each category. Wait for approval.
5. **Apply approved fixes**, re-scan to verify, report results.
6. No git operations unless the user explicitly asks.
