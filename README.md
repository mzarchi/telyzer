 <div align="center">

# ◈ Telyzer

### A Rust-powered foundation for exploring Telegram data.

**A work in progress — built for extensibility, clarity, and control.**

[![Rust](https://img.shields.io/badge/Rust-2021%20Edition-orange?logo=rust&logoColor=white)](https://www.rust-lang.org/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-In%20Development-orange)](https://github.com/mzarchi/telyzer)
[![GitHub](https://img.shields.io/badge/GitHub-mzarchi%2Ftelyzer-181717?logo=github)](https://github.com/mzarchi/telyzer)

[Overview](#overview) · [Architecture](#architecture) · [Getting Started](#getting-started) · [Roadmap](#roadmap)

</div>

---

## Overview

**Telyzer** is an evolving Telegram-focused project written in Rust. It is designed around a modular architecture with a shared core, a command-line interface, and a graphical interface.

Built on the [Grammers](https://github.com/Lonami/grammers) ecosystem, Telyzer lays the groundwork for Telegram client integration and future data analysis capabilities.

> **Note:** Telyzer is currently in early development. Some components are prototypes, and the complete Telegram authentication and analysis workflows are not yet implemented.

## Features & Components

- **Rust-powered:** A modern, compiled foundation with Cargo workspace management.
- **Shared Core:** Common application paths, configuration locations, and error handling.
- **CLI:** A command-line entry point for inspecting application directories.
- **GUI Prototype:** An early login interface built with Iced.
- **Cross-platform paths:** Platform-aware locations for application data and configuration.
- **Telegram integration:** Grammers dependencies prepared for client functionality.
- **Modular architecture:** Separate packages for core logic, CLI, and GUI.

## Architecture

Telyzer is organized as a Cargo workspace:

```text
telyzer/
├── .gitattributes
├── .gitignore
├── Cargo.toml
├── Cargo.lock
├── LICENCE
├── README.md
├── clippy.toml
├── rustfmt.toml
│
├── core/
│   ├── Cargo.toml
│   └── src/
│       ├── auth.rs
│       ├── client.rs
│       ├── config.rs
│       ├── error.rs
│       ├── lib.rs
│       └── secrets.rs.example
│
├── cli/
│   ├── Cargo.toml
│   └── src/
│       ├── main.rs
│       └── commands/
│           ├── mod.rs
│           ├── login.rs
│           └── whoami.rs
│
└── gui/
    ├── Cargo.toml
    └── src/
        ├── app.rs
        ├── constants.rs
        ├── main.rs
        └── ui.rs
```

### Workspace packages

| Package | Responsibility |
|---|---|
| `telyzer-core` | Shared paths and core error types |
| `telyzer-cli` | Command-line entry point |
| `telyzer-gui` | Graphical interface prototype |

## Getting Started

### Prerequisites

- [Rust](https://www.rust-lang.org/tools/install)
- Cargo
- Git

### 1. Clone the repository

```bash
git clone https://github.com/mzarchi/telyzer.git
cd telyzer
```

### 2. Run the CLI

```bash
cargo run -p telyzer-cli
```

The current CLI initializes the application paths and displays the locations used for application data, configuration, and the Telegram session file.

### 3. Build the project

Build all workspace packages:

```bash
cargo build --workspace
```

Run static checks with Clippy:

```bash
cargo clippy --workspace --all-targets
```

## Tech Stack

| Technology | Purpose |
|---|---|
| [Rust](https://www.rust-lang.org/) | Core programming language |
| [Cargo](https://doc.rust-lang.org/cargo/) | Workspace and dependency management |
| [Grammers](https://github.com/Lonami/grammers) | Telegram client libraries |
| [Tokio](https://tokio.rs/) | Asynchronous runtime |
| [Serde](https://serde.rs/) | Serialization framework |
| [Iced](https://iced.rs/) | GUI toolkit |

## Roadmap

Telyzer is actively evolving. Planned development areas include:

- [ ] Complete Telegram authentication and session management
- [ ] Connect the GUI login flow to the Telegram client
- [ ] Implement channel and chat data collection
- [ ] Add message analysis and statistical reporting
- [ ] Introduce structured data export
- [ ] Improve error handling and logging
- [ ] Add automated tests and documentation
- [ ] Prepare release builds and distribution packages

*The roadmap is subject to change as development progresses.*

## Contributing

Contributions, ideas, and bug reports are welcome.

1. Fork the repository.
2. Create a feature branch.
3. Make your changes and test them.
4. Open a pull request with a clear description.

For major changes, consider opening an issue first to discuss the proposed approach.

- **Repository:** [mzarchi/telyzer](https://github.com/mzarchi/telyzer)
- **Issues:** [Report a bug or suggest a feature](https://github.com/mzarchi/telyzer/issues)

## Security & Privacy

Telegram session files may provide access to an account. Keep session files, API credentials, and exported private data secure.

- Never commit session files or API credentials.
- Do not publish private messages or sensitive exports without authorization.
- Use Telegram data responsibly and respect users' privacy.

## License

This project is licensed under the [MIT License](LICENSE).

---

<div align="center">

**Telyzer** · Built by [@mzarchi](https://github.com/mzarchi)
</div>