---
description: Add content to your Obsidian vault — note, daily entry, URL capture, or researched topic
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, Agent, WebFetch, WebSearch, Skill
argument-hint: [content, URL, topic to research, or file path]
---

The user wants to add content to their Obsidian vault. Input: $ARGUMENTS

Follow the obsidian-vault-organizer skill — specifically the **Vault Discovery** section first, then route:

1. **Resolve vault path** using the skill's vault discovery logic.
2. **Read `Tag-Taxonomy.md`** from the vault root for current types, domains, and tags.
3. **Read `${CLAUDE_PLUGIN_ROOT}/skills/obsidian-vault-organizer/references/taxonomy-guide.md`** for classification decision logic.
4. **Route based on input:**
   - **Short/informal** (1-2 sentences, quick thought, reminder) → append to today's daily note (`YYYY-MM-DD.md` in vault root). Add inline `[[wikilinks]]` to existing notes where relevant. Show draft, wait for approval.
   - **URL** → fetch with WebFetch, extract key information, classify as a full note.
   - **Topic to research** (no URL or content provided, just a subject — e.g., "Pinecone", "vector databases") → invoke the `research` skill to gather information first, then classify the output into a vault note.
   - **Substantial content or file** → classify as a full note. Determine type, domain, tags from taxonomy. Show proposed classification + full draft. Wait for approval. Write to the appropriate type folder.
5. **After writing:** no git operations unless the user explicitly asks.
