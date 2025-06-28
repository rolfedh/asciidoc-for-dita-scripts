# Security Policy

## Supported Versions

We currently support the following versions with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability within this project, please send an email to the maintainers. Please do not use the public issue tracker for security vulnerabilities.

### What to include

- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Any suggested fixes

### Response Time

We aim to respond to security reports within 48 hours and provide a fix within 7 days for critical vulnerabilities.

## Security Considerations

This toolkit processes user-provided AsciiDoc files and should be used with appropriate caution:

- Always run the toolkit in a sandboxed environment when processing untrusted files
- Be aware that file processing could potentially consume significant disk space or memory
- The toolkit modifies files in-place - always use version control or backups

## Dependencies

This project currently has no runtime dependencies, which reduces the attack surface. Development dependencies are regularly updated to address known vulnerabilities.
