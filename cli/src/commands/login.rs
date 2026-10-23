use anyhow::{bail, Context, Result};
use dialoguer::{Input, Password};
use telyzer_core::{validate_phone, SignInResult, TelyzerClient};

const MAX_CODE_ATTEMPTS: u32 = 3;

pub async fn run(client: &TelyzerClient) -> Result<()> {
    if client.is_authorized().await? {
        println!("You are already logged in. Use 'whoami' to see your info.");
        return Ok(());
    }

    let phone = loop {
        let raw: String = Input::new()
            .with_prompt("Phone number (e.g. +989121234567)")
            .interact_text()?;

        match validate_phone(&raw) {
            Ok(phone) => break phone,
            Err(e) => eprintln!("{e}"),
        }
    };

    println!("Requesting login code...");
    let token = client
        .request_login_code(&phone)
        .await
        .context("Failed to request login code")?;
    println!("Code sent. Check your Telegram app.");

    let mut attempts = 0;
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
            SignInResult::InvalidCode => {
                attempts += 1;
                if attempts >= MAX_CODE_ATTEMPTS {
                    bail!("Too many invalid codes. Please start the login again.");
                }
                eprintln!("Invalid code, try again ({attempts}/{MAX_CODE_ATTEMPTS}).");
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
