# Security Policy

## Supported Versions

We provide security updates for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability in the AsciiDoc DITA Toolkit, please report it responsibly:

1. **Do not** create a public GitHub issue for security vulnerabilities
2. Send an email to the maintainers with details of the vulnerability
3. Include steps to reproduce the issue if possible
4. We will acknowledge receipt within 48 hours
5. We will provide a fix or mitigation within 30 days for confirmed vulnerabilities

## Security Considerations

This toolkit processes AsciiDoc files and modifies them in place. Please be aware of the following security considerations:

### File Processing
- The toolkit modifies files in place without creating backups by default
- Always use version control when processing important files
- Be cautious when processing files from untrusted sources

### Input Validation
- The toolkit validates file extensions (.adoc) but processes file contents directly
- Malformed input files could potentially cause unexpected behavior
- Always validate input files from untrusted sources

### Directory Traversal
- The toolkit respects symlinks and will skip them by design
- Recursive processing is limited to the specified directory tree
- No arbitrary file system access outside the specified directories

### Dependencies
- This toolkit uses only Python standard library modules
- No external dependencies reduce the attack surface
- Regular updates to Python itself are recommended

## Best Practices

When using this toolkit:

1. **Use version control** - Always commit your files before running the toolkit
2. **Test first** - Run on test files before processing production content
3. **Validate input** - Ensure input files are from trusted sources
4. **Monitor changes** - Review the changes made by the toolkit before committing
5. **Keep updated** - Use the latest version of the toolkit and Python

## Scope

This security policy covers:
- The asciidoc-dita-toolkit Python package
- CLI tools and plugins
- File processing and modification functionality

This policy does not cover:
- Third-party dependencies (there are none)
- User-generated content or configurations
- Operating system or Python interpreter vulnerabilities
