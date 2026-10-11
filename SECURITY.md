# Security Policy

## Supported Versions

Telyzer is under active development. Security fixes are generally prioritized for the latest version available on the `main` branch.

Older versions may not receive security updates.

## Reporting a Vulnerability

If you discover a potential security vulnerability in Telyzer, please report it responsibly.

**Please do not disclose security vulnerabilities through public GitHub issues or public discussions.**

Instead:

1. Visit the [Telyzer GitHub repository](https://github.com/mzarchi/telyzer).
2. If private vulnerability reporting is available, use the repository's **Security → Report a vulnerability** option.
3. If private reporting is unavailable, contact the repository maintainer privately through their GitHub profile.

When reporting a vulnerability, please include:

- A clear description of the issue.
- The potential security impact.
- The steps required to reproduce it.
- The affected component, version, or commit.
- Any proof of concept that helps demonstrate the issue, without exposing real user data or credentials.

You may redact sensitive information from your report.

## Response Process

After receiving a report, the maintainer will make reasonable efforts to:

- Review and assess the reported vulnerability.
- Request additional information if necessary.
- Determine the affected components and severity.
- Develop and release a fix when appropriate.
- Communicate relevant remediation guidance.

Response and remediation timelines may vary depending on the severity and complexity of the issue.

## Scope

Security reports related to the following areas are especially relevant:

- Telegram authentication and session management.
- Handling of API credentials, secrets, and configuration.
- Exposure of private messages or exported user data.
- Insecure file handling and data storage.
- Dependency vulnerabilities.
- Command execution or other security issues affecting the CLI, GUI, or core components.

## Protecting Credentials and User Data

Telyzer interacts with Telegram accounts and may process private messages and other sensitive information.

Please follow these precautions when developing, testing, or reporting issues:

- Never commit Telegram API credentials, authentication codes, passwords, session files, or other secrets.
- Never include real authentication sessions or private user data in public issues, pull requests, logs, or test fixtures.
- Use synthetic or anonymized data when reproducing issues.
- Store sensitive configuration locally and keep it out of version control.
- Review changes involving authentication, serialization, logging, and data export carefully.

## Dependency Security

Contributors should avoid introducing unnecessary dependencies and should consider the security implications of new or updated crates.

Security-related dependency updates should be reviewed and tested before being merged.

## Responsible Disclosure

Please allow the maintainer a reasonable opportunity to investigate and address a vulnerability before disclosing technical details publicly.

This policy does not guarantee a particular response time or security support for older releases.

Thank you for helping keep Telyzer and its users safe.
