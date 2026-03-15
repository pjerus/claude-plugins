# Obsidian Vault Organizer

Organize your Obsidian vault with structured taxonomy, smart tagging, and bidirectional wikilinks.

## Commands

| Command | Description |
|---------|-------------|
| `/vault-note` | Add content (text, URL, file) as a classified vault note |
| `/vault-daily` | Append a quick note to today's daily note |
| `/vault-audit` | Scan and fix tagging/linking issues across the vault |
| `/vault-find` | Search notes by tag, domain, or keyword |
| `/vault-brief` | Get a synthesized briefing on a domain or topic |
| `/vault-related` | Explore connections from a specific note |

## How it works

The plugin uses a `Tag-Taxonomy.md` file in your vault as the canonical reference for types, domains, and tags. All classification is checked against this taxonomy — new tags are surfaced for your approval before being added.

Every write operation (new notes, tag fixes, link additions) is followed by a git commit and push to keep your vault synced.

## Setup

1. Your Obsidian vault needs a `Tag-Taxonomy.md` file defining your taxonomy. If you don't have one, use `/vault-audit` and the plugin will offer to create one.
2. Git should be initialized in your vault for auto-commit/push to work.
3. For git push, you'll need GitHub auth configured on your machine (`gh auth login`).

## Skills

The plugin includes the **obsidian-vault-organizer** skill, which also triggers automatically when you mention Obsidian, vault, notes, tags, or wikilinks in conversation — no slash command needed.

## Scripts

- `scan_vault.py` — Python scanner that reports missing frontmatter, empty Related sections, unknown tags, standalone hashtags, and other vault health issues.
