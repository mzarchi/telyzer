use anyhow::Result;
use telyzer_core::{Paths, TelyzerClient};

#[tokio::main]
async fn main() -> Result<()> {
    let paths = Paths::init()?;
    println!("Data dir: {}", paths.data_dir().display());

    let client = TelyzerClient::new(&paths).await?;
    println!("Connected to Telegram!");

    let authorized = client.is_authorized().await?;
    println!("Authorized: {}", authorized);

    Ok(())
}