# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability in IceBreaker, please report it responsibly:

1. **DO NOT** create a public GitHub issue
2. Email security@icebreaker.dev with:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

We will respond within 48 hours and work with you to address the issue promptly.

## Security Best Practices

When using IceBreaker:

- Never commit API keys to version control
- Use environment variables or `.env` files (which are gitignored by default)
- Rotate API keys regularly
- Use the principle of least privilege for API keys
- Monitor API usage for unexpected activity

## API Key Security

IceBreaker never:
- Stores your API keys
- Transmits keys to any server other than your configured AI provider
- Logs API keys

API keys are only used in-memory during the execution of commands.
