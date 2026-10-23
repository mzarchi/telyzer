use anyhow::Result;
use telyzer_core::{Paths, TelyzerClient};

pub async fn run(paths: &Paths) -> Result<()> {
    let client = TelyzerClient::new(paths).await?;

    if !client.is_authorized().await? {
        println!("Not logged in.");
        return Ok(());
    }

    println!("Logging out...");
    client.sign_out().await?;

    drop(client);

    let session_file = paths.session_file();
    if session_file.exists() {
        let _ = std::fs::remove_file(session_file);
    }

    println!("Logged out successfully.");
    Ok(())
}
