---
description: Search, get briefings, or explore connections in your vault
allowed-tools: Read, Bash, Grep, Glob, WebSearch, WebFetch
argument-hint: [search query, topic, or note name]
---

The user wants to read from their Obsidian vault. Query: $ARGUMENTS

Follow the obsidian-vault-organizer skill — specifically the **Vault Discovery** section first, then route:

1. **Resolve vault path** using the skill's vault discovery logic.
2. **Determine intent from the query:**
   - **Search** (default — keywords, tag names, "find X", "what do I have on X") → search using `rg` across vault markdown files + frontmatter. Summarize matches with one-sentence descriptions, grouped by type/domain.
   - **Briefing** ("brief me on X", "summarize my notes on X", "what do I know about X") → find all relevant notes, read them fully, synthesize key facts, key players, gaps, and hidden connections. Cite with `[[wikilinks]]`.
   - **Connections** ("what's related to X", "connections from X") → find the starting note, trace direct links, shared tags (2+), shared domain. Present layered from strongest to weakest. Identify missing links.
3. **Offer next steps** — deeper reads, missing links to add, topics worth capturing.
