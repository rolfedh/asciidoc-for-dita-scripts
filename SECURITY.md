# Security Policy

## Supported Versions

We actively support the following versions of asciidoc-dita-toolkit:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability in asciidoc-dita-toolkit, please report it responsibly:

### Private Disclosure
- **Email**: [security@example.com] (replace with actual contact)
- **Subject**: [SECURITY] asciidoc-dita-toolkit vulnerability report

### What to Include
- Description of the vulnerability
- Steps to reproduce the issue
- Potential impact assessment
- Suggested fix (if available)

### Response Timeline
- **Initial Response**: Within 48 hours
- **Status Update**: Within 7 days
- **Fix Timeline**: Security issues are prioritized and typically resolved within 30 days

### Disclosure Policy
- We request 90 days to address the issue before public disclosure
- We will acknowledge your contribution in the security advisory
- Critical vulnerabilities may be disclosed sooner with coordinated disclosure

## Security Considerations

### File Processing
- The toolkit processes text files and does not execute user code
- All file operations are limited to `.adoc` files in specified directories
- No network operations or external command execution

### Plugin Security
- Plugins run with the same permissions as the user
- Custom plugins should be reviewed before use
- Only install plugins from trusted sources

### Dependencies
- Runtime: Zero external dependencies (uses only Python standard library)
- Development: Dependencies are pinned and regularly updated

For general security best practices when using this toolkit, see our [documentation](README.md#troubleshooting).
