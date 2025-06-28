#!/usr/bin/env python3
"""
Generate HTML from Vale rules tables in README.md

This script extracts tables from a README.md file containing Vale rules
and generates an HTML file with those tables.
"""
import re
import os
import sys
import html
import argparse


def slugify(text):
    """Convert text to a URL-friendly slug."""
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def extract_tables(md_text):
    """
    Extract tables from the markdown text under '## Available rules' section.
    Returns a list of (severity, entries) tuples.
    """
    rules_section = re.split(r"^## Available rules", md_text, flags=re.MULTILINE)[-1]
    pattern = re.compile(
        r"### (Errors|Warnings|Suggestions)\n(?:.*?\n)*?(\| Vale Rule \| Explanation \|(?:\n\|.*)+)", 
        re.MULTILINE
    )
    tables = []
    
    for match in pattern.finditer(rules_section):
        severity = match.group(1)
        table_md = match.group(2)
        
        # Parse table rows
        rows = [r.strip() for r in table_md.strip().split("\n") if r.strip().startswith("|")]
        
        # Remove header and separator
        if len(rows) >= 2:
            rows = rows[2:]
        
        entries = []
        for row in rows:
            cols = [c.strip() for c in row.strip("|").split("|")]
            if len(cols) == 2:
                rule, explanation = cols
                entries.append((rule, explanation))
        
        tables.append((severity, entries))
    
    return tables


def generate_html(tables):
    """Generate HTML from the extracted tables."""
    html_parts = [
        "<html>",
        "<head><meta charset='utf-8'><title>AsciiDocDITA Vale Rules</title></head>",
        "<body>",
        "<h1>AsciiDocDITA Vale Rules</h1>"
    ]
    
    for severity, entries in tables:
        html_parts.append(f"<h2>{html.escape(severity)}</h2>")
        html_parts.append("<table border='1' cellspacing='0' cellpadding='4'>")
        html_parts.append("<tr><th>Vale Rule</th><th>Explanation</th></tr>")
        
        for rule, explanation in entries:
            rule_id = slugify(rule)
            html_parts.append(
                f"<tr id='{rule_id}'><td>{html.escape(rule)}</td><td>{html.escape(explanation)}</td></tr>"
            )
        
        html_parts.append("</table>")
    
    html_parts.append("</body></html>")
    return "\n".join(html_parts)


def main():
    """Main function with argument parsing."""
    parser = argparse.ArgumentParser(description="Generate HTML from Vale rules in README.md")
    parser.add_argument("readme_path", help="Path to the README.md file")
    parser.add_argument("-o", "--output", help="Output HTML file path", 
                       default=os.path.join(os.path.dirname(__file__), "rules.html"))
    
    args = parser.parse_args()
    
    try:
        with open(args.readme_path, encoding="utf-8") as f:
            md_text = f.read()
    except FileNotFoundError:
        print(f"Error: README file not found: {args.readme_path}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading README file: {e}", file=sys.stderr)
        sys.exit(1)
    
    tables = extract_tables(md_text)
    if not tables:
        print("Warning: No tables found in the README file", file=sys.stderr)
    
    html_text = generate_html(tables)
    
    try:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(html_text)
        print(f"HTML file generated at {args.output}")
    except Exception as e:
        print(f"Error writing HTML file: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
