use anyhow::{Context, Result};
use telyzer_core::{Paths, TelyzerClient};

/// Consumes the client: signs out, stops the connection, then deletes the
/// local session files. The caller must create a new client afterwards.
pub async fn run(client: TelyzerClient, paths: &Paths) -> Result<()> {
    if !client.is_authorized().await? {
        println!("Not logged in.");
        client.shutdown().await;
        return Ok(());
    }

    println!("Logging out...");
    let sign_out = client.sign_out().await;

    // The connection and SQLite must be fully closed before deleting files
    client.shutdown().await;

    sign_out.context("Telegram sign-out failed; local session was kept")?;
    paths
        .remove_session_files()
        .context("Could not delete the local session files")?;

    println!("Logged out successfully.");
    Ok(())
}
