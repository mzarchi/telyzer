# Contributing to Telyzer

Thank you for your interest in contributing to **Telyzer**! Contributions of all kinds are welcome, including bug fixes, feature proposals, code improvements, documentation, and testing.

Telyzer is an open-source Telegram analysis project written in Rust. It is currently under active development, and contributions should help keep the codebase modular, maintainable, secure, and easy to extend.

## Table of Contents

- [Getting Started](#getting-started)
- [Project Structure](#project-structure)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Code Style](#code-style)
- [Testing and Validation](#testing-and-validation)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)
- [Reporting Bugs](#reporting-bugs)
- [Security and Privacy](#security-and-privacy)

## Getting Started

Before contributing, please:

1. Read the [README](README.md) to understand the project's goals and current status.
2. Check existing [issues](https://github.com/mzarchi/telyzer/issues) and pull requests to avoid duplicate work.
3. For significant changes, open an issue first to discuss the proposed solution.
4. Keep in mind that Telyzer is still evolving. Some features may be incomplete or subject to architectural changes.

## Project Structure

Telyzer is organized as a Cargo workspace with three main packages:

- **`core/`** — Shared application logic, configuration, authentication, client integration, and error handling.
- **`cli/`** — Command-line interface and application commands.
- **`gui/`** — Graphical user interface prototype built with Iced.

When contributing, place new functionality in the appropriate package. Shared functionality should generally belong in `core/` rather than being duplicated across the CLI and GUI.

Avoid unnecessary architectural changes or introducing additional dependencies without a clear reason.

## Development Setup

### Prerequisites

- [Git](https://git-scm.com/)
- [Rust and Cargo](https://www.rust-lang.org/tools/install)
- A compatible Rust toolchain for the project's declared minimum Rust version.

### Clone the repository

```bash
git clone https://github.com/mzarchi/telyzer.git
cd telyzer
```

### Build the workspace

```bash
cargo build --workspace
```

### Run the CLI

```bash
cargo run -p telyzer-cli
```

### Run the GUI

```bash
cargo run -p telyzer-gui
```

Some features may require additional configuration or may not yet be fully implemented.

## Making Changes

For each contribution, create a dedicated branch:

```bash
git checkout -b feature/your-feature-name
```

Use a descriptive branch name that reflects the purpose of your change. For example:

- `feature/channel-analysis`
- `fix/session-handling`
- `docs/setup-guide`
- `refactor/error-handling`

Keep changes focused and avoid combining unrelated fixes or features in a single pull request.

### General Guidelines

- Follow the existing project architecture and naming conventions.
- Prefer clear, maintainable, and idiomatic Rust code.
- Reuse existing functionality where appropriate.
- Handle errors explicitly and provide useful error messages.
- Avoid unnecessary dependencies.
- Update documentation when behavior, configuration, or usage changes.
- Do not commit generated build artifacts or local configuration files containing secrets.

## Code Style

Telyzer uses `rustfmt` for formatting and Clippy for static analysis.

Format your changes before submitting:

```bash
cargo fmt --all
```

Check for common Rust issues:

```bash
cargo clippy --workspace --all-targets
```

Please follow the repository's existing `rustfmt.toml` and `clippy.toml` configurations.

Avoid unrelated formatting changes that make code reviews harder.

## Testing and Validation

Before opening a pull request, build and validate your changes:

```bash
cargo fmt --all -- --check
cargo check --workspace
cargo test --workspace
cargo clippy --workspace --all-targets
```

If you introduce new functionality, add appropriate tests whenever practical.

If a feature cannot be tested automatically, document the manual verification steps and any limitations.

Do not claim that a feature has been tested unless you have actually verified it.

## Commit Guidelines

Write clear, concise commit messages that describe the change.

Recommended format:

```text
<type>: <short description>
```

Examples:

```text
feat: add Telegram session management
fix: handle authentication errors
refactor: simplify configuration loading
docs: update development instructions
test: add configuration validation tests
chore: update dependencies
```

Keep each commit focused on a logical change.

## Pull Request Process

1. Fork the repository and create a feature branch.
2. Implement your changes and update relevant documentation.
3. Run the applicable formatting, build, and test commands.
4. Commit your changes with descriptive messages.
5. Push your branch to your fork.
6. Open a pull request against the `main` branch of the original repository.

Each pull request should include:

- **Summary:** What changed?
- **Motivation:** Why is the change needed?
- **Implementation:** How does it work?
- **Testing:** What commands or manual checks were performed?
- **Additional context:** Screenshots, logs, or related issues, when relevant.

Keep pull requests focused and reasonably sized. Be prepared to discuss feedback and make revisions.

Contributions may require review before they can be merged.

## Reporting Bugs

If you encounter a bug, please open an issue:

[Report a bug or request a feature](https://github.com/mzarchi/telyzer/issues/new)

Include as much relevant information as possible:

- A clear description of the problem.
- Steps to reproduce the issue.
- Expected and actual behavior.
- Your operating system and Rust toolchain version.
- Relevant error messages or logs.

Before sharing logs, remove API credentials, session data, personal information, and other sensitive content.

## Security and Privacy

Telyzer interacts with Telegram and may handle authentication credentials, session files, messages, and other private data.

Contributors must follow these rules:

- Never commit Telegram session files, API credentials, authentication codes, or passwords.
- Never include real credentials in examples, tests, screenshots, or logs.
- Use mock data or synthetic test data whenever possible.
- Do not expose private messages or user information without proper authorization.
- Treat authentication and session-management changes with particular care.

If you discover a security vulnerability, avoid publishing sensitive exploit details in a public issue. Report it privately to the repository maintainer.

## Questions and Discussions

For questions, feature discussions, or architectural proposals, use the repository's [GitHub Issues](https://github.com/mzarchi/telyzer/issues).

Please be respectful, constructive, and open to feedback.

Thank you for helping improve Telyzer!

---

**Repository:** [mzarchi/telyzer](https://github.com/mzarchi/telyzer)

**License:** [MIT License](LICENCE)
