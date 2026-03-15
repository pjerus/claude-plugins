#!/usr/bin/env python3
"""
Scan an Obsidian vault and report tagging/linking issues.

Usage: python3 scan_vault.py <vault-path> [--taxonomy <path-to-Tag-Taxonomy.md>]

Output: JSON report to stdout + vault_scan.json in parent of vault path.
"""

import os
import sys
import re
import json
import argparse
from pathlib import Path
from datetime import datetime

SKIP_DIRS = {'.git', '.obsidian', 'Templates', '.trash'}

def parse_frontmatter(content):
    """Extract YAML frontmatter as a dict. Returns (dict, rest_of_content) or (None, content)."""
    if not content.startswith('---'):
        return None, content
    end = content.find('---', 3)
    if end == -1:
        return None, content
    fm_text = content[3:end].strip()
    # Simple YAML parsing for our flat structure
    meta = {}
    for line in fm_text.split('\n'):
        line = line.strip()
        if ':' not in line:
            continue
        key, val = line.split(':', 1)
        key = key.strip()
        val = val.strip()
        # Parse arrays like [a, b, c] or ["a", "b"]
        if val.startswith('[') and val.endswith(']'):
            items = val[1:-1]
            meta[key] = [item.strip().strip('"').strip("'") for item in items.split(',') if item.strip()]
        else:
            meta[key] = val.strip('"').strip("'")
    return meta, content[end+3:].strip()

def extract_taxonomy_tags(taxonomy_path):
    """Read Tag-Taxonomy.md and extract all known tags, types, and domains."""
    known = {'types': set(), 'domains': set(), 'tags': set()}
    if not taxonomy_path or not os.path.exists(taxonomy_path):
        return known

    content = open(taxonomy_path).read()

    # Extract types from table rows: | type | description |
    # Match any row in the type table (after "Document Type" header)
    type_match = re.search(r'## `type`.*?\n\n\|.*?\n\|[-| ]+\n(.*?)(?:\n---|\n\n##)', content, re.DOTALL)
    if type_match:
        for row in type_match.group(1).strip().split('\n'):
            m = re.match(r'\|\s*(\w[\w-]*)\s*\|', row)
            if m:
                known['types'].add(m.group(1))

    # Extract domains from table rows
    domain_match = re.search(r'## `domain`.*?\n\n\|.*?\n\|[-| ]+\n(.*?)(?:\n---|\n\n##)', content, re.DOTALL)
    if domain_match:
        for row in domain_match.group(1).strip().split('\n'):
            m = re.match(r'\|\s*(\w[\w-]*)\s*\|', row)
            if m:
                known['domains'].add(m.group(1))

    # Extract tags from the specific topic tag lists (comma-separated lines under ### headers)
    tags_section = re.search(r'## `tags`.*?(?=\n## [^`]|\n---\n\n## Naming)', content, re.DOTALL)
    if tags_section:
        tag_text = tags_section.group(0)
        # Find comma-separated tag lists: lines with 2+ comma-separated words
        tag_lines = re.findall(r'^([\w][\w-]*(?:,\s*[\w][\w-]*)+)', tag_text, re.MULTILINE)
        for line in tag_lines:
            for tag in line.split(','):
                tag = tag.strip()
                if tag and len(tag) > 0:
                    known['tags'].add(tag)

    return known

def find_standalone_hashtags(content, body_only=True):
    """Find lines that are only hashtags (not headings, not in code blocks)."""
    lines = content.split('\n')
    hashtag_lines = []
    in_code_block = False
    in_frontmatter = False

    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped == '---':
            if i == 0:
                in_frontmatter = True
                continue
            elif in_frontmatter:
                in_frontmatter = False
                continue
        if in_frontmatter:
            continue
        if stripped.startswith('```'):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue
        # Check if line is only hashtags
        if stripped and re.match(r'^(#[a-zA-Z][a-zA-Z0-9_/-]*)(\s+#[a-zA-Z][a-zA-Z0-9_/-]*)*$', stripped):
            hashtag_lines.append({'line': i + 1, 'content': stripped})

    return hashtag_lines

def find_wikilinks(content):
    """Extract all [[wikilinks]] from content."""
    return re.findall(r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]', content)

def has_related_section(content):
    """Check if file has a ## Related section and whether it's populated."""
    if '## Related' not in content:
        return 'missing'
    # Find content after ## Related
    match = re.search(r'## Related\n(.*?)(?=\n## |\Z)', content, re.DOTALL)
    if match:
        related_content = match.group(1).strip()
        if not related_content or related_content == '-':
            return 'empty'
        if '[[' in related_content:
            return 'populated'
        return 'empty'
    return 'empty'

def scan_vault(vault_path, taxonomy_path=None):
    """Scan the vault and return a report."""
    vault = Path(vault_path)

    # Auto-find taxonomy
    if not taxonomy_path:
        tax_file = vault / 'Tag-Taxonomy.md'
        if tax_file.exists():
            taxonomy_path = str(tax_file)

    known = extract_taxonomy_tags(taxonomy_path)

    report = {
        'vault_path': str(vault),
        'scan_date': datetime.now().isoformat(),
        'total_files': 0,
        'issues': {
            'no_frontmatter': [],
            'missing_type': [],
            'missing_domain': [],
            'missing_tags': [],
            'standalone_hashtags': [],
            'no_related_section': [],
            'empty_related_section': [],
            'unknown_tags': [],
            'unknown_types': [],
            'unknown_domains': [],
        },
        'stats': {
            'by_type': {},
            'by_domain': {},
            'tag_frequency': {},
            'files_with_frontmatter': 0,
            'files_with_wikilinks': 0,
            'files_with_related': 0,
        },
        'all_tags_used': [],
        'files': []
    }

    for root, dirs, files in os.walk(vault):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]

        for fname in sorted(files):
            if not fname.endswith('.md'):
                continue

            fpath = os.path.join(root, fname)
            relpath = os.path.relpath(fpath, vault)

            # Skip taxonomy itself
            if fname == 'Tag-Taxonomy.md':
                continue

            # Skip templates
            if 'Templates' in relpath.split(os.sep):
                continue

            report['total_files'] += 1
            content = open(fpath).read()
            meta, body = parse_frontmatter(content)

            file_info = {
                'path': relpath,
                'has_frontmatter': meta is not None,
                'type': None,
                'domain': [],
                'tags': [],
                'wikilinks': find_wikilinks(content),
                'related_status': has_related_section(content),
                'issues': []
            }

            # Check frontmatter
            if meta is None:
                report['issues']['no_frontmatter'].append(relpath)
                file_info['issues'].append('no_frontmatter')
            else:
                report['stats']['files_with_frontmatter'] += 1

                if 'type' not in meta:
                    report['issues']['missing_type'].append(relpath)
                    file_info['issues'].append('missing_type')
                else:
                    file_info['type'] = meta['type']
                    t = meta['type']
                    report['stats']['by_type'][t] = report['stats']['by_type'].get(t, 0) + 1
                    if known['types'] and t not in known['types']:
                        report['issues']['unknown_types'].append({'file': relpath, 'type': t})

                if 'domain' not in meta:
                    report['issues']['missing_domain'].append(relpath)
                    file_info['issues'].append('missing_domain')
                else:
                    domains = meta['domain'] if isinstance(meta['domain'], list) else [meta['domain']]
                    file_info['domain'] = domains
                    for d in domains:
                        report['stats']['by_domain'][d] = report['stats']['by_domain'].get(d, 0) + 1
                        if known['domains'] and d not in known['domains']:
                            report['issues']['unknown_domains'].append({'file': relpath, 'domain': d})

                if 'tags' not in meta:
                    report['issues']['missing_tags'].append(relpath)
                    file_info['issues'].append('missing_tags')
                else:
                    tags = meta['tags'] if isinstance(meta['tags'], list) else [meta['tags']]
                    file_info['tags'] = tags
                    for tag in tags:
                        report['stats']['tag_frequency'][tag] = report['stats']['tag_frequency'].get(tag, 0) + 1
                        if known['tags'] and tag not in known['tags']:
                            report['issues']['unknown_tags'].append({'file': relpath, 'tag': tag})

            # Check for standalone hashtags
            hashtags = find_standalone_hashtags(content)
            if hashtags:
                report['issues']['standalone_hashtags'].append({
                    'file': relpath,
                    'lines': hashtags
                })
                file_info['issues'].append('standalone_hashtags')

            # Check wikilinks / related
            if file_info['wikilinks']:
                report['stats']['files_with_wikilinks'] += 1

            if file_info['related_status'] == 'missing':
                report['issues']['no_related_section'].append(relpath)
            elif file_info['related_status'] == 'empty':
                report['issues']['empty_related_section'].append(relpath)
            elif file_info['related_status'] == 'populated':
                report['stats']['files_with_related'] += 1

            report['files'].append(file_info)

    # Sort tag frequency
    report['all_tags_used'] = sorted(report['stats']['tag_frequency'].keys())
    report['stats']['tag_frequency'] = dict(
        sorted(report['stats']['tag_frequency'].items(), key=lambda x: -x[1])
    )

    # Summary
    total_issues = sum(
        len(v) for v in report['issues'].values()
    )
    report['summary'] = {
        'total_files': report['total_files'],
        'total_issues': total_issues,
        'files_with_frontmatter': report['stats']['files_with_frontmatter'],
        'files_with_wikilinks': report['stats']['files_with_wikilinks'],
        'files_with_related': report['stats']['files_with_related'],
        'issue_counts': {k: len(v) for k, v in report['issues'].items() if v}
    }

    return report


def main():
    parser = argparse.ArgumentParser(description='Scan Obsidian vault for tagging issues')
    parser.add_argument('vault_path', help='Path to the Obsidian vault')
    parser.add_argument('--taxonomy', help='Path to Tag-Taxonomy.md (auto-detected if not given)')
    parser.add_argument('--output', help='Output path for JSON report')
    args = parser.parse_args()

    report = scan_vault(args.vault_path, args.taxonomy)

    # Output JSON to stdout for programmatic consumption
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"Report written to {args.output}", file=sys.stderr)
    else:
        json.dump(report, sys.stdout, indent=2)


if __name__ == '__main__':
    main()
