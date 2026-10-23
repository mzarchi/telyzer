use anyhow::Result;
use dialoguer::{theme::ColorfulTheme, Select};
use telyzer_core::{Paths, TelyzerClient};

use crate::commands;

enum MenuAction {
    Login,
    AccountInfo,
    Contacts,
    Channels,
    Groups,
    Bots,
    Logout,
    Exit,
}

pub async fn run(paths: &Paths) -> Result<()> {
    loop {
        let is_auth = {
            let client = TelyzerClient::new(paths).await?;
            let auth = client.is_authorized().await?;

            if auth {
                if let Ok(me) = client.get_me().await {
                    let name = me.first_name().unwrap_or("User");
                    let v = env!("CARGO_PKG_VERSION");
                    let display_v = v.split('+').nth(1).unwrap_or(v);
                    println!("Telyzer (CLI) v{}", display_v);
                    println!("Hey {}!", name);
                }
            } else {
                let v = env!("CARGO_PKG_VERSION");
                let display_v = v.split('+').nth(1).unwrap_or(v);
                println!("Telyzer (CLI) v{}", display_v);
                println!("Status: Not logged in");
            }
            auth
        };

        let mut actions = Vec::new();

        if is_auth {
            actions.push((MenuAction::AccountInfo, "My Account Info"));
            actions.push((MenuAction::Contacts, "Contacts"));
            actions.push((MenuAction::Channels, "Channels"));
            actions.push((MenuAction::Groups, "Groups"));
            actions.push((MenuAction::Bots, "Bots"));
            actions.push((MenuAction::Logout, "Logout"));
            actions.push((MenuAction::Exit, "Exit app"));
        } else {
            actions.push((MenuAction::Login, "Login"));
            actions.push((MenuAction::AccountInfo, "My Account Info"));
            actions.push((MenuAction::Exit, "Exit app"));
        }

        let items: Vec<&str> = actions.iter().map(|(_, label)| *label).collect();

        let theme = ColorfulTheme {
            prompt_prefix: dialoguer::console::style(String::new()),
            active_item_prefix: dialoguer::console::style(String::from("    ❯")),
            inactive_item_prefix: dialoguer::console::style(String::from("     ")),
            ..ColorfulTheme::default()
        };

        let selection = Select::with_theme(&theme)
            .with_prompt("    Choose an action")
            .items(&items)
            .default(0)
            .interact()?;

        match actions[selection].0 {
            MenuAction::Login => {
                if let Err(e) = commands::login::run(paths).await {
                    eprintln!("Error: {e}");
                }
            }
            MenuAction::AccountInfo => {
                if let Err(e) = commands::whoami::run(paths).await {
                    eprintln!("Error: {e}");
                }
            }
            MenuAction::Contacts => {
                println!("Contacts list is not implemented yet.");
            }
            MenuAction::Channels => {
                println!("Channels list is not implemented yet.");
            }
            MenuAction::Groups => {
                println!("Groups list is not implemented yet.");
            }
            MenuAction::Bots => {
                println!("Bots list is not implemented yet.");
            }
            MenuAction::Logout => {
                if let Err(e) = commands::logout::run(paths).await {
                    eprintln!("Error: {e}");
                }
            }
            MenuAction::Exit => {
                println!("Exiting app...");
                break;
            }
        }

        println!();
        println!("Press Enter to continue...");
        let mut input = String::new();
        std::io::stdin().read_line(&mut input)?;
    }

    Ok(())
}
