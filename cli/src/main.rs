mod commands;
mod menu;

use clap::{Parser, Subcommand};
use telyzer_core::{Paths, TelyzerClient};

#[derive(Parser)]
#[command(name = "telyzer")]
#[command(version, about = "Telegram analyzer for experienced users")]
struct Cli {
    #[command(subcommand)]
    command: Option<Commands>,
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
            tracing_subscriber::EnvFilter::try_from_default_env().unwrap_or_else(|_| "info".into()),
        )
        .init();

    let cli = Cli::parse();
    let paths = Paths::init()?;
    let client = TelyzerClient::new(&paths).await?;

    let result = match cli.command {
        Some(Commands::Login) => commands::login::run(&client).await,
        Some(Commands::Whoami) => commands::whoami::run(&client).await,
        // The menu owns the client and shuts it down itself
        None => return menu::run(&paths, client).await,
    };

    client.shutdown().await;
    result
}
