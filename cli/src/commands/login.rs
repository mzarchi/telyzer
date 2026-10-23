use anyhow::{Context, Result};
use dialoguer::{Input, Password};
use telyzer_core::{Paths, SignInResult, TelyzerClient};

pub async fn run(paths: &Paths) -> Result<()> {
    let client = TelyzerClient::new(paths).await?;

    if client.is_authorized().await? {
        println!("You are already logged in. Use 'Who am I' to see your info.");
        return Ok(());
    }

    let phone: String = Input::new()
        .with_prompt("Phone number (e.g. +989121234567)")
        .interact_text()?;

    println!("Requesting login code...");
    let token = client
        .request_login_code(&phone)
        .await
        .context("Failed to request login code")?;
    println!("Code sent. Check your Telegram app.");

    let password_token = loop {
        let code: String = Input::new().with_prompt("Enter code").interact_text()?;

        match client.sign_in(&token, &code).await? {
            SignInResult::Success(user) => {
                println!(
                    "Logged in as: {} (id: {})",
                    user.first_name().unwrap_or("user"),
                    user.id()
                );
                return Ok(());
            }
            SignInResult::NeedPassword(pt) => {
                println!("Two-factor authentication required.");
                break pt;
            }
        }
    };

    let password: String = Password::new().with_prompt("Password").interact()?;

    let user = client.sign_in_password(password_token, &password).await?;
    println!(
        "Logged in as: {} (id: {})",
        user.first_name().unwrap_or("user"),
        user.id()
    );

    Ok(())
}
