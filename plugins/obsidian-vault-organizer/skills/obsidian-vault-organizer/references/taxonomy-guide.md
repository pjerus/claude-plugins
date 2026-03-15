# Taxonomy Guide

This document explains the reasoning behind the TechVault taxonomy so the organizer can make good classification decisions.

## Type selection logic

The `type` field answers: "What kind of document is this?"

| If the note is about... | Use type |
|---|---|
| A specific company or organization | `company` |
| A developer tool, library, framework, or SaaS product | `tool` |
| A concept, paradigm, or technical explanation | `technology` |
| The user's own project (code they wrote/maintain) | `project` |
| A specific person | `person` |
| An academic paper or preprint | `paper` |
| A how-to guide, video walkthrough, or tutorial | `tutorial` |
| Setup guides, cheat sheets, reference material | `resource` |
| Industry research, market analysis, supply chain notes | `research` |
| Daily notes, scratch notes, meeting notes | `note` |
| A startup idea or project brainstorm | `idea` |
| A conference or meetup | `event` |

### Ambiguous cases

- **Company vs Tool**: If the note is primarily about the company (HQ, CEO, funding, strategy), it's a `company`. If it's about the product and how to use it (API docs, features, setup), it's a `tool`. Some notes cover both — go with whichever is the primary focus.
- **Technology vs Tool**: A `technology` is a concept (e.g., "Knowledge Graphs", "Vector Search"). A `tool` is a specific product that implements the concept (e.g., "Neo4j", "Elasticsearch").
- **Note vs everything else**: `note` is the catch-all. Only use it when nothing more specific fits.

## Domain selection logic

The `domain` field answers: "What broad subject area does this touch?"

Pick 1-3 domains. Most notes have 1-2. If something touches AI and web development, give it both.

The domains are meant to be broad enough that you could filter your vault to "show me everything about AI" or "show me everything about petrochemical research" and get a useful view.

## Tag selection logic

Tags are the most specific level. They answer: "What specific topics does this cover?"

Rules of thumb:
- 2-5 tags per note is typical
- Use tags from the taxonomy. Don't invent new ones without flagging it.
- Tags should be useful for finding the note later. Ask: "If I were searching for this note, what would I type?"
- Company/product names can be tags when another note references that company's technology (e.g., a note about knowledge graphs might get `neo4j` as a tag if it discusses Neo4j specifically)

## Wikilink logic

Related notes should link to each other. Good link candidates:
- A company and the technologies it implements
- Tools in the same category (all hosting platforms should link to each other)
- A person and their projects/writings
- Research notes about the same supply chain or industry
- A technology concept and the tools that implement it

Links go in a `## Related` section at the bottom. Format: `- [[Note Name]]`
