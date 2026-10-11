mod commands;

use clap::{Parser, Subcommand};
use telyzer_core::Paths;

#[derive(Parser)]
#[command(name = "telyzer")]
#[command(version, about = "Telegram analyzer for power users")]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    Login,
    Whoami,
}

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    tracing_subscriber::fmt()
        .with_env_filter(
            tracing_subscriber::EnvFilter::try_from_default_env()
                .unwrap_or_else(|_| "info".into()),
        )
        .init();

    let cli = Cli::parse();
    let paths = Paths::init()?;

    match cli.command {
        Commands::Login => commands::login::run(&paths).await?,
        Commands::Whoami => commands::whoami::run(&paths).await?,
    }

    Ok(())
}