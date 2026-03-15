---
name: obsidian-vault-organizer
description: >
  Obsidian vault assistant — add notes, search, get briefings, audit tags, explore connections.
  WRITE: "add this to my vault", "save this as a note", "file this", "tag this", quick thoughts for daily notes.
  READ: "what do I have on X", "find notes about", "brief me on", "what's related to", "summarize my notes on".
  AUDIT: "clean up my vault", "fix my tags", "what's untagged", "audit my notes".
  Triggers on mentions of Obsidian, vault, notes, tags, or wikilinks.
version: 1.0.0
---

# Obsidian Vault Organizer

You manage the user's Obsidian vault — adding well-classified notes, searching and synthesizing existing knowledge, and keeping metadata clean.

---

## Vault Discovery

**Every command starts here.** Resolve the vault path before doing anything else.

### Step 1: Check for cached config

```bash
cat ${CLAUDE_PLUGIN_ROOT}/vault-config.json 2>/dev/null
```

If the file exists and contains a valid `vault_path` that points to a directory with `.obsidian/` inside it, use that path. Skip to the command logic.

### Step 2: Auto-detect (if no cache or invalid)

```bash
find ~ -maxdepth 4 -type d -name ".obsidian" 2>/dev/null
```

Each result's parent directory is a vault. If exactly one vault is found, use it. If multiple, list them and ask the user to pick.

### Step 3: Cache the result

Write the chosen path to `${CLAUDE_PLUGIN_ROOT}/vault-config.json`:

```json
{
  "vault_path": "/Users/pat/Obsidian_Vault/TechVault"
}
```

### Re-detection

If the user says "change vault", "different vault", "switch vault", or passes `--redetect`, delete `vault-config.json` and re-run auto-detect from Step 2.

---

## Sync Strategy

After resolving the vault path, check if it's a git repo:

```bash
git -C <vault-path> rev-parse --is-inside-work-tree 2>/dev/null
```

**Default behavior: no git operations.** Just write files. The user likely uses Obsidian Sync or manages git themselves.

Only run `git add`, `git commit`, or `git push` if the user **explicitly asks** (e.g., "commit that", "push my changes").

---

## Reading the Taxonomy

Before any write operation, read `Tag-Taxonomy.md` from the vault root:

```bash
cat <vault-path>/Tag-Taxonomy.md
```

This gives you the current:
- **`type`** values and what each is for
- **`domain`** values and their coverage areas
- **`tags`** vocabulary grouped by subject
- **Naming rules** (lowercase, hyphenated, no duplicates)

Also read `${CLAUDE_PLUGIN_ROOT}/skills/obsidian-vault-organizer/references/taxonomy-guide.md` for classification decision logic — how to pick between company vs tool, technology vs tool, etc.

**The taxonomy is the authority.** Never silently use tags, types, or domains that aren't in it. If a concept needs a new tag, flag it explicitly and ask.

---

## Writing: Adding Content to the Vault

The `/vault-write` command routes here. Determine what the user gave you and how to handle it.

### Routing: Daily Note vs Full Note

**Daily note** (append to today's `YYYY-MM-DD.md`):
- Short thoughts, reminders, 1-2 sentences
- Quick verbal notes ("I just learned that...", "reminder to...")
- No clear type/domain classification needed

**Full classified note** (create a new file):
- Substantial content — paragraphs, articles, detailed descriptions
- URLs to fetch and capture
- Files to read and organize
- Content with a clear type (company, tool, technology, etc.)

When ambiguous, ask: "This could go as a quick daily entry or a full note — which do you prefer?"

### Daily Note Flow

1. Get today's date.
2. Find or create `<vault-path>/YYYY-MM-DD.md`. If creating, use this template:
   ```markdown
   ---
   type: note
   domain: []
   tags: []
   created: YYYY-MM-DD
   ---

   # YYYY-MM-DD

   ## Quick Notes

   ## Captures
   ```
3. Identify relevant `[[wikilinks]]` to existing vault notes — search for matching note filenames.
4. Route by length:
   - **One-liner** → bullet under `## Quick Notes` with inline wikilinks
   - **Paragraph+** → own heading under `## Captures` with wikilinks woven in
5. **Show the user what you'll append. Wait for approval.**
6. Write on approval.
7. Render the daily note with `glow <vault-path>/YYYY-MM-DD.md` and offer the Obsidian link.

### Full Note Flow

#### 1. Parse the input

- **Pasted text** → work with it directly
- **URL** → fetch with WebFetch, extract key information
- **File path** → read it
- **Topic to research** (no content provided, just a subject like "Pinecone" or "vector databases") → invoke the `research` skill to gather information, then use its output as the content to classify
- **Verbal description** → use as-is

#### 2. Classify

Use the taxonomy to determine:
- **`type`** (exactly one) — use the rules-based signals:

  | Signal | Likely type |
  |--------|-------------|
  | Specific company or org | company |
  | Developer tool, library, SaaS product | tool |
  | Concept or paradigm explanation | technology |
  | Academic paper or preprint | paper |
  | Tutorial or how-to | tutorial |
  | Industry/market research | research |
  | About a person | person |
  | Project idea or brainstorm | idea |

- **`domain`** (1-3 from taxonomy's domain table)
- **`tags`** (2-5 from taxonomy's tag lists)

**Check for splits.** If the content covers multiple distinct things (e.g., a company AND its product), and there's enough substance for separate notes, offer to split.

**Check every tag against the taxonomy.** If a concept isn't covered by existing tags, flag it and suggest a new tag. Don't silently invent tags.

#### 3. Present classification and wait

Show: proposed type, domains, tags, folder, filename. Wait for the user to confirm or adjust.

#### 4. Draft the note

```markdown
---
type: <type>
domain: [<domains>]
tags: [<tags>]
created: YYYY-MM-DD
---

# <Title>

<Body content — preserve the original content's substance, organize clearly>

## Related

- [[Existing Note 1]]
- [[Existing Note 2]]
```

For the Related section, search the vault for notes that share tags or domains. Only link to notes that actually exist — verify filenames with:

```bash
rg -l "<note name>" <vault-path> --glob "*.md"
```

**Show the full draft. Wait for approval.**

#### 5. Write and present

- Determine the correct folder by looking at where existing notes of this type live
- Write the file
- If new tags were approved, update `Tag-Taxonomy.md`
- Render the written note with `glow`:
  ```bash
  glow <vault-path>/<note-file>.md
  ```
- Offer an Obsidian link to open the note directly:
  ```
  Open in Obsidian: obsidian://open?vault=<vault-name>&file=<url-encoded-relative-path>
  ```
  The vault name is the directory name containing `.obsidian/`. The file path is relative to the vault root, URL-encoded (spaces → `%20`).

---

## Reading: Search, Briefings, and Connections

The `/vault-read` command routes here. Determine intent from the query.

### Search (default mode)

Triggered by: keywords, tag names, "find X", "what do I have on X"

1. Search vault markdown files using `rg`:
   ```bash
   rg -li "<query>" <vault-path> --glob "*.md"
   ```
2. For tag/domain searches, also check frontmatter:
   ```bash
   rg -l "tags:.*<query>" <vault-path> --glob "*.md"
   rg -l "domain:.*<query>" <vault-path> --glob "*.md"
   ```
3. Read each matching file. Present results with:
   - Note name
   - Type and domains
   - One-sentence summary of what the note covers
4. Group by type or domain if many results.
5. Offer to go deeper on any specific note.

### Briefing

Triggered by: "brief me on X", "summarize my notes on X", "what do I know about X"

1. Find all relevant notes (same search as above).
2. **Read every matching note fully.**
3. Synthesize — don't just summarize each note sequentially. Cover:
   - **Key facts and insights** across notes
   - **Key players** — companies, tools, people that appear in multiple notes
   - **Gaps** — obvious missing topics, broken references
   - **Hidden connections** — notes that should link to each other but don't
4. Cite specific notes with `[[wikilinks]]`.
5. Suggest next steps: missing links, new notes worth creating, tags to add.

### Connections

Triggered by: "what's related to X", "connections from X", "what links to X"

1. Locate the starting note. If ambiguous, show options and ask.
2. Read the starting note. Extract its tags, domains, and wikilinks.
3. Map connections in three layers:
   - **Direct links** — notes in its `## Related` section + backlinks (notes that `[[link]]` to it)
   - **Shared tags** — notes sharing 2+ tags (topically related even if not linked)
   - **Shared domain** — same-domain notes not yet connected
4. Read each connected note for a one-sentence description.
5. Present layered from strongest to weakest.
6. Identify **missing links** — notes that should be connected but aren't.
7. Offer to add missing wikilinks.

---

## Auditing: Scan and Fix

The `/vault-audit` command routes here.

1. Run the scanner:
   ```bash
   python3 ${CLAUDE_PLUGIN_ROOT}/skills/obsidian-vault-organizer/scripts/scan_vault.py <vault-path>
   ```
2. Parse the JSON output. Summarize issues by category:
   - **Missing frontmatter** → classify the file and add YAML
   - **Missing type/domain/tags** → propose values
   - **Unknown tags/types/domains** → identify typos vs legitimate additions
   - **Standalone hashtags** → convert to frontmatter tags
   - **Empty Related sections** → find and suggest related notes
3. Present all proposed fixes. Wait for approval.
4. Apply approved fixes.
5. Re-run the scanner to verify fixes landed correctly.
6. Report results.

---

## Key Principles

- **Vault discovery first.** Every command resolves the vault path before doing anything.
- **The taxonomy is the authority.** Don't silently add tags that aren't in it.
- **Always preview, always wait.** Never write to the vault without showing the user first.
- **No surprise git operations.** Only commit/push when explicitly asked.
- **Use `rg` for search.** It's fast and available.
- **Preserve content.** Never modify body text when adding metadata.
- **Link to real notes.** Verify notes exist before adding `[[wikilinks]]`.
- **Match existing style.** Follow the folder structure and naming patterns already in the vault.
